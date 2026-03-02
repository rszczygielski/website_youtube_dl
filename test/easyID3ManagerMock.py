class EasyID3ManagerMock:  # pragma: no_cover
    """
    Mock class for EasyID3 metadata management to bypass 
    actual file tagging during unit tests.
    """

    def __init__(self, file_full_path=None):
        self.file_path = file_full_path
        self.title = None
        self.album = None
        self.artist = None
        self.playlist_name = None
        self.track_number = None
        self.website = None

    def change_file_path(self, file_full_path):
        """Updates the internal file path reference."""
        self.file_path = file_full_path

    def set_params(self,
                   file_path,
                   title=None,
                   album=None,
                   artist=None,
                   yt_hash=None,
                   track_number=None,
                   playlist_name=None):
        """
        Sets multiple metadata parameters at once.
        Note: yt_hash is mapped to the 'website' field.
        """
        self.file_path = file_path
        self.title = title
        self.album = album
        self.artist = artist
        self.website = yt_hash
        self.track_number = track_number
        self.playlist_name = playlist_name

    def save_meta_data(self):
        """Mock implementation of saving metadata (Nop)."""
        pass

    def read_meta_data(self):
        """Mock implementation of reading metadata (Nop)."""
        pass

    def set_playlist_name(self, playlist_name):
        """Sets the name of the playlist associated with the track."""
        self.playlist_name = playlist_name

    def _show_meta_data_info(self, path):
        """
        Displays mock metadata info for debugging.
        
        Args:
            path (str): The target file path.
        """
        print(f"DEBUG: Mock metadata info for {path}")