from flask import render_template, request, redirect, url_for, flash

from shopfront import app
from shopfront.handlers.functions import itemGet
from shopfront.handlers.item import showItems

@app.route('/tag/<tag>/item/')
@app.route('/tag/<tag>/')
def showTag(tag, **kwargs):
    """
    Show all the items for the selected tag.
    """
    return showItems(tag=tag, **kwargs)

@app.route('/tag/')
def showTags(**kwargs):
    """
    Show all the tags.
    """
    return showItems()

