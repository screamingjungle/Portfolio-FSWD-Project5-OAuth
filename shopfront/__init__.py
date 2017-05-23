from flask import Flask
from flask_seasurf import SeaSurf

# Flask initialization
app = Flask(__name__)

# https://discussions.udacity.com/t/do-we-need-to-encrypt-the-state-when-implementing-csrf-protection/196609
csrf = SeaSurf(app)

import shopfront.handlers.base
import shopfront.handlers.images
import shopfront.handlers.homepage
import shopfront.handlers.item
import shopfront.handlers.category
import shopfront.handlers.collection
import shopfront.handlers.tag
import shopfront.handlers.search
import shopfront.handlers.user
import shopfront.handlers.message
import shopfront.handlers.login
import shopfront.handlers.oauth
