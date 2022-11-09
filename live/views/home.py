from flask import (
        Blueprint,
        current_app,
        render_template,
        request)

from live.database import get_dict_cursor
from live.models import (
        artist,
        concert,
        era,
        update)

blueprint = Blueprint('home', __name__)



@blueprint.route('/')
def home():
    """ Renders the home page.
    """
    cur = get_dict_cursor()
    primary_short_name = current_app.config.get(
        "PRIMARY_ARTIST_SHORT_NAME", "rage")
    artist_inst = artist.get_artist_from_short_name(cur, primary_short_name)

    eras = era.get_all_for_artist(cur, artist_inst)

    upcoming_concerts = []
    if artist_inst:
        upcoming_concerts = concert.get_upcoming_concerts(
                cur, artist_inst, limit=10)
    recent_updates = update.get_recent_updates(cur, limit=15)
    return render_template(
            "home.html",
            artist=artist_inst,
            concerts=upcoming_concerts,
            eras=eras,
            updates=recent_updates)


@blueprint.route('/update-archive')
def update_achive():
    """ Renders the update archive.
    """
    cur = get_dict_cursor()
    recent_updates = update.get_recent_updates(cur)
    return render_template(
            "update_archive.html",
            updates=recent_updates)


@blueprint.route('/most-wanted')
def most_wanted():
    """ Renders the most wanted list.
    """
    return render_template(
            "most_wanted.html")


@blueprint.route('/links')
def links():
    """ Renders the links page.
    """
    return render_template(
            "links.html")
