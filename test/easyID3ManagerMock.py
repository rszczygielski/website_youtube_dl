class EasyID3ManagerMock():  # pragma: no_cover

    def __init__(self, fileFullPath=None):
        self.file_path = fileFullPath
        self.title = None
        self.album = None
        self.artist = None
        self.playlist_name = None
        self.track_number = None
        self.website = None

    def change_file_path(self, fileFullPath):
        self.file_path = fileFullPath

    def set_params(self,
                   filePath,
                   title=None,
                   album=None,
                   artist=None,
                   yt_hash=None,
                   track_number=None,
                   playlist_name=None):
        self.file_path = filePath
        self.title = title
        self.album = album
        self.artist = artist
        self.website = yt_hash
        self.track_number = track_number
        self.playlist_name = playlist_name

    def save_meta_data(self):
        pass

    def read_meta_data(self):
        pass

    def set_playlist_name(self, playlist_name):
        self.playlist_name = playlist_name

    def _show_meta_data_info(self, path):
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        print(f"Mock metadata info for {path}")
