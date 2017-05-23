from flask import render_template, redirect, url_for, flash, session
from functools import wraps

from shopfront import app
from shopfront.db.database_setup import Collection, Item, User
from shopfront.db.database_connect import connect_to_database
from shopfront.handlers.functions import userGet, itemGet, isAdmin, categoryGet, collectionGet, redirect_back, canInsertItem, userItemCount, isLoggedIn


def owner_check(function):
    """
    Checks if the person logged in is the admin (or is able to insert items)
    or the owner of the item, category, collection
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if canInsertItem(**kwargs):
            return function(**kwargs)

        flash('Sorry, but you do have authorisation to do this')
        return redirect(redirect_back())
    return wrapper


def user_owner_check(function):
    """
    Checks if the person logged in is the particular user
    """
    @wraps(function)
    def wrapper(user_id, **kwargs):
        if not isAdmin(user_id=user_id):
            flash('Sorry, but you are not this user')
            return redirect(url_for('homepage'))
        return function(user_id, **kwargs)
    return wrapper


def collection_owner_check(function):
    """
    Checks if the person logged in is the owner of the collection
    """
    @wraps(function)
    def wrapper(collection_id):
        collection = collectionGet(collection_id=collection_id)
        creator = userGet(collection.user_id)
        if creator.id != session['user_id']:
            flash('Sorry, but you did not create this collection')
            return redirect(url_for('showAll'))
        return function(collection_id)
    return wrapper

def category_owner_check(function):
    """
    Checks if the person logged in is the owner of the category
    """
    @wraps(function)
    def wrapper(category_id, **kwargs):
        if not isAdmin(category_id=category_id):
            flash('Sorry, but you did not create this category')
            return redirect(url_for('showCategory', category_id=category_id))
        return function(category_id, **kwargs)
    return wrapper


def item_owner_check(function):
    """
    Checks if the person logged in is the owner of a particular item
    """
    @wraps(function)
    def wrapper(item_id, **kwargs):
        if not isAdmin(item_id=item_id):
            flash('Sorry, but you did not create this item')
            return redirect(url_for('homepage'))
        return function(item_id, **kwargs)
    return wrapper


# Check if item exists
def item_exists(function):
    """
    Checks if the collection and the item exists.

    Also checks if the item belongs to the collection if they both exist
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'item_id' in kwargs:
            item = itemGet(**kwargs)
            if not item:
                flash('Oops, but that item does not exist')
                return redirect(url_for('homepage'))
        return function(*args, **kwargs)
    return wrapper


def user_logged_in(function):
    """
    Redirects to the login page if the user is not logged in
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not isLoggedIn():
            flash('You need to be logged in to do that!')
            return redirect(url_for('showLogin'))
        return function(*args, **kwargs)
    return wrapper


def collection_exists(function):
    """
    Checks if the collection exists and renders the home page if it does not
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'collection_id' in kwargs:
            collection = collectionGet(kwargs['collection_id'])
            if not collection:
                flash('Oops, but that collection does not exist')
                return redirect(url_for('homepage'))
        return function(*args, **kwargs)
    return wrapper


def category_exists(function):
    """
    Checks if the category exists and renders the home page if it does not
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'category_id' in kwargs:
            category = categoryGet(kwargs['category_id'])
            if not category:
                flash('Oops, but that category does not exist')
                return redirect(url_for('homepage'))
        return function(*args, **kwargs)
    return wrapper


def user_exists(function):
    """
    Checks if the user exists and renders the home page if it does not
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'user_id' in kwargs:
            user = userGet(kwargs['user_id'])
            if not user:
                flash('Oops, but that user does not exist')
                return redirect(url_for('homepage'))
        return function(*args, **kwargs)
    return wrapper


def admin_check(function):
    """
    Checks if the person logged in is an admin
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if isAdmin():
            return function(*args, **kwargs)

        flash('Sorry, but you are not an admin')
        return redirect(url_for('homepage'))
    return wrapper


def user_stats(function):
    """
    Gets messages for the logged in user.
    This may be item alerts (e.g. unlinked items to collection)

    These messages are injected into function kwargs
    Gets pinged on homepage and messages (to improve performance).
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if isLoggedIn():
            messages = userItemCount()
            session['messages'] = messages['total_items'] or 0
            return function(*args, messages=messages, **kwargs)
        return function(*args, **kwargs)
    return wrapper
