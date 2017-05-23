import re
import string
from unicodedata import normalize

from shopfront import app
from shopfront.db.database_setup import User, Item, Category, Collection
from shopfront.db.database_connect import connect_to_database, ilike_needle

from flask import abort, session, request, url_for
from sqlalchemy import desc, or_
from sqlalchemy.orm import subqueryload
from sqlalchemy.sql import func, case, literal_column

# return updated object with param_errors
def processFormFields(form_fields,item,params,has_error=False):
    for field in form_fields:
        if field.startswith( '*' ): # required
            field = re.sub('\*', '', field)
            if not field in request.form:
                params['error_%s' % field] = "too empty is %s" % field
                setattr(item, field, '')
                has_error = True
                continue

            # ensure there is enough content in required fields
            if len(request.form[field]) < app.config['MIN_FIELD_LENGTH']:
                params['error_%s' % field] = "too short is %s" % field
                setattr(item, field, request.form[field])
                has_error = True
                continue

        if field in request.form:
            print "%s = %s" % (field, request.form[field])
            if field == "tags":
                setattr(item, field, clean_tags(request.form[field]))
            else:
                setattr(item, field, request.form[field])
    return item, params, has_error


def userCreate(login_session):
    """
    Add a new user to the database

    Set group to 'standard' - 'readonly' only set when user is being bad
    """
    try:
        name = login_session['username'] if 'username' in login_session else None
        email = login_session['email'] if 'email' in login_session else None
        picture = login_session['picture'] if 'picture' in login_session else None
        provider = login_session['provider'] if 'provider' in login_session else None

        if name and email:
            user = User(
                name=name,
                email=email,
                picture=picture,
                group='standard',
                provider=provider
            )

            db_session = connect_to_database()
            db_session.add(user)
            db_session.flush()
            ret = {user.id: user.name}

            db_session.commit()
            db_session.close()
            return ret

        return False
    except:
        return False


def userGet(user_id):
    """
    Get all user information for the given ID
    """
    try:
        db_session = connect_to_database()
        user = db_session.query(User).filter_by(id=user_id).first()
        db_session.close()
        return user
    except:
        return None


def userIdGet(email):
    """
    Get the User ID for the given email if it exists
    """
    try:
        db_session = connect_to_database()
        user = db_session.query(User).filter_by(email=email).first()
        db_session.close()
        return user.id
    except:
        return None

def userGroupGet(user_id):
    """
    Get the User Group for the given user id
    """
    try:
        return userGet(session['user_id']).group
    except:
        return None


def isLoggedIn():
    """
    Returns True if logged in
    """
    return 'user_id' in session

def redirect_back(default='homepage'):
    if request.referrer:
        referrer =  re.sub(r'/\d(/delete|\d/edit|new)/$', '', request.referrer)
        print("referrer = %s" % referrer)
    return request.args.get('next') or \
           referrer or \
           url_for(default)

def canInsertItem(**kwargs):
    ret = False
    if session['group'] == 'admin' or session['group'] == 'standard':
        ret = True
        if 'collection_id' in kwargs: # needs TESTING
            if not session['user_id'] == collectionGet(kwargs['collection_id']).usr.id:
                ret = False
        if 'category_id' in kwargs: # needs TESTING
            if not session['user_id'] == categoryGet(kwargs['category_id']).usr.id:
                ret = False
    return ret

def isAdmin(**kwargs):
    """
    Returns True if user_id is in Admin group or if owner of item
    """
    if 'group' in session:
        if session['group'] == 'admin':
            return True
    if 'item_id' in kwargs:
        if session['user_id'] == itemGet(kwargs['item_id']).user_id:
            return True
    if 'collection_id' in kwargs:
        if session['user_id'] == collectionGet(kwargs['collection_id']).usr.id:
            return True
    if 'category_id' in kwargs:
        if session['user_id'] == categoryGet(kwargs['category_id']).usr.id:
            return True
    if 'user_id' in kwargs:
        if session['user_id'] == userGet(kwargs['user_id']).id:
            return True
    return False

def userItemCount(**kwargs):

    user_id = session['user_id']
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']

    db_session = connect_to_database()
    item = db_session.query(
        func.count(Item.id).label("total_items"),
        func.count(
            case([((Item.category_id == None), Item.id)], else_=literal_column("NULL")))
            .label('uncat_items'),
        func.count(
            case([((Item.collection_id == None), Item.id)], else_=literal_column("NULL")))
            .label('uncol_items')
    )
    if 'category_id' in kwargs:
        item = item.filter_by(category_id=kwargs['category_id'])
    if 'collection_id' in kwargs:
        item = item.filter_by(collection_id=kwargs['collection_id'])
    if user_id:
        item = item.filter_by(user_id=user_id)
    if 'tag' in kwargs:
        item = item.filter(Item.tags.ilike( ilike_needle(kwargs['tag']) ))

    res = item.first()._asdict()

    #mysum = item.with_entities(func.count(Item.quantity)).scalar()
    #print("mysum = %s" % mysum)

    db_session.close()
    return res

def itemSearch(search_term, **kwargs):
    """
    Returns False if no items are found.
    Sorted by Updated Date descending

    Set the sort field by setting 'order_field' to:
    - created
    - name
    - price
    - updated
    - quantity
    order_type: asc or desc (default)
    """
    if not search_term:
        return False

    try:
        print("search = %s" % search_term)

        search_term = ilike_needle(search_term)

        order_field = 'created'
        if 'order_field' in kwargs:
            fields = [
                'created',
                'name',
                'price'
                'updated',
                'quantity'
            ]
            if kwargs['order_field'] in fields:
                order_field = kwargs['order_field']

        order_type = 'desc'
        if 'order_type' in kwargs:
            if kwargs['order_type'] == 'asc':
                order_type = 'asc'

        db_session = connect_to_database()
        item = db_session.query(Item)
        # eager load as db_session is closed before template requires it
        # (without it lazy loading in template fails)
        item = item.options(subqueryload(Item.usr))
        item = item.options(subqueryload(Item.cat))
        item = item.options(subqueryload(Item.coll))
        if 'category_id' in kwargs:
            item = item.filter_by(category_id=kwargs['category_id'])
        if 'collection_id' in kwargs:
            item = item.filter_by(collection_id=kwargs['collection_id'])
        if 'user_id' in kwargs:
            item = item.filter_by(user_id=kwargs['user_id'])
        if 'tag' in kwargs:
            item = item.filter(Item.tags.ilike( ilike_needle(kwargs['tag']) ))

        #item = item.filter(Item.name.like('%' + searchForm.courseName.data + '%'))
        item = item.filter(or_(
            Item.name.like(search_term),
            Item.tags.like(search_term),
        ))

        if order_type == 'asc':
            item = item.order_by(order_field)
        else:
            item = item.order_by(desc(order_field))

        if 'limit' in kwargs:
            item = item.limit(int(kwargs['limit']))
        else:
            item = item.limit(int(app.config['PAGE_LIMIT']))

        res = item.all()

        db_session.close()
        return res
    except:
        return False


def itemGet(item_id=None, **kwargs):
    """
    Returns False if no items are found.
    Sorted by Updated Date descending

    TODO: sort via kwargs
    - created
    - name
    - price
    - quantity
    """
    try:
        if 'item_id' in kwargs:
            item_id = kwargs['item_id']

        db_session = connect_to_database()
        item = db_session.query(Item)
        # eager load as db_session is closed before template requires it
        # (without it lazy loading in template fails)
        item = item.options(subqueryload(Item.usr))
        item = item.options(subqueryload(Item.cat))
        item = item.options(subqueryload(Item.coll))
        if 'category_id' in kwargs:
            item = item.filter_by(category_id=kwargs['category_id'])
        if 'collection_id' in kwargs:
            item = item.filter_by(collection_id=kwargs['collection_id'])
        if 'user_id' in kwargs:
            item = item.filter_by(user_id=kwargs['user_id'])
        if 'tag' in kwargs:
            item = item.filter(Item.tags.ilike( ilike_needle(kwargs['tag']) ))

        if item_id:
            item = item.filter_by(id=item_id)
            res = item.first()
        else:
            item = item.order_by(desc(Item.updated))
            if 'limit' in kwargs:
                item = item.limit(int(kwargs['limit']))
            #else:
            #  item = item.limit(int(app.config['PAGE_LIMIT']))
            res = item.all()

            #mysum = item.with_entities(func.count(Item.quantity)).scalar()
            #print("mysum = %s" % mysum)

        db_session.close()
        return res
    except:
        return False

def itemSet(item):
    """
    Returns False is Item was not updated.
    """
    try:
        db_session = connect_to_database()
        db_session.add(item)
        db_session.flush()
        ret = {item.id: item.name}

        db_session.commit()
        db_session.close()
        return ret
    except:
        return False

def itemDelete(item_id, **kwargs):
    """
    Returns False is Item was not deleted.
    """
    try:
        print "item_id = %s" % item_id

        item = itemGet(item_id, **kwargs)
        ret = {item.id: item.name}

        db_session = connect_to_database()
        db_session.delete(item)
        db_session.flush()

        db_session.commit()
        db_session.close()
        return ret
    except:
        return False

def categoryGet(category_id=None, **kwargs):
    """
    Returns the requested Category object or aborts if it doesn't exist.
    Sorted by name (A to Z)
    """
    try:
        db_session = connect_to_database()
        category = db_session.query(Category)
        category = category.options(subqueryload(Category.usr))
        if 'user_id' in kwargs:
            category = category.filter_by(user_id=kwargs['user_id'])
        if category_id:
            category = category.filter_by(id=category_id)
            res = category.first()
        else:
            category = category.order_by(Category.name)
            if 'limit' in kwargs:
                category = category.limit(int(kwargs['limit']))
            res = category.all()
        db_session.close()
        return res
    except:
        abort(404)
        # should this be False?

def categorySet(category):
    """
    Returns False is Category was not updated.
    """
    try:
        db_session = connect_to_database()
        db_session.add(category)
        db_session.flush()
        ret = {category.id: category.name}

        db_session.commit()
        db_session.close()
        return ret
    except:
        return False

def categoryDelete(category_id):
    """
    Returns False is category was not deleted.
    """
    try:
        db_session = connect_to_database()
        category = db_session.query(Category)
        category = category.filter_by(id=category_id)
        category.delete()
        db_session.commit()
        db_session.close()
        return True
    except:
        return False


def collectionGet(collection_id=None, **kwargs):
    """
    Returns the requested Collection object or aborts if it doesn't exist.

    TODO: sort by:
    - creation date
    """
    try:
        db_session = connect_to_database()
        collection = db_session.query(Collection)
        collection = collection.options(subqueryload(Collection.usr))
        if 'user_id' in kwargs:
            collection = collection.filter_by(user_id=kwargs['user_id'])
        if collection_id:
            collection = collection.filter_by(id=collection_id)
            res = collection.first()
        else:
            collection = collection.order_by(Collection.name)
            if 'limit' in kwargs:
                collection = collection.limit(int(kwargs['limit']))
            res = collection.all()
        db_session.close()
        return res
    except:
        abort(404)
        # should this be False?

def collectionSet(collection):
    """
    Returns False is Collection was not updated.
    """
    try:
        db_session = connect_to_database()
        db_session.add(collection)
        db_session.flush()
        ret = {collection.id: collection.name}

        db_session.commit()
        db_session.close()
        return ret
    except:
        return False

def collectionDelete(collection_id, delete_items=False):
    """
    Returns False is collection was not deleted.

    TODO: option to delete all collection.items thatare not linked elsewhere
    """
    try:
        db_session = connect_to_database()

        item = db_session.query(Item)
        item = item.filter_by(collection_id=collection_id)
        if delete_items or collection_id==1:
            item.delete()
        else: # set item collection_id to orphaned collection id
            item = item.update(dict(collection_id=1))
        db_session.commit()

        if collection_id > 1:
            collection = db_session.query(Collection)
            collection = collection.filter_by(id=collection_id)
            collection.delete()
            db_session.commit()

        db_session.close()
        return True
    except:
        return False

def userGet(user_id=None):
    """
    Returns the requested user object or aborts if it doesn't exist.
    """
    try:
        db_session = connect_to_database()
        user = db_session.query(User)
        if user_id:
          user = user.filter_by(id=user_id)
          res = user.first()
        else:
          user = user.order_by(desc(User.id))
          res = user.all()
        db_session.close()
        return res
    except:
        abort(404)
        # should this be False?

def userSet(user):
    """
    Returns False is user was not updated.
    """
    try:
        db_session = connect_to_database()
        db_session.add(user)
        db_session.flush()
        ret = {user.id: user.name}

        db_session.commit()
        db_session.close()
        return ret
    except:
        return False

def userDelete(user_id):
    """
    Returns False is user was not deleted.

    TODO: delete all collections and user.items and any stagnant categories
    """
    try:
        db_session = connect_to_database()
        user = db_session.query(User)
        user = user.filter_by(id=user_id)
        name = user.name
        user.delete()
        db_session.commit()
        db_session.close()
        return name
    except:
        return False


# Clears the user session context.
def reset_session():

    session.clear()
    '''
    if session['provider'] == 'google':
        del session['credentials']
        del session['gplus_id']
    elif session['provider'] == 'facebook':
        del session['facebook_id']

    del session['username']
    del session['email']
    del session['picture']
    del session['user_id']
    del session['group']
    del session['provider']
    del session['messages']

    del session['state']
    #del session['csrf_token']
    '''


def clean_tags(kw_str=None, return_list=False):
    # returns a List or string
    if kw_str:
        l = re.split(r'[\n.()!,; ""/]', kw_str)
        res = [x for x in l if len(x) > 0]

        if return_list:
            return res

        return ",".join(res)

    if return_list:
        return []

    #tags = self.clean_tags(self.request.get("tags"))
    #q.filter("tags", self.clean_tags(tag, True))

def slugify(text):
    punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    delim = u'-'
    result = []
    for word in punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


