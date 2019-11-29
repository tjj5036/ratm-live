""" All artist related modeling functions.
"""

class Artist:
    """Class to encapsulate artist information.
    """
    def __init__(self,
                 artist_id=None,
                 artist_name=None,
                 artist_short_name=None,
                 row=None):
        """ Initializes an artist instance. If a row is provided, we use that.
        """
        if row is not None:
            self.artist_id = row.get('artist_id')
            self.artist_name = row.get('artist_name')
            self.artist_short_name = row.get('short_name')
        else:
            self.artist_id = artist_id
            self.artist_name = artist_name
            self.artist_short_name = artist_short_name


def get_artist_from_short_name(cur, artist_short_name):
    """ Returns an Artist object if the artist_short_name is present
    in the database.

    Args:
        cur: database cursor
        artist_short_name: the "short name" of an artist.

    Returns:
        Artist object
    """
    cur.execute("""
        SELECT artist_id, artist_name, short_name 
        FROM artists
        WHERE short_name = %s""", (artist_short_name,))
    res = cur.fetchone()
    if not res:
        return None
    artist = Artist(row=res)
    return artist
