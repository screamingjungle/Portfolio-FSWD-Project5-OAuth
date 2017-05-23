from flask import render_template, request, redirect, url_for, flash, session

from shopfront import app
from shopfront.db.database_setup import Category
from shopfront.handlers.decorators import user_logged_in, category_exists, owner_check
from shopfront.handlers.functions import userGet, itemGet, categoryGet, categorySet, categoryDelete, redirect_back, slugify, processFormFields


@app.route('/category/<int:category_id>/item/')
@app.route('/category/<int:category_id>/')
@app.route('/collection/<int:collection_id>/category/<int:category_id>/item/')
@app.route('/collection/<int:collection_id>/category/<int:category_id>/')
@category_exists
def showCategory(category_id, **kwargs):
    """
    Show all the items for the selected category.

    For the creator of the category, a button for editing and deleting
    the category is rendered.
    For the creator of an item, a button for editing and deleting the
    corresponding item is rendered.
    """
    return render_template(
        'category.html',
        items=itemGet(category_id=category_id, **kwargs),
        category=categoryGet(category_id, **kwargs),
        listview=request.args.get('listview'),
        params=dict())

@app.route('/category/')
def showCategories(**kwargs):
    """
    Show all the categories.
    """
    creator = []
    if 'user_id' in kwargs:
        creator = userGet(kwargs['user_id'])
    return render_template(
        'categories.html',
        creator=creator,
        categories=categoryGet(**kwargs)
    )

@app.route('/collection/<int:collection_id>/category/new/', methods=['GET', 'POST'])
@app.route('/category/new/', methods=['GET', 'POST'])
@user_logged_in
@owner_check
def addCategory(**kwargs):
    """
    Allows the user to creat a category.
    """
    return editCategory(**kwargs)

@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@app.route('/collection/<int:collection_id>/category/<int:category_id>/edit/',
    methods=['GET', 'POST'])
@user_logged_in
@category_exists
@owner_check
def editCategory(category_id=None, **kwargs):
    """
    Allows the the creator of the category to edit the title and description.

    The button for to do this is only visible on the items page for
    the creator of the category.
    """
    if 'category_id' in kwargs:
        category_id = kwargs['category_id']

    params = dict()
    has_error = False

    form_fields = [
        '*name',
        '*description'
    ]

    user_id = session['user_id']
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']

    if category_id:
        category = categoryGet(category_id, **kwargs)
    else:
        category = Category()

    if request.method == 'POST':

        category, params, has_error = processFormFields(
            form_fields, category, params, has_error)

        if not has_error:
            if not category_id:
                category.seo_url=slugify(category.name)
                category.user_id=user_id

            coll = categorySet(category)

            if not category_id:
                category_id = next(iter(coll))

            if coll[category_id]:
                flash('Category Successfully Edited')
                print("updated category = %s" % coll[category_id])
                return redirect(url_for('showCategory', category_id=category_id))
            else:
                flash('Category Update Failed!')
                params['error_submit'] = "Unable to update category"
                has_error = True

    return render_template(
        'edit_category.html',
        category=category,
        creator=category.usr,
        params=params)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@user_logged_in
@category_exists
@owner_check
def deleteCategory(category_id, **kwargs):
    """
    Deletes the category and all the items that belong to it from the database
    """
    user_id = session['user_id']
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']
    params = dict()

    if request.method == 'POST':
        if categoryDelete(category_id):
            flash('Category Successfully Deleted')
            return redirect(url_for('showUserCategory', user_id=user_id))
        else:
            params['error_submit'] = "Unable to delete category"

    return render_template(
        'delete_category.html',
        category=categoryGet(category_id),
        params=params) 