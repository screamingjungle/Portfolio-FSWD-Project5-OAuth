from flask import send_from_directory

from shopfront import app
from shopfront.db.database_setup import ABSOLUTE_IMAGE_DIRECTORY

@app.route('/img/<filename>')
def serve_image(filename):
    """
    Serve an item image.
    """
    return send_from_directory(ABSOLUTE_IMAGE_DIRECTORY, filename)