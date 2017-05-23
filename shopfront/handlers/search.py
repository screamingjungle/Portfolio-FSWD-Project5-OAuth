from flask import render_template, request, redirect, url_for, flash, jsonify

from shopfront import app
from shopfront.handlers.functions import itemSearch

@app.route('/search/', methods=['GET', 'POST'])
@app.route('/search/<query>')
def search(query=None,**kwargs):
    """
    Redirect search form to search API.
    This prevents form resusmission on page reload.
    """
    if request.method == 'POST':
        if 'sterm' in request.form:
            return redirect(url_for('searchResults', query=request.form['sterm']))
    return redirect(url_for('searchResults', query=query))


@app.route('/search_json/<query>')
def searchJson(query,**kwargs):
    """
    Search API to return results in JSON format.
    Used in menu search feature.
    """
    return searchResults(query=query, json=True, **kwargs)


@app.route('/search_results/')
@app.route('/search_results/<query>')
def searchResults(query=None, **kwargs):
    """
    Show all the items for a search term.
    """
    items = []
    if query:
        items = itemSearch(query, **kwargs)

    creator = []
    if 'user_id' in kwargs:
        creator = userGet(kwargs['user_id'])

    if 'json' in kwargs:
        if items:
            return jsonify(items=[i.serializeJson for i in items])
        return '{}'

    return render_template(
        'search.html',
        items=items,
        listview=request.args.get('listview'),
        creator=creator,
        query=query,
        params=dict()
    )
