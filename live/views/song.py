from flask import (
        abort,
        render_template,
        request,
        Blueprint)

from live.database import get_dict_cursor
from live.models import (
        artist,
        concert,
        song)

blueprint = Blueprint('song', __name__)


@blueprint.route('/artists/<artist_name>/songs/<song_url>')
def song_get_by_artist_name(artist_name, song_url):
    """ Gets song information by an artist and a song url.

    Args:
        artist_name: short name of the artist
        song_url: the unique identifier for that song
    """
    cur = get_dict_cursor()
    artist_inst = artist.get_artist_from_short_name(cur, artist_name)
    if not artist_inst:
        abort(404)

    song_inst = song.get_complete_song_info(cur, artist_inst, song_url)
    if not song_inst:
        abort(404)

    first_performance = None
    latest_performance = None
    if song_inst.concerts and len(song_inst.concerts) > 0:
        first_performance = song_inst.concerts[0]
        latest_performance = song_inst.concerts[-1]

    return render_template(
            "song.html",
            artist=artist_inst,
            concerts=song_inst.concerts,
            song=song_inst,
            first_performance=first_performance,
            latest_performance=latest_performance)



@blueprint.route('/artists/<artist_name>/songs')
def song_get_all_by_artist_name(artist_name):
    """ Gets all songs as well as a count of their performances by artist.

    Args:
        artist_name: short name of the artist
    """
    cur = get_dict_cursor()
    artist_inst = artist.get_artist_from_short_name(cur, artist_name)
    if not artist_inst:
        abort(404)

    songs = song.get_all_for_artist(cur, artist_inst)

    max_performance_count = 0
    if len(songs) > 0:
        max_performance_count = songs[0].concert_count

    return render_template(
            "song_list_for_artist.html",
            artist=artist_inst,
            songs=songs,
            max_performance_count=max_performance_count)
