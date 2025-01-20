from abc import ABC, abstractmethod
from ..common.youtubeDataKeys import PlaylistInfo, MediaInfo
from .. import socketio


class BaseEmit(ABC):
    dataStr = "data"
    playlistName = "playlistName"
    trackList = "trackList"
    playlistList = "playlistList"
    errorStr = "error"

    def __init__(self, emitMsg) -> None:
        self.emitMsg = emitMsg

    def sendEmit(self, data):
        convertedData = self.convertDataToMessage(data)
        socketio.emit(self.emitMsg, {self.dataStr: convertedData})

    def sendEmitError(self, error_msg):
        socketio.emit(self.emitMsg, {self.errorStr: error_msg})

    @abstractmethod
    def convertDataToMessage(self):  # pragma: no_cover
        pass


class DownloadMediaFinishEmit(BaseEmit):

    def __init__(self) -> None:
        emitMsg = "downloadMediaFinish"
        super().__init__(emitMsg)

    def convertDataToMessage(self, genereted_hash):
        return {"HASH": genereted_hash}



class SingleMediaInfoEmit(BaseEmit):
    def __init__(self) -> None:
        emitMsg = "mediaInfo"
        super().__init__(emitMsg)

    def convertDataToMessage(self, flaskSingleMedia):
        mediaInfoDict = {
            MediaInfo.TITLE.value: flaskSingleMedia.title,
            MediaInfo.ARTIST.value: flaskSingleMedia.artist,
            MediaInfo.URL.value: flaskSingleMedia.url
        }
        return mediaInfoDict


class PlaylistMediaInfoEmit(BaseEmit):
    def __init__(self) -> None:
        emitMsg = "playlistMediaInfo"
        super().__init__(emitMsg)

    def convertDataToMessage(self, flaskPlaylistMedia):
        playlistName = flaskPlaylistMedia.playlistName
        playlistTrackList = []
        for track in flaskPlaylistMedia.trackList:
            trackInfoDict = {
                PlaylistInfo.TITLE.value: track.title,
                PlaylistInfo.URL.value: track.url,
            }
            playlistTrackList.append(trackInfoDict)
        return {self.playlistName: playlistName,
                self.trackList: playlistTrackList}


class UploadPlaylistToConfigEmit(BaseEmit):
    def __init__(self):
        emitMsg = "uploadPlaylists"
        super().__init__(emitMsg)

    def convertDataToMessage(self, playlistList):
        return {self.playlistList: playlistList}


class GetPlaylistUrlEmit(BaseEmit):
    playlistUrlStr = "playlistUrl"

    def __init__(self):
        emitMsg = self.playlistUrlStr
        super().__init__(emitMsg)

    def convertDataToMessage(self, playlistUrl):
        return {self.playlistUrlStr: playlistUrl}

class PlaylistTrackFinish(BaseEmit):

    def __init__(self):
        emitMsg = "playlistTrackFinish"
        super().__init__(emitMsg)

    def convertDataToMessage(self, index):
        return {"index": index}

    def sendEmitError(self, index:int):
        socketio.emit(self.emitMsg, {self.errorStr: index})