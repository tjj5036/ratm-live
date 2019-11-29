class Venue:

    def __init__(self, venue_name, location):
        """ Initializes venue information.

        Args:
            venue_name: the name of the venue
            location: populated Location object.
        """
        self.venue_name = venue_name
        self.location = location
