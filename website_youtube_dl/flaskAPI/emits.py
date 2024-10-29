from abc import ABC, abstractmethod
from ..common.youtubeDataKeys import PlaylistInfo, MediaInfo
from .emitKeys import EmitAttributes, EmitMessages
from .. import socketio


class BaseEmit(ABC):
    def __init__(self, emitMsg) -> None:
        self.emitMsg = emitMsg

    def sendEmit(self, data):
        convertedData = self.convertDataToMessage(data)
        socketio.emit(self.emitMsg, {EmitAttributes.DATA.value: convertedData})

    @abstractmethod
    def convertDataToMessage(self):  # pragma: no_cover
        pass


class DownloadMediaFinishEmit(BaseEmit):
    def __init__(self) -> None:
        emitMsg = EmitMessages.DOWNLOAD_MEDIA_FINISH.value
        super().__init__(emitMsg)

    def convertDataToMessage(self, genereted_hash):
        return {"HASH": genereted_hash}

    def sendEmitError(self, error_msg):
        socketio.emit(self.emitMsg, {EmitAttributes.ERROR.value: error_msg})


class SingleMediaInfoEmit(BaseEmit):
    def __init__(self) -> None:
        emitMsg = EmitMessages.MEDIA_INFO.value
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
        emitMsg = EmitMessages.PLAYLIST_MEDIA_INFO.value
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
        return {EmitAttributes.PLAYLIST_NAME.value: playlistName,
                EmitAttributes.TRACK_LIST.value: playlistTrackList}


class UploadPlaylistToConfigEmit(BaseEmit):
    def __init__(self):
        emitMsg = EmitMessages.UPLOAD_PLAYLISTS.value
        super().__init__(emitMsg)

    def convertDataToMessage(self, playlistList):
        return {EmitAttributes.PLAYLIST_LIST.value: playlistList}


class GetPlaylistUrlEmit(BaseEmit):
    def __init__(self):
        emitMsg = EmitMessages.PLAYLIST_URL.value
        super().__init__(emitMsg)

    def convertDataToMessage(self, playlistUrl):
        return {EmitMessages.PLAYLIST_URL.value: playlistUrl}
