from flask import render_template, request, redirect, url_for, flash, session

from shopfront import app
from shopfront.handlers.decorators import user_logged_in, user_stats
from shopfront.handlers.functions import userGet

@app.route('/message/')
@user_logged_in
@user_stats
def showMessages(*args, **kwargs):
    """
    Show the user messages.

    TODO: unfinished
    """
    user_id = session['user_id']
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']

    messages = {}
    if 'messages' in kwargs:
        messages = kwargs['messages']

    return render_template(
        'messages.html',
        messages=messages)
