class Media:
    def __init__(
            self,
            concert_id=None,
            media_id=None,
            media_url=None,
            media_type=None,
            row=None):
        if row is not None:
            self.concert_id = row.get("concert_id")
            self.media_id = row.get("media_id")
            self.media_url = row.get("media_url")
            self.media_type = row.get("media_type", None)


def get_all_media_for_concert(cur, concert_id):
    """ Given a concert id, returns all media for that concert.

        Args:
            cur: database cursor
            artist_id: (required) artist id
            concert id: concert id
    """
    cur.execute("""
        select mc.media_id,
               m.media_url,
               mt.media_type
        from media_concert as mc
        left join media as m on mc.media_id = m.media_id
        left join media_types mt on mc.media_type_id = mt.media_type_id
        where mc.concert_id = %s""", (concert_id,))
    media = {'setlist': [], 'ticket': [], 'poster_flyer': [], 'live_shot': [], 'tour_itinerary': [], 'other': []}
    stored_media = cur.fetchall()
    for media_row in stored_media:
        m = Media(row=media_row)
        if m.media_type in media:
            media[m.media_type].append(m)
        else:
            media['other'].append(m)
    return media
