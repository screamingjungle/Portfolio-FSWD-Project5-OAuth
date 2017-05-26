from flask import render_template
from sqlalchemy import asc

from shopfront import app
from shopfront.handlers.functions import itemGet
from shopfront.handlers.decorators import user_stats

@app.route('/')
@user_stats
def homepage(*args, **kwargs):
    """
    Show all collections. This is the home page.
    """
    return render_template('homepage.html',
        items=itemGet(limit=app.config['PAGE_LIMIT']),
        title='Latest Items',
        view_title='View item'
    )
