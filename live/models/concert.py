from live.models.location import Location 
from live.models.setlist import get_latest_setlist_for_concert
from live.models.song import Song
from live.models.venue import Venue


class Concert:
    """ Class that encapsulates information about a concert.
    """

    def __init__(
            self,
            artist_id=None,
            concert_id=None,
            date=None,
            notes=None,
            concert_friendly_url=None,
            venue=None,
            location=None,
            setlist=None,
            has_setlist=False,
            has_recordings=False,
            has_media=False,
            row=None,
            concerts_before_after=None,
            tour=None):
        """ Initializes a concert object. Either uses a database
        object (row) directly, or uses passed in values.

        Args:
            artist_id: (required) artist id
            concert id: concert id
            setlist: initialized setlist object
            venue: initialized venue object
            notes: notes about the concert
            concert_friendly_url: a unique url that can be used to find this concert
            has_setlist: whether or not the setlist is known for the concert
            has_recordings: whether recordings exist for the concert
            has_media: whether media exists for the concert
            row: object encapsulating concert informatin specified directly
                 from the database. If specified, takes precedence. Note that
                 artist_id is still required
            concerts_before_after: list of concerts that came immediately before/after
                                   the current one.
            tour: a tour reference if part of a tour
        
        """
        self.artist_id = artist_id
        if row:
            # Direct concert attributes
            self.concert_id = row.get('concert_id')
            self.date = row.get('date')
            self.notes = row.get('notes')
            self.concert_friendly_url = row.get('concert_friendly_url')
            self.has_setlist = row.get('has_setlist', False)
            self.has_recordings = row.get('has_recordings', False)
            self.has_media = row.get('has_media', False)
            self.tour = row.get('tour_name', None)

        else:
            self.concert_id = concert_id
            self.setlist = setlist
            self.date = date
            self.notes = notes
            self.concert_friendly_url = concert_friendly_url
            self.has_setlist = has_setlist
            self.has_recordings = has_recordings
            self.has_media = has_media
            self.tour = tour

        # Information tied to concerts that is usually derived from
        # the same query (ie, fetching location information)
        self.venue = venue
        self.location = location

        # This is populated by a separate query
        self.setlist = setlist

        # Separate query
        self.concerts_before_after = concerts_before_after


def initialize_from_result(
        cur, 
        artist_inst,
        concert_row,
        fetch_setlist=False,
        fetch_before_prev_concert=False):
    """ Given a db result, initializes a fully populated concert,
    including venue and location information.

    Args:
        cur: a cursor to the database
        artist_inst: instance of an Artist object
        concert_row: a row from the database representing concert info
        fetch_setlist: if true, resolves the setlist for this concert.
        fetch_before_prev_concert: if true, gets the concert info before/after the given one
    """
    location = Location(
        concert_row["country_name"],
        concert_row["state_name"],
        concert_row["city_name"])

    venue = None
    if concert_row.get("venue_name") is not None:
        venue = Venue(concert_row["venue_name"], location)

    setlist = None
    if fetch_setlist:
        setlist = get_latest_setlist_for_concert(
                cur,
                artist_inst.artist_id,
                concert_row["concert_id"])

    concerts_before_after = []
    if fetch_before_prev_concert:
        # This is actually kind of gnarly. We have to do a rank
        # and then select the dates prior/before if present
        cur.execute("""
            with near_final as (
                with before_after as (
                    with concert_artist_dates as (
                        select cc.artist_id,
                               cc.date,
                               cc.concert_friendly_url,
                               row_number() over (ORDER BY cc.date asc) as rn
                        from concerts as cc 
                        where cc.artist_id=%s
                    )
                    select 
                        prev.date as prev_date,
                        prev.concert_friendly_url as prev_concert_friendly_url,
                        next.date as next_date,
                        next.concert_friendly_url as next_concert_friendly_url
                    from concert_artist_dates curr
                    left outer join concert_artist_dates next ON curr.rn+1=next.rn
                    right outer join concert_artist_dates prev ON curr.rn-1=prev.rn
                    where curr.artist_id=%s and curr.concert_friendly_url=%s 
                )
                select prev_concert_friendly_url as concert_friendly_url from before_after
                union all
                select next_concert_friendly_url as concert_friendly_url from before_after
            )
            select * from near_final""",
            (artist_inst.artist_id,
              artist_inst.artist_id,
              concert_row.get('concert_friendly_url')))
        concert_rows = cur.fetchall()
        if not concert_rows:
            concert_rows = []
        for cr in concert_rows:
            concerts_before_after.append(
                get_for_artist_and_url(
                  cur,
                  artist_inst,
                  cr.get('concert_friendly_url'),
                  fetch_setlist=False,
                  fetch_before_prev_concert=False))

    concert = Concert(
        artist_inst.artist_id,
        row=concert_row,
        setlist=setlist,
        venue=venue,
        location=location,
        concerts_before_after=concerts_before_after)
    return concert


def get_all_for_era(cur, artist_inst, era_inst):
    """ Gets all concerts for an artist and a particular era.

    Args:
        artist_inst: Artist instance
        era_inst: Era instance
    """
    if not artist_inst or not era_inst:
        return None
    cur.execute("""
        select c.date,
               c.concert_friendly_url,
               v.venue_name,
               countries.name as country_name,
               cities.name as city_name,
               states.name as state_name,
               cs.complete is not null as has_setlist,
               cr.concert_id is not null as has_recordings,
               cm.concert_id is not null as has_media,
               ct.name as tour_name
        from concerts as c 
          full join venues as v on c.venue_id = v.venue_id
          full join locations as l on c.location_id = l.id 
          full join countries on l.fk_country_id = countries.id
          full join cities on l.fk_cities_id = cities.id 
          full join states on l.fk_state_id = states.id
          full join concert_setlist as cs on c.concert_id = cs.concert_id
          full join (select distinct concert_id from concert_recording_mapping) as cr on c.concert_id = cr.concert_id
          full join (select distinct concert_id from media_concert) as cm on c.concert_id = cm.concert_id
          full join concert_tours as ct on c.tour_id = ct.id
        where c.artist_id = %s and c.era_id = %s
        order by date ASC;""", (artist_inst.artist_id, era_inst.era_id))
    res = []
    concerts = cur.fetchall()
    for concert_row in concerts:
        concert = initialize_from_result(cur, artist_inst, concert_row)
        res.append(concert)
    return res


def get_all_for_artist_listing_only(cur, artist_inst, year=None):
    """ Gets all concerts for an artist. This returns a subset of concert
    information, it's namely intended to be used when listing concert info,
    ex date, venue, location, etc. Note that it returns the listing in
    sorted order by date.

    There's probably a better way of consolidating the two below queries,
    but there is guaranteed to be safe with respect to year injection
    (assuming that year has been validated at this point already).

    Args:
        cur: a cursor to the database
        artist_inst: an instance of Artist
        year: optional string representing a year. If specified we filter
              results such that only concerts of that year are returned.
    """
    if not artist_inst:
        return None
    if not year:
        cur.execute("""
            select c.date,
                   c.concert_friendly_url,
                   v.venue_name,
                   countries.name as country_name,
                   cities.name as city_name,
                   states.name as state_name,
                   cs.complete is not null as has_setlist,
                   cr.concert_id is not null as has_recordings,
                   cm.concert_id is not null as has_media,
                   ct.name as tour_name
            from concerts as c 
              full join venues as v on c.venue_id = v.venue_id
              full join locations as l on c.location_id = l.id 
              full join countries on l.fk_country_id = countries.id
              full join cities on l.fk_cities_id = cities.id 
              full join states on l.fk_state_id = states.id
              full join concert_setlist as cs on c.concert_id = cs.concert_id
              full join (select distinct concert_id from concert_recording_mapping) as cr on c.concert_id = cr.concert_id
              full join (select distinct concert_id from media_concert) as cm on c.concert_id = cm.concert_id
              full join concert_tours as ct on c.tour_id = ct.id
            where c.artist_id = %s
            order by date ASC;""", (artist_inst.artist_id,))
    else:
        cur.execute("""
            select c.date,
                   c.concert_friendly_url,
                   v.venue_name,
                   countries.name as country_name,
                   cities.name as city_name,
                   states.name as state_name,
                   cs.complete is not null as has_setlist,
                   cr.concert_id is not null as has_recordings,
                   cm.concert_id is not null as has_media,
                   ct.name as tour_name
            from concerts as c 
              full join venues as v on c.venue_id = v.venue_id
              full join locations as l on c.location_id = l.id 
              full join countries on l.fk_country_id = countries.id
              full join cities on l.fk_cities_id = cities.id 
              full join states on l.fk_state_id = states.id
              full join concert_setlist as cs on c.concert_id = cs.concert_id
              full join (select distinct concert_id from concert_recording_mapping) as cr on c.concert_id = cr.concert_id
              full join (select distinct concert_id from media_concert) as cm on c.concert_id = cm.concert_id
              full join concert_tours as ct on c.tour_id = ct.id
            where c.artist_id = %s
                  and date_part('year', c.date) = %s
            order by date ASC;""", (artist_inst.artist_id, year))

    res = []
    concerts = cur.fetchall()
    for concert_row in concerts:
        concert = initialize_from_result(cur, artist_inst, concert_row)
        res.append(concert)
    return res


def get_upcoming_concerts(cur, artist_inst, limit=None):
    """ Gets all upcoming concerts for a given artist
    Args:
        cur: a cursor to the database
        artist_inst: an instance of Artist
        limit: how many shows to fetch. None means fetch next 200 shows
               (seriously who has more than 200 upcoming shows at a time)..
    """
    if not artist_inst:
        return None
    if not limit:
        limit = 200
    cur.execute("""
        select c.date,
               c.concert_friendly_url,
               v.venue_name,
               countries.name as country_name,
               cities.name as city_name,
               states.name as state_name
        from concerts as c 
          full join venues as v on c.venue_id = v.venue_id
          full join locations as l on c.location_id = l.id 
          full join countries on l.fk_country_id = countries.id
          full join cities on l.fk_cities_id = cities.id 
          full join states on l.fk_state_id = states.id
        where c.artist_id = %s
              and date > CURRENT_DATE
        order by date ASC
        limit %s""", (artist_inst.artist_id,limit,))
    res = []
    concerts = cur.fetchall()
    for concert_row in concerts:
        concert = initialize_from_result(cur, artist_inst, concert_row)
        res.append(concert)
    return res


def get_for_artist_and_url(
        cur,
        artist_inst,
        url,
        fetch_setlist=True,
        fetch_before_prev_concert=True):
    """ Returns a concert given an artist and a url.

    Args:
        cur: database cursor
        artist_inst: an instance of an Artist object
        url: the url of the concert.
    """
    if not artist_inst:
        return None
    cur.execute("""
        select c.date,
               c.concert_friendly_url,
               c.notes,
               c.concert_id,
               v.venue_name,
               countries.name as country_name,
               cities.name as city_name,
               states.name as state_name,
               ct.name as tour_name
        from concerts as c 
          full join venues as v on c.venue_id = v.venue_id
          full join locations as l on c.location_id = l.id 
          full join countries on l.fk_country_id = countries.id
          full join cities on l.fk_cities_id = cities.id 
          full join states on l.fk_state_id = states.id
          full join concert_tours as ct on c.tour_id = ct.id
        where c.artist_id=%s
              and c.concert_friendly_url=%s""",
        (artist_inst.artist_id, url))
    concert_row = cur.fetchone()
    if not concert_row:
        return None
    concert = initialize_from_result(
            cur,
            artist_inst,
            concert_row,
            fetch_setlist=fetch_setlist,
            fetch_before_prev_concert=fetch_before_prev_concert)
    return concert


def get_concerts_with_song(cur, artist_inst, song_id):
    """ Gets the concerts at which song was played.

    The inner join accounts for versions - we dont
    use latest version from the concert_setlist table here. We might
    need to change that in the future - if we enforce that we go
    one to one with version / latest_version, then we're fine.

    Args:
        cur: database cursor
        artist_inst: an instance of an Artist object
        song_id: the id of the song we're searching for
    """
    cur.execute("""
        select c.date,
               c.concert_friendly_url,
               c.notes,
               c.concert_id,
               v.venue_name,
               countries.name as country_name,
               cities.name as city_name,
               states.name as state_name
        from concerts as c 
          full join venues as v on c.venue_id = v.venue_id
          full join locations as l on c.location_id = l.id 
          full join countries on l.fk_country_id = countries.id
          full join cities on l.fk_cities_id = cities.id 
          full join states on l.fk_state_id = states.id
        where c.artist_id=%s
              and c.concert_id in (
                select cso.concert_id
                from concert_setlist_ordering as cso
                inner join (
                    select concert_id, max(version) as latest_version
                    from concert_setlist_ordering
                    group by concert_id) grouped_versions
                on cso.concert_id = grouped_versions.concert_id
                and cso.version = grouped_versions.latest_version
                where cso.song_id = %s
              )
        order by c.date asc; """ % (artist_inst.artist_id, song_id,))
    res = []
    concerts = cur.fetchall()
    for concert_row in concerts:
        concert = initialize_from_result(cur, artist_inst, concert_row)
        res.append(concert)
    return res


def get_count_of_concerts_for_all_songs(cur, artist_inst):
    """ Gets the count of song to performances by that particular
    artist. This might need to get moved to song... not sure if this
    belongs here.

    Args:
        cur: database cursor
        artist_inst: an instance of an Artist object

    Returns:
        list of songs sorted by performance count in descending order
    """
    cur.execute("""
        select s.title,
               s.song_url,
               case
                when song_count_info.concert_count is not null 
                    then song_count_info.concert_count
                else 0
               end as concert_count
        from songs as s
        full join  (
          select cso.song_id,
                 count(cso.concert_id) as concert_count
          from concert_setlist_ordering as cso
          left join songs as s on s.song_id = cso.song_id
          full join (
            select concert_id, max(version) as latest_version
            from concert_setlist_ordering
            group by concert_id) grouped_versions
            on cso.concert_id = grouped_versions.concert_id
               and cso.version = grouped_versions.latest_version
            where s.artist_id = %s
            group by cso.song_id
          )  song_count_info
          on s.song_id = song_count_info.song_id
        where s.artist_id = %s
        order by song_count_info.concert_count desc nulls last
    """, (artist_inst.artist_id, artist_inst.artist_id))
    res = []
    songs = cur.fetchall()
    for row in songs:
        song_inst = Song(
                title=row.get("title"),
                song_url=row.get("song_url"),
                concert_count=row.get("concert_count"))
        res.append(song_inst)
    return res


def get_years_of_concerts_for_artist(cur, artist_inst):
    """ Gets the years that the artist had concerts in.

    Args:
        cur: database cursor
        artist_inst: an instance of an Artist object

    Returns:
        sorted list of years.
    """
    if not artist_inst:
        return set() 

    cur.execute("""
        select distinct(date_part('year', date))::int as year
        from concerts as c
        where c.artist_id = %s 
        order by year asc;""", (artist_inst.artist_id,))
    years = cur.fetchall()
    year_set = set()
    for year in years: year_set.add(year.get("year"))
    return year_set
