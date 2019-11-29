import re

from flask import (
        abort,
        render_template,
        request,
        Blueprint)

from live.database import get_dict_cursor
from live.models import (
        artist,
        concert,
        media,
        recording)

blueprint = Blueprint('concerts', __name__)


@blueprint.route('/artists/<artist_name>/concerts')
def concerts_get_by_artist(artist_name):
    """ Gets all concerts for a given artist. Note that we optionally
    accept the following query parameters:

    - year: if year is specified, we filter dates to that year

    If the year is specified, we need to manually find all years active
    for an artist such that we can display them. Otherwise, if we are showing
    all concerts, we can re-use the result set and mine the year from that.

    Args:
        artist_name: the "short" artist name.
    """
    cur = get_dict_cursor()
    artist_inst = artist.get_artist_from_short_name(cur, artist_name)
    if not artist_inst:
        abort(404)

    generate_year_filters = True
    year = None
    year_param = request.args.get('year')
    year_filters = set()

    if year_param is not None:
        year_match = re.match(r'.*([1-3][0-9]{3})', year_param)
        if year_match is not None:
            year = year_match.group(1)
            year_filters = concert.get_years_of_concerts_for_artist(
                    cur, artist_inst)

    concert_listings = concert.get_all_for_artist_listing_only(
            cur,
            artist_inst,
            year=year)

    if generate_year_filters:
        for concert_listing in concert_listings:
            if concert_listing.date:
                concert_listing_year = concert_listing.date.year
                if concert_listing_year not in year_filters:
                    year_filters.add(concert_listing_year)


    return render_template(
            "concerts_get_by_artist.html",
            artist=artist_inst,
            concerts=concert_listings,
            year_filters=sorted(year_filters))


@blueprint.route('/artists/<artist_name>/concerts/<concert_friendly_url>')
def concerts_get_by_artist_and_concert_friendly_url(
        artist_name,
        concert_friendly_url):
    """ Gets a single concert as determined from the artist and the
    concert friendly url.

    Args:
        artist_name: the "short" artist name.
        concert_friendly_url: a unique identifier for this concert
    """
    cur = get_dict_cursor()
    artist_inst = artist.get_artist_from_short_name(cur, artist_name)
    if not artist_inst:
        abort(404)

    concert_inst = concert.get_for_artist_and_url(
            cur,
            artist_inst,
            concert_friendly_url)
    if not concert_inst:
        abort(404)

    # Maybe move this inside media
    stored_media = media.get_all_media_for_concert(
            cur, concert_inst.concert_id)

    recordings = recording.get_all_recordings_for_concert(
            cur, concert_inst.concert_id)

    return render_template(
            "concert.html",
            artist=artist_inst,
            concert=concert_inst,
            media=stored_media,
            recordings=recordings)
