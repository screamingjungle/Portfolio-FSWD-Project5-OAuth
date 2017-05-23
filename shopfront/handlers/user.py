import re
from flask import render_template, request, redirect, url_for, flash, session

from shopfront import app
from shopfront.db.database_setup import User
from shopfront.handlers.decorators import user_logged_in, user_exists, user_owner_check, admin_check, item_exists
from shopfront.handlers.functions import userGet, userSet, itemGet, processFormFields
from shopfront.handlers.item import showItems, showItem
from shopfront.handlers.category import showCategories, showCategory
from shopfront.handlers.collection import showCollections, showCollection

@app.route('/user/<int:user_id>/')
@user_logged_in
@user_exists
def showUser(user_id, **kwargs):
    """
    Show the user page with user specific management options.
    """
    return render_template(
        'user.html',
        items=itemGet(user_id=user_id, **kwargs),
        user=userGet(user_id, **kwargs))

@app.route('/user/<int:user_id>/item/')
@app.route('/user/<int:user_id>/item/<int:item_id>')
@user_exists
def showUserItem(user_id, item_id=None, **kwargs):
    """
    Show user's items.
    """
    if item_id:
        return showItem(user_id=user_id, item_id=item_id, **kwargs)
    return showItems(user_id=user_id, **kwargs)

@app.route('/user/<int:user_id>/category/')
@app.route('/user/<int:user_id>/category/<int:category_id>')
@user_exists
def showUserCategory(user_id, category_id=None, **kwargs):
    """
    Show the user categories.
    """
    if category_id:
        return showCategory(
            user_id=user_id, 
            category_id=category_id, 
            **kwargs)
    return showCategories(user_id=user_id, **kwargs)

@app.route('/user/<int:user_id>/collection/')
@app.route('/user/<int:user_id>/collection/<int:collection_id>')
@user_exists
def showUserCollection(user_id, collection_id=None, **kwargs):
    """
    Show the user collections.
    """
    if collection_id:
        return showCollection(
            user_id=user_id, 
            collection_id=collection_id, 
            **kwargs)
    return showCollections(user_id=user_id, **kwargs)

@app.route('/user/new', methods=['GET', 'POST'])
@admin_check
def addUser(**kwargs):
    """
    Allows the admin to add a user
    """
    return editUser(user_id=None, **kwargs)


@app.route('/user/<int:user_id>/edit',
    methods=['GET', 'POST'])
@user_logged_in
@user_exists
@user_owner_check
def editUser(user_id=None, **kwargs):
    """
    Allows the creator of an user to update it from the database
    """
    params = dict()
    has_error = False
    form_fields = [
        '*name',
        '*email',
        '*group',
        'picture',
    ]

    if 'user_id' in kwargs:
        user_id = kwargs['user_id']

    if user_id:
        user = userGet(user_id, **kwargs)
    else:
        user = User()

    if request.method == 'POST':
        user, params, has_error = processFormFields(
            form_fields, user, params, has_error)

        if not has_error:
            coll = userSet(user)
            if not user_id:
                user_id = next(iter(coll))

            if coll[user_id]:
                flash('User Successfully Edited')
                print("updated user = %s" % coll[user_id])
                return redirect(url_for('showUser', user_id=user_id))
            else:
                flash('User Update Failed!')
                params['error_submit'] = "Unable to update user"
                has_error = True

    return render_template(
        'edit_user.html',
        user=user,
        params=params)


@app.route('/user-management/', methods=['GET', 'POST'])
@admin_check
def user_management():
    """
    Admin access to edit User group and Disable access.
    """
    params = dict()
    has_error = False

    if request.method == 'POST':
        users = userGet()
        for user in users:
            if user.email in request.form:
                user.group = request.form[user.email]
                if user.group == 'disabled' and not user.group == 'admin':
                    user.enabled = False
                if not userSet(user):
                    has_error = True

        if not has_error:
            flash("User settings have been saved")
            return redirect(url_for('user_management'))
        else:
            flash("Unable to save user settings!")
            params['error_submit'] = "Unable to update user"

    return render_template('manage_users.html',
        params=params,
        users=userGet())

