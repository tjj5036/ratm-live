class Media:
    def __init__(
            self,
            concert_id=None,
            media_id=None,
            media_url=None,
            row=None):
        if row is not None:
            self.concert_id = row.get("concert_id")
            self.media_id = row.get("media_id")
            self.media_url = row.get("media_url")


def get_all_media_for_concert(cur, concert_id):
    """ Given a concert id, returns all media for that concert.

        Args:
            cur: database cursor
            artist_id: (required) artist id
            concert id: concert id
    """
    cur.execute("""
        select m.media_id,
               m.media_url
        from media_concert as mc
        join media as m on mc.media_id = mc.media_id
        and mc.concert_id = %s""", (concert_id,))
    media = []
    stored_media = cur.fetchall()
    for media_row in stored_media:
        res.append(Media(row=media_row))
    return media
