
class EasyID3Manager():  # pragma: no_cover

    def __init__(self, fileFullPath):
        self.filePath = fileFullPath
        self.title = None
        self.album = None
        self.artist = None
        self.playlist_name = None
        self.trackNumber = None

    def change_file_path(self, fileFullPath):
        self.filePath = fileFullPath

    def set_params(self,
                   title=None,
                   album=None,
                   artist=None,
                   trackNumber=None,
                   playlist_name=None):
        self.title = title
        self.album = album
        self.artist = artist
        self.playlist_name = playlist_name
        self.trackNumber = trackNumber

    def save_meta_data(self):
        pass

    def set_playlist_name(self, playlist_name):
        self.playlist_name = playlist_name

    def _show_meta_data_info(self, path):  # pragma: no_cover
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        pass
