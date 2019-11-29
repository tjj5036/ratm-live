"""
Class intended to create a database connection and add it to
the request context.
"""
import os

import psycopg2
import psycopg2.extras

from flask import current_app, g


def get_db():
    """ Gets the database connection. Note that this uses environment
    variables to configure the connection. You should initialize these
    before launching the app.
    """
    if 'conn' not in g:
        conn = psycopg2.connect(
                user=os.environ.get("PGUSER"),
                password=os.environ.get("PGPASSWORD"),
                host="localhost",
                dbname=os.environ.get("PGDBNAME"),
                port=os.environ.get("PGPORT"))
        g.conn = conn
    return g.conn

def get_dict_cursor():
    """ Gets a dictionary cursor.
    """
    cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return cur


def close_db(e=None):
    """ Closes a database connection, if present.
    """
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()


def init_app(app):
    """ Initializes the current app with respect to the database.
    Namely, this registers the `get_db` and `close_db` methods.

    Args:
        app: the instance of the application
    """
    app.teardown_appcontext(close_db)
