""" App module that contains the app factory function.
This is where the application actually gets created.
"""
import os
from flask import (
        Flask,
        render_template)

from live.database import (
    init_app
)
from live.views import (
        about,
        artists,
        concerts,
        contact,
        home,
        song)

STATIC_URI = "https://ratmlive.sfo2.digitaloceanspaces.com"


def create_app():
    app = Flask(__name__)
    init_app(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_config(app)
    register_static(app)
    return app


def register_blueprints(app):
    """ Registers blueprints, which are basically routing functions.
    """
    app.register_blueprint(about.blueprint)
    app.register_blueprint(artists.blueprint)
    app.register_blueprint(concerts.blueprint)
    app.register_blueprint(contact.blueprint)
    app.register_blueprint(home.blueprint)
    app.register_blueprint(song.blueprint)


def page_not_found(e):
    """ Function to handle 404s."""
    return render_template("404.html")


def register_error_handlers(app):
    """ Registers error handling functionality, namely 404s and
    the like.
    """
    app.register_error_handler(404, page_not_found)


def register_config(app):
    """ Registers any configuration key/value pairs.
    """
    app.config["PRIMARY_ARTIST_SHORT_NAME"] = "rage"


def register_static(app):
    """ Registers any static endpoints.
    """
    app.config["STATIC_URI"] = STATIC_URI
