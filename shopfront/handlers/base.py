from flask import request, redirect, url_for, flash, session

from shopfront import app
from shopfront.handlers.functions import collectionGet, categoryGet, itemGet, userItemCount, isLoggedIn


@app.context_processor
def inject_menu():
    """
    Makes lists available to layout template for
    purpose of building the navigation menu links.
    """
    if isLoggedIn():
        return dict(
            menu_collections=collectionGet(limit=5),
            menu_categories=categoryGet(limit=5),
            menu_items=itemGet(limit=5),
            messages=userItemCount()
        )
    return dict()

#@app.before_request
def csrf_protect():
    """
    Verifies that all POST requests have the correct anti-CSRF token. If the
    _csrf_token field is not present, or does not match the current session's
    token, the browser will be redirected to the home page.

    NOT IN USE as SeaSurf does this
    """
    if request.method == 'POST':
        post_token = request.args.get('_csrf_token')
        session_token = session.get('_csrf_token')

        if post_token is None or post_token != session_token:
            flash("Session expired")
            #return redirect(url_for('homepage'))
            



