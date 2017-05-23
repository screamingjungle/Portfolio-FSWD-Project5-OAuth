from flask import render_template, request, redirect, url_for, flash, session

from shopfront import app
from shopfront.db.database_setup import Collection

from shopfront.handlers.decorators import user_logged_in, owner_check, collection_exists
from shopfront.handlers.functions import userGet, itemGet, collectionGet, collectionSet, collectionDelete, slugify, processFormFields


@app.route('/collection/<int:collection_id>/item/')
@app.route('/collection/<int:collection_id>/')
@collection_exists
def showCollection(collection_id, **kwargs):
    """
    Show all the items for the selected collection.

    For the creator of the collection, a button for editing and deleting
    the collection is rendered.
    For the creator of an item, a button for editing and deleting the
    corresponding item is rendered.
    """
    return render_template(
        'collection.html',
        items=itemGet(collection_id=collection_id, **kwargs),
        collection=collectionGet(collection_id, **kwargs),
        listview=request.args.get('listview'),
        params=dict())


@app.route('/collection/')
def showCollections(**kwargs):
    """
    Show all the collections.
    """
    creator = []
    if 'user_id' in kwargs:
        creator = userGet(kwargs['user_id'])
    return render_template(
        'collections.html',
        creator=creator,
        collections=collectionGet(**kwargs)
    )


@app.route('/collection/new/', methods=['GET', 'POST'])
@user_logged_in
@owner_check
def addCollection(**kwargs):
    """
    Allows the user to creat a collection.
    """
    return editCollection(**kwargs)


@app.route('/collection/<int:collection_id>/edit/', methods=['GET', 'POST'])
@user_logged_in
@collection_exists
@owner_check
def editCollection(collection_id=None, **kwargs):
    """
    Allows the the creator of the collection to edit the title and description.

    The button for to do this is only visible on the items page for
    the creator of the collection.
    """
    if 'collection_id' in kwargs:
        collection_id = kwargs['collection_id']

    params = dict()
    has_error = False

    form_fields = [
        '*name',
        '*description'
    ]

    user_id = session['user_id']
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']

    if collection_id:
        collection = collectionGet(collection_id, **kwargs)
    else:
        collection = Collection()

    if request.method == 'POST':

        collection, params, has_error = processFormFields(
            form_fields, collection, params, has_error)

        if not has_error:
            if not collection_id:
                collection.seo_url=slugify(collection.name)
                collection.user_id=user_id

            coll = collectionSet(collection)

            if not collection_id:
                collection_id = next(iter(coll))

            if coll[collection_id]:
                flash('Collection Successfully Edited')
                print("updated collection = %s" % coll[collection_id])
                return redirect(url_for('showCollection', collection_id=collection_id))
            else:
                flash('Collection Update Failed!')
                params['error_submit'] = "Unable to update collection"
                has_error = True

    return render_template(
        'edit_collection.html',
        collection=collection,
        params=params)



@app.route('/collection/<int:collection_id>/delete/', methods=['GET', 'POST'])
@app.route('/collection/<int:collection_id>/delete/<option>', methods=['GET', 'POST'])
@user_logged_in
@collection_exists
@owner_check
def deleteCollection(collection_id, option=None):
    """
    Deletes the collection and all the items that belong to it from the database
    """
    user_id = session['user_id']
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']
    params = dict()

    if request.method == 'POST':
        if collectionDelete(collection_id, 'all' in request.form or option=='all'):
            flash('Collection Successfully Deleted')
            return redirect(url_for('showUserCollection', user_id=user_id))  # perhaps go to user collections screen
        else:
            params['error_submit'] = "Unable to delete collection"

    return render_template(
        'delete_collection.html',
        collection=collectionGet(collection_id),
        params=params) 