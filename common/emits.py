import random
import string
from abc import ABC, abstractmethod
from common.youtubeDataKeys import PlaylistInfo, MediaInfo
from mainWebPage import socketio


class BaseEmit(ABC):
    emit_msg = ""

    @abstractmethod
    def sendEmit(self):
        pass

    @abstractmethod
    def convertDataToMessage(self):
        pass


class DownloadMediaFinishEmit(BaseEmit):
    emit_msg = "downloadMediaFinish"

    def convertDataToMessage(self, genereted_hash):
        return {"data": {"HASH": genereted_hash}}

    def sendEmitError(self, error_msg):
        socketio.emit({"error": error_msg})

    def sendEmit(self, genereted_hash):
        converted_data = self.convertDataToMessage(genereted_hash)
        socketio.emit(self.emit_msg, converted_data)


class SingleMediaInfoEmit(BaseEmit):
    emit_msg = "mediaInfo"

    def convertDataToMessage(self, flaskSingleMedia):
        mediaInfoDict = {
            MediaInfo.TITLE.value: flaskSingleMedia.title,
            MediaInfo.ARTIST.value: flaskSingleMedia.artist,
            MediaInfo.URL.value: flaskSingleMedia.url
        }
        return {"data": [mediaInfoDict]}

    def sendEmit(self, data):
        converted_data = self.convertDataToMessage(data)
        return socketio.emit(self.emit_msg, converted_data)


class PlaylistMediaInfoEmit(BaseEmit):
    emit_msg = "mediaInfo"

    def convertDataToMessage(self, flaskPlaylistMedia):
        playlistName = flaskPlaylistMedia.playlistName
        playlistTrackList = []
        for track in flaskPlaylistMedia.trackList:
            trackInfoDict = {
                PlaylistInfo.TITLE.value: track.title,
                PlaylistInfo.ARTIST.value: track.artist,
                PlaylistInfo.URL.value: track.url,
                PlaylistInfo.PLAYLIST_NAME.value: playlistName
            }
            playlistTrackList.append(trackInfoDict)
        return {"data": playlistTrackList}

    def sendEmit(self, playlistData):
        converted_data = self.convertDataToMessage(playlistData)
        return socketio.emit(self.emit_msg, converted_data)


class DownloadErrorEmit():
    emit_msg = "downloadError"
    format_not_specified = "Format not specified"
    empty_url = "Youtube URL empty"

    def sendEmitFormatNotSpecified(self):
        return socketio.emit(self.emit_msg, self.format_not_specified)

    def sendEmitNoUrl(self):
        return socketio.emit(self.emit_msg, self.empty_url)
