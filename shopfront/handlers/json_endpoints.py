from shopfront import app

from shopfront.handlers.decorators import user_logged_in
from shopfront.handlers.item import showItems
from shopfront.handlers.search import searchResults
from shopfront.handlers.functions import isAdmin

@app.route('/catalog.json')
@app.route('/item/json')
@user_logged_in
def jsonItems(**kwargs):
    """
    Serve JSON with all or filtered items.
    """
    if not isAdmin() and not 'user_id' in kwargs:
        return showItems(json=True,user_id=session['user_id'],**kwargs)
    return showItems(json=True,**kwargs)

@app.route('/search_json/<query>')
def searchJson(query,**kwargs):
    """
    Search API to return results in JSON format.
    Used in menu search feature.
    """
    return searchResults(query=query, json=True, **kwargs)
