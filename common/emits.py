import random
import string
from abc import ABC, abstractmethod
from common.youtubeDataKeys import PlaylistInfo, MediaInfo
from mainWebPage import socketio

class BaseEmit(ABC):
    emit_msg = ""

    @abstractmethod
    def send_emit(self):
        pass

    @abstractmethod
    def convert_data_to_message(self):
        pass

    def convert_error_to_message(self):
        pass


class DownloadMediaFinishEmit(BaseEmit):
    emit_msg = "downloadMediaFinish"

    def __init__(self):
        self.genereted_hash = self.generete_hash()

    def generete_hash(self):
        return ''.join(random.sample(string.ascii_letters + string.digits, 6))

    def get_data_dict(self, fullFilePath):
        splitedFilePath = fullFilePath.split("/")
        fileName = splitedFilePath[-1]
        direcotryPath = "/".join(splitedFilePath[:-1])
        data_dict = {"downloadFileName": fileName,
                     "downloadDirectoryPath": direcotryPath}
        return data_dict

    def convert_data_to_message(self):
        return {"data": {"HASH": self.genereted_hash}}

    def send_emit_error(self, error_msg):
        socketio.emit({"error": error_msg})

    def send_emit(self, data):
        converted_data = self.convert_data_to_message(data)
        socketio.emit(self.emit_msg, converted_data)

class SingleMediaInfoEmit(BaseEmit):
    emit_msg = "mediaInfo"

    def convert_data_to_message(self, flaskSingleMedia):
        mediaInfoDict = {
        MediaInfo.TITLE.value: flaskSingleMedia.title,
        MediaInfo.ARTIST.value: flaskSingleMedia.artist,
        MediaInfo.URL.value: flaskSingleMedia.url
        }
        return {"data": [mediaInfoDict]}
    
    def send_emit(self, data):
        converted_data = self.convert_data_to_message(data)
        return socketio.emit(self.emit_msg, converted_data)

class PlaylistMediaInfoEmit(BaseEmit):
    emit_msg = "mediaInfo"

    def convert_data_to_message(self, playlistInfo, playlistName):
        playlistTrackList = []
        for track in playlistInfo.singleMediaList:
            trackInfoDict = {
                PlaylistInfo.TITLE.value: track.title,
                PlaylistInfo.ALBUM.value: track.album ,
                PlaylistInfo.ARTIST.value: track.artist,
                PlaylistInfo.YOUTUBE_HASH.value: track.ytHash,
                PlaylistInfo.URL.value: track.url,
                PlaylistInfo.PLAYLIST_INDEX.value: track.playlistIndex,
                PlaylistInfo.PLAYLIST_NAME.value: playlistName
            }
            playlistTrackList.append(trackInfoDict)
        return {"data": playlistTrackList}

    def send_emit(self, playlistData, playlistName):
        converted_data = self.convert_data_to_message(playlistData, playlistName)
        return socketio.emit(self.emit_msg, converted_data)

class DownloadErrorEmit():
    emit_msg = "downloadError"
    format_not_specified = "Format not specified"
    empty_url = "Youtube URL empty"

    def sendEmitFormatNotSpecified(self):
        return socketio.emit(self.emit_msg, self.format_not_specified)
    
    def sendEmitNoUrl(self):
        return socketio.emit(self.emit_msg, self.empty_url)

