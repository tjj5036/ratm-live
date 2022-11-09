from flask import (
        abort,
        Blueprint,
        current_app,
        render_template,
        request)

from live.database import get_dict_cursor
from live.models import (
        artist,
        concert,
        era)

blueprint = Blueprint('tours_and_eras', __name__)


@blueprint.route('/tours')
def tours():
    abort(404)


@blueprint.route('/eras/<artist_name>/eras/<era_identifier>')
def eras(artist_name, era_identifier):
    """ Gets eras for a particular artist."""
    cur = get_dict_cursor()
    artist_inst = artist.get_artist_from_short_name(cur, artist_name)
    if not artist_inst:
        abort(404)

    era_inst = era.get_for_artist_and_identifier(cur, artist_inst, era_identifier)
    if not era_inst:
        abort(404)
 
    concert_listings = concert.get_all_for_era(cur, artist_inst, era_inst)
    year_filters = set()
    return render_template(
            "concerts_get_by_artist.html",
            artist=artist_inst,
            concerts=concert_listings,
            year_filters=year_filters)
