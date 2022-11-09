class Era:
    """ Class that encapsulates an "era" for a particular artist. An "era" is
    loosely defined as a significant set of shows for an artist that may include
    tours. As an example, the shows for Rage Against the Machine prior to their
    first tour w/ Suicidal Tendencies can be thought of as an era as they were not
    officially touring and were instead playing one-off shows.

    Args:
        artist_id: ID of the artist we're fetching the era for
        era_id: the ID of the era (primary key)
        era_tile: the path to an image that is used when rendering available
                  eras for a particular era
        era_identifier: the identifier (shortname) of a particular era
        row: if initialized from a database then the result of querying the era table
    """

    def __init__(
            self,
            artist_id=None,
            era_id=None,
            era_tile=None,
            era_identifier=None,
            row=None):
        if row:
            self.artist_id = row.get('artist_id', None)
            self.era_id = row.get('era_id', -1)
            self.era_tile = row.get('era_tile', None)
            self.era_identifier = row.get('era_identifier', None)
        else:
            self.artist_id = artist_id
            self.era_id = era_id
            self.era_tile = era_tile
            self.era_identifier = era_identifier

def get_for_artist_and_identifier(
        cur,
        artist_inst,
        era_identifier):
    """ Gets an era for an artist based on an era identifier.

    Args:
        cur: a cursor to the database
        artist_inst: an Artist instance
        era_identifier: an identifier for a particular era

    Returns: populated Era object if exists, None otherwise.
    """
    cur.execute("""
        select
            artist_id, era_id
        from eras e
        where e.artist_id=%s and e.era_identifier=%s
        limit 1""",
        (artist_inst.artist_id, era_identifier,))
    era_row = cur.fetchone()
    if not era_row:
        return None
    return Era(row=era_row)


def get_all_for_artist(
        cur,
        artist_inst):
    """ Gets all eras for a particular artist

    Args:
        cur: a cursor to the database
        artist_inst: an Artist instance

    Returns: list of populated Era objects
    """
    if not artist_inst:
        return []
    # TODO: the order by is a hack because I entered in
    # the DB entries in tour order so the ids are increasing.
    cur.execute("""
        select
            artist_id,
            era_id,
            era_identifier,
            era_tile
        from eras e
        where e.artist_id=%s
        order by era_id""", (artist_inst.artist_id,))
    era_rows = cur.fetchall()
    eras = []
    if era_rows:
        for era_row in era_rows:
            eras.append(Era(row=era_row))
    return eras

