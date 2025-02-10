
class EasyID3Manager():  # pragma: no_cover

    def __init__(self, fileFullPath):
        self.filePath = fileFullPath
        self.title = None
        self.album = None
        self.artist = None
        self.playlistName = None
        self.trackNumber = None

    def changeFilePath(self, fileFullPath):
        self.filePath = fileFullPath

    def setParams(self,
                  title=None,
                  album=None,
                  artist=None,
                  trackNumber=None,
                  playlistName=None):
        self.title = title
        self.album = album
        self.artist = artist
        self.playlistName = playlistName
        self.trackNumber = trackNumber

    def saveMetaData(self):
        pass

    def setPlaylistName(self, playlistName):
        self.playlistName = playlistName

    def _showMetaDataInfo(self, path):  # pragma: no_cover
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        pass