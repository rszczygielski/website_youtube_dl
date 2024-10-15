import os


class FlaskSingleMedia():
    def __init__(self, title: str, artist: str, url: str) -> None:
        self.title = title
        self.artist = artist
        self.url = url


class FlaskMediaFromPlaylist():
    def __init__(self, title, url):
        self.title = title
        self.url = url


class FlaskPlaylistMedia():
    def __init__(self, plyalistName: str,
                 trackList: list[FlaskMediaFromPlaylist]) -> None:
        self.playlistName = plyalistName
        self.trackList = trackList

    @classmethod
    def initFromPlaylistMedia(cls, playlistName, trackList):
        flaskSingleMediaList = []
        for track in trackList:
            flaskSingleMediaList.append(FlaskMediaFromPlaylist(track.title,
                                                               track.ytHash))
        return cls(playlistName, flaskSingleMediaList)


class SessionDownloadData():
    fileName = None
    fileDirectoryPath = None

    def __init__(self, fullFilePath) -> None:
        self.setSessionDownloadData(fullFilePath)

    def setSessionDownloadData(self, fullFilePath):
        if not os.path.isfile(fullFilePath):
            raise FileNotFoundError(
                f"File {fullFilePath} doesn't exist - something went wrong")
        splitedFilePath = fullFilePath.split("/")
        self.fileName = splitedFilePath[-1]
        self.fileDirectoryPath = "/".join(splitedFilePath[:-1])
