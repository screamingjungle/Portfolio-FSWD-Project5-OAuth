import re

from flask import render_template, request, redirect, url_for, flash, session, jsonify

from shopfront import app
from shopfront.db.database_setup import Item

from shopfront.handlers.decorators import user_logged_in, item_exists, owner_check, collection_exists, category_exists
from shopfront.handlers.functions import userGet, itemGet, isAdmin, itemSet, itemDelete, categoryGet, clean_tags, slugify, collectionGet, processFormFields

@app.route('/item/<int:item_id>/')
@app.route('/category/<int:category_id>/item/<int:item_id>/')
@app.route('/collection/<int:collection_id>/item/<int:item_id>/')
@app.route('/collection/<int:collection_id>/category/<int:category_id>/item/<int:item_id>/')
@item_exists
def showItem(item_id, **kwargs):
    """
    Renders the page for a single item.

    Buttons for editing and deleting the item are also rendered for the
    item creator
    """
    return render_template(
        'item.html',
        item=itemGet(item_id, **kwargs),
        listview=request.args.get('listview'),
        params=dict()
    )


@app.route('/item/')
def showItems(**kwargs):
    """
    Show all the items.
    """
    creator = []
    if 'user_id' in kwargs:
        creator = userGet(kwargs['user_id'])

    items = itemGet(**kwargs)
    if 'json' in kwargs:
        return jsonify(Items=[i.serialize for i in items])

    return render_template(
        'items.html',
        items=items,
        listview=request.args.get('listview'),
        creator=creator,
        params=dict()
    )

@app.route(
    '/item/new',
    methods=['GET', 'POST'])
@app.route(
    '/collection/<int:collection_id>/new',
    methods=['GET', 'POST'])
@app.route(
    '/category/<int:category_id>/new',
    methods=['GET', 'POST'])
@app.route(
    '/collection/<int:collection_id>/category/<int:category_id>/new',
    methods=['GET', 'POST'])
@user_logged_in
@owner_check
def addItem(**kwargs):
    """
    Allows the creator to add an item to the database
    """
    return editItem(**kwargs)


@app.route(
    '/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
@app.route(
    '/collection/<int:collection_id>/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
@app.route(
    '/collection/<int:collection_id>/category/<int:category_id>/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
@user_logged_in
@item_exists
@owner_check
def editItem(item_id=None, **kwargs):
    """
    Allows the creator of an item to update it from the database
    """
    if 'item_id' in kwargs:
        item_id = kwargs['item_id']

    params = dict()
    has_error = False

    form_fields = [
        '*name',
        '*description',
        'meta_description',
        'price',
        '*tags',
        'category_id',
        'collection_id'
    ]

    user_id = session['user_id']
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']

    if item_id:
        item = itemGet(item_id, **kwargs)
    else:
        item = Item()

    if request.method == 'POST':

        item, params, has_error = processFormFields(
            form_fields, item, params, has_error)

        if not has_error:
            if not item_id:
                item.seo_url=slugify(item.name)
                item.user_id=user_id

            coll = itemSet(item)

            if not item_id:
                item_id = next(iter(coll))

            if coll[item_id]:
                flash('Item Successfully Edited')
                print("updated item = %s" % coll[item_id])
                return redirect(url_for('showItem', item_id=item_id))
            else:
                flash('Item Update Failed!')
                params['error_submit'] = "Unable to update item"
                has_error = True

    return render_template(
        'edit_item.html',
        item=item,
        collections=collectionGet(user_id=user_id),
        categories=categoryGet(user_id=user_id),
        params=params)


@app.route(
    '/item/<int:item_id>/delete',
    methods=['GET', 'POST'])
@app.route(
    '/collection/<int:collection_id>/item/<int:item_id>/delete',
    methods=['GET', 'POST'])
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/delete',
    methods=['GET', 'POST'])
@app.route(
    '/collection/<int:collection_id>/category/<int:category_id>/item/<int:item_id>/delete',
    methods=['GET', 'POST'])
@user_logged_in
@item_exists
@owner_check
def deleteItem(item_id, **kwargs):
    """
    Deletes the selected item from the database
    """
    if request.method == 'POST':
        if itemDelete(item_id, **kwargs):
            flash('Item Successfully Deleted')
            return redirect(url_for('homepage', item_id=item_id))
            # TODO: this should be collection or somewhere else
        else:
            flash('Item NOT Deleted')
            item=itemGet(item_id, **kwargs)
            params = dict()
            params['error_deletion'] = "Unable to delete item"
            return render_template(
                'item.html',
                item=item,
                creator = userGet(item.user_id),
                params=params)
    else:
        return render_template(
            'delete_item.html',
            item=itemGet(item_id, **kwargs))

