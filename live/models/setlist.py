from live.models.song import (
    Song
)

class SetlistSong:
    """ Helper class used within #Setlist.
    """

    def __init__(self, song_order, song):
        """ Initializes a class used to hold songs in a setlist.

        Args:
            song_order: the order of a song in a setlist
            song: a Song object, holds detailed information about a song.
        """
        self.song_order = song_order;
        self.song = song


class Setlist:
    """ Class that encapsulates information about a setlist.
    A setlist is basically a list of songs in an ordered form. Setlists have
    versions, that is, for a given concert there might be multiple versions
    of a setlist depending on the edits. 
    """

    def __init__(self, concert_id=None, version=None, complete=False):
        """
        Args:
            concert_id: the id of the concert this setlist belongs to
            version: the version of this setlist. Concerts can have multiple
                     versions of a setlist if there are multiple edits - you
                     can time travel between them
            complete: whether this setlist is complete. This indicates that the
                      setlist is fully "known" - ie many setlists we only know
                      a song or two, so this would be false.
        """
        self.concert_id = concert_id
        self.version = version
        self.complete = complete
        self.setlist_songs = []

    def add_song_to_setlist(self, setlist_song):
        """ Adds a setlist song.

        Args:
            setlist_song: instance of Song
        """
        if not setlist_song:
            return
        self.setlist_songs.append(setlist_song)


def get_latest_setlist_for_concert(cur, artist_id, concert_id):
    """ Gets the latest setlist for a concert.

    Note: this uses two queries. I think we can use a nested query,
    but I don't really feel like investigating that RN...

    Args:
        cur: cursor to the database
        artist_id: id of the artist this concert belongs to
        concert_id: id of the concert to fetch the setlist for

    Returns:
        populated setlist, or None if no such setlist exists
    """
    cur.execute("""
        select latest_version,
               complete
        from concert_setlist
        where concert_id = %s
        order by latest_version desc
        limit 1;""", (concert_id,))
    version_info = cur.fetchone()
    if not version_info:
        return None

    latest_version = version_info.get("latest_version", 0)
    complete = version_info.get("complete", False)

    cur.execute("""
       select s.title,
              s.song_url,
              s.artist_id,
              a.short_name as artist_name,
              aa.artist_name as original_artist_name,
              cso.notes,
              cso.song_order
        from concert_setlist_ordering as cso
            full join songs as s on cso.song_id = s.song_id
            left join songs as ss on ss.song_id = s.original_song_id
            left join artists as a on s.artist_id = a.artist_id
            left join artists as aa on ss.artist_id = aa.artist_id
        where cso.concert_id = %s 
        and cso.version = %s
        order by cso.song_order
        """, (concert_id, latest_version))
    setlist = Setlist(
            concert_id=concert_id,
            version=latest_version,
            complete=complete)
    setlist_songs = cur.fetchall()
    for setlist_song in setlist_songs:
        song = Song(row=setlist_song)
        setlist.add_song_to_setlist(song)
    return setlist
