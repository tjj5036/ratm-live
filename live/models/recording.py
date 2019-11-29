class RecordingType:
    """ Helper class to represent the type of a recording, ex FLAC,
    DVD, etc. You can think of it like a file format.
    """
    def __init__(
            self,
            recording_type_id=None,
            recording_name=None,
            row=None):
        """ Initializes a recording type id.

        Args:
            recording_type_id: the id in the database
            recording_name: the name of the recording type, ie 'FLAC'
            row: database representation. If specified, takes precedence
        """
        if row is not None:
            self.recording_type_id = row.get('recording_type_id')
            self.recording_name = row.get('recording_name')
        else:
            self.recording_type_id = recording_type_id
            self.recording_name = recording_name


class SourceType:
    """ Helper class to encapsulate the source type of a recording, ex
    'Audience', etc.
    """
    def __init__(
            self,
            source_type_id=None,
            source_name=None,
            row=None):
        if row is not None:
            self.source_type_id = row.get('source_type_id')
            self.source_name = row.get('source_name')
        else:
            self.source_type_id = source_type_id
            self.source_name = source_name


class Recording:
    """ Encapsulates all information about a given recording.
    """

    def __init__(
            self,
            recording_id=0,
            lineage=None,
            notes=None,
            length=0,
            complete=False,
            row=None):
        """ Initializes a recording object.

        Args:
            row: database representation of a recording
        """
        if row is not None:
            self.recording_id = row.get('recording_id')
            self.lineage = row.get('lineage')
            self.notes = row.get('notes')
            self.complete = row.get('complete', False)
            self.length = row.get('length', 0)
            self.taper = row.get('taper')
            self.source_type = SourceType(
                source_name=row.get('source_name'))
            self.recording_type = RecordingType(
                recording_name= row.get('recording_name'))
        else:
            self.recording_id = recording_id
            self.lineage = lineage
            self.notes = notes
            self.complete = complete
            self.length = length
            self.taper = taper
            self.source_type = None
            self.recording_type = None

        # Files for this recording
        self.recording_files = []

        # Preview URLs. For now, we assume this is Youtube, but we should
        # account for others later like Soundcloud
        self.preview_urls = []


def get_all_recordings_for_concert(cur,
                                   concert_id,
                                   include_files=True,
                                   include_preview_urls=True):
    """ Gets all recordings for a given concert.

    Args:
        cur: database cursor
        concert_id: id of the concert.
        include_files: whether or not to fetch files for the recording
        include_preview_urls: whether or not to fetch preview urls

    Returns:
        list of Recordings
    """
    cur.execute("""
        select r.recording_id,
               rt.recording_name,
	       s.source_name,
	       r.taper,
	       r.length,
	       r.lineage,
	       r.notes,
	       r.complete
        from recording as r
        join source_types as s on r.source_type = s.source_type_id
        join recording_types as rt on r.recording_type =  rt.recording_type_id
        left join concert_recording_mapping as crm on crm.recording_id = r.recording_id
        where crm.concert_id = %s""", (concert_id,))

    recordings = []
    recording_rows = cur.fetchall()
    for recording_row in recording_rows:
        recordings.append(Recording(row=recording_row))
    if include_files:
        for recording in recordings:
            cur.execute("""
                select file_url from recording_file
                where recording_id = %s
                and is_public = True""", (recording.recording_id,))
            recording_files = cur.fetchall()
            for recording_file in recording_files:
                recording.recording_files.append(recording_file.get('file_url'))
    if include_preview_urls:
        for recording in recordings:
            cur.execute("""
                select preview_url from  recording_preview_urls
                where recording_id = %s""", (recording.recording_id,))
            preview_urls = cur.fetchall()
            for preview_url in preview_urls:
                recording.preview_urls.append(preview_url.get('preview_url'))
    return recordings
