from live.models import concert

class Song:
    """ Encapsulates all information given a song.
    """

    def __init__(
            self,
            artist_id=None,
            song_id=None,
            title=None,
            notes=None,
            lyrics=None,
            original_song_id=None,
            song_url=None,
            song_order=None,
            original_artist_name=None,
            concert_count=0,
            row=None):
        """
        Note: the lstrip at the bottom for the lyrics is due to the way I
        entered these into the database.

        Args:
            artist_id: the id of the artist that wrote the song
            song_id: a unique identifier for this song
            title: the human friendly title of the song (ex, "Bulls on Parade")
            notes: notes about this song. This could be a history of the song,
                   for example
            lyrics: the lyrics of the song
            original_song_id: the song id of another song if this song is a
                              cover. For instance, for Rage, this could be a
                              pointer to Bruce Springsteen's "The Ghost of Tom
                              Joad".
            song_url: the URL identifier that can be used to lookup this song
            concert_count: the count of how many concerts this song has been
                           performed at.
            row: the database representation of a song. If specified, none of
                 the other parameters are used - everything is taken from this.

        """
        if row:
            self.artist_id = row.get("artist_id")
            self.song_id = row.get("song_id")
            self.title = row.get("title")
            self.notes = row.get("notes")
            self.lyrics = row.get("lyrics")
            self.original_song_id = row.get("original_song_id")
            self.original_artist_name = row.get("original_artist_name")
            self.song_url = row.get("song_url")
            self.song_order = row.get("song_order")
        else:
            self.artist_id = artist_id
            self.song_id = song_id
            self.title = title
            self.notes = notes
            self.lyrics = lyrics
            self.original_song_id = original_song_id
            self.song_url = song_url
            self.song_order = song_order
            self.original_artist_name = original_artist_name

        if self.lyrics is not None:
            self.lyrics = self.lyrics.lstrip()

        self.concerts = []
        self.concert_count = concert_count

    def add_concerts(self, concerts):
        """ Adds concerts that this song was played at.

        Note: this also updates concert count.
        """
        if not concerts:
            return
        self.concerts = concerts
        self.concert_count = len(concerts)


def get_complete_song_info(cur, artist_inst, song_url):
    """ Gets complete information about a song given its human friendly
    url.

    Args:
        cur: database cursor
        artist_name: short name of the artist
        song_url: the unique identifier for that song

    Returns:
        instance of #Song if the song exists, song otherwise
    """
    cur.execute("""
         select s.title,
               s.lyrics,
               s.notes,
               s.original_song_id,
               s.artist_id,
               s.song_id,
               ss.artist_id as original_artist_id,
               a.artist_name as original_artist_name
        from songs as s
            left join songs as ss on ss.song_id = s.original_song_id
            left join artists as a on ss.artist_id = a.artist_id
        where s.artist_id = %s
              and s.song_url = %s
        limit 1;""",  (artist_inst.artist_id, song_url))
    song_info = cur.fetchone()
    if not song_info:
        return None

    song_inst = Song(row=song_info)
    concerts = concert.get_concerts_with_song(
            cur, artist_inst, song_inst.song_id)
    song_inst.add_concerts(concerts)
    return song_inst


def get_all_for_artist(cur, artist_inst):
    """ Gets all songs, as well as their performance counts, for an artist

    Note: this is potentially expensive, we can probably cache this.

    Args:
        cur: database cursor
        artist_name: short name of the artist

    Returns:
        list of songs sorted by performance count
    """
    if not artist_inst:
        return []
    return concert.get_count_of_concerts_for_all_songs(cur, artist_inst)
