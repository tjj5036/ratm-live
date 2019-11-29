class Update:
    """ Class that encapsulates information about an update.
    """

    def __init__(
            self,
            update_date=None,
            concert_friendly_url=None,
			artist_short_name=None,
            blurb=None,
            row=None):
        """ Initializes a concert object. Either uses a database
        object (row) directly, or uses passed in values.

        Args:
            update_date: date of update
            concert id: concert id
            concert_friendly_url: a unique url that can be used to find a concert
                                  in conjunction with `artist_short_name`
            artist_short_name: short name of the artist.
            row: object encapsulating concert informatin specified directly
                 from the database. If specified, takes precedence.
        """
        if row:
            # Direct concert attributes
            self.update_date = row.get('update_date')
            self.concert_friendly_url = row.get('concert_friendly_url')
            self.artist_short_name = row.get('short_name')
            self.blurb = row.get('blurb')
        else:
            self.update_date = update_date
            self.concert_friendly_url = concert_friendly_url
            self.artist_short_name = artist_short_name
            self.blurb = blurb


def get_recent_updates(cur, limit=None):
    """ Gets recent updates
    Args:
        cur: a cursor to the database
        limit: how many updates we want to fetch. If none fetches all updates
    """
    limit_str = ''
    if limit is not None:
        try:
            limit_int = int(limit)
            limit_str = 'limit %s' % (limit_int)
        except ValueError as e:
            # Default to no limit
            pass
    cur.execute("""
	select
		u.update_date,
		c.concert_friendly_url,
		a.short_name,
		u.blurb
	from updates as u
	join concerts as c on u.concert_id = c.concert_id
	join artists as a on c.artist_id = a.artist_id
	order by u.update_date desc, c.concert_friendly_url
    %s""" % (limit_str))
    res = []
    updates = cur.fetchall()
    for update_row in updates:
        update = Update(row=update_row)
        res.append(update)
    return res
