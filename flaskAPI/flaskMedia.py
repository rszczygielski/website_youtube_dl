import os

class FlaskSingleMedia():  # pragma: no_cover
    def __init__(self, title: str, artist: str, url: str) -> None:
        self.title = title
        self.artist = artist
        self.url = url

class FlaskMediaFromPlaylist():
    def __init__(self, title, url):
        self.title = title
        self.url = url

class FlaskPlaylistMedia():  # pragma: no_cover
    def __init__(self, plyalistName: str, trackList: list[FlaskMediaFromPlaylist]) -> None:
        self.playlistName = plyalistName
        self.trackList = trackList

    @classmethod
    def initFromPlaylistMedia(cls, playlistName, trackList):
        flaskSingleMediaList = []
        for track in trackList:
            flaskSingleMediaList.append(FlaskMediaFromPlaylist(track.title,
                                                                track.ytHash))
        return cls(playlistName, flaskSingleMediaList)

class FileInfo():
    fileName = None
    fileDirectoryPath = None

    def __init__(self, fullFilePath) -> None:
        if not os.path.isfile(fullFilePath):
            raise FileNotFoundError(
                f"File {fullFilePath} doesn't exist - something went wrong")
        self.setFileInfo(fullFilePath)

    def setFileInfo(self, fullFilePath):
        splitedFilePath = fullFilePath.split("/")
        self.fileName = splitedFilePath[-1]
        self.fileDirectoryPath = "/".join(splitedFilePath[:-1])
