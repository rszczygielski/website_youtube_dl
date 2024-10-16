from abc import ABC, abstractmethod
from ..common.youtubeDataKeys import PlaylistInfo, MediaInfo
from .. import socketio
# from flaskAPI.youtube import FlaskSingleMedia


class BaseEmit(ABC):
    def __init__(self, emit_msg) -> None:
        self.emit_msg = emit_msg

    def sendEmit(self, data):
        convertedData = self.convertDataToMessage(data)
        print(convertedData)
        print(self.emit_msg)
        socketio.emit(self.emit_msg, {"data": convertedData})

    @abstractmethod
    def convertDataToMessage(self): # pragma: no_cover
        pass


class DownloadMediaFinishEmit(BaseEmit):
    def __init__(self) -> None:
        emit_msg = "downloadMediaFinish"
        super().__init__(emit_msg)

    def convertDataToMessage(self, genereted_hash):
        return {"HASH": genereted_hash}

    def sendEmitError(self, error_msg):
        socketio.emit(self.emit_msg, {"error": error_msg})


class SingleMediaInfoEmit(BaseEmit):
    def __init__(self) -> None:
        emit_msg = "mediaInfo"
        super().__init__(emit_msg)
    

    def convertDataToMessage(self, flaskSingleMedia):
        mediaInfoDict = {
            MediaInfo.TITLE.value: flaskSingleMedia.title,
            MediaInfo.ARTIST.value: flaskSingleMedia.artist,
            MediaInfo.URL.value: flaskSingleMedia.url
        }
        return mediaInfoDict


class PlaylistMediaInfoEmit(BaseEmit):
    def __init__(self) -> None:
        emit_msg = "playlistMediaInfo"
        super().__init__(emit_msg)
    

    def convertDataToMessage(self, flaskPlaylistMedia):
        playlistName = flaskPlaylistMedia.playlistName
        playlistTrackList = []
        for track in flaskPlaylistMedia.trackList:
            print(type(track))
            trackInfoDict = {
                PlaylistInfo.TITLE.value: track.title,
                PlaylistInfo.URL.value: track.url,
            }
            playlistTrackList.append(trackInfoDict)
        return {"playlistName": playlistName,
                "trackList": playlistTrackList}
