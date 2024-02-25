import random
import string
from abc import ABC, abstractmethod
from common.youtubeDataKeys import PlaylistInfo, MediaInfo

class BaseEmit(ABC):
    emit_msg = ""

    def convert_error_to_message(self):
        pass

    @abstractmethod
    def convert_data_to_message(self):
        pass

class DownloadMediaFinishEmit(BaseEmit):
    emit_msg = "downloadMediaFinish"
    _file_name_str = "downloadFileName"
    _directory_path_str = "downloadDirectoryPath"

    def __init__(self):
        self.genereted_hash = self.generete_hash()

    def generete_hash(self):
        return ''.join(random.sample(string.ascii_letters + string.digits, 6))

    def get_data_dict(self, fullFilePath):
        splitedFilePath = fullFilePath.split("/")
        fileName = splitedFilePath[-1]
        direcotryPath = "/".join(splitedFilePath[:-1])
        data_dict = {self._file_name_str: fileName,
                     self._directory_path_str: direcotryPath}
        return data_dict

    def convert_data_to_message(self):
        return {"data": {"HASH": self.genereted_hash}}

    def convert_error_to_message(self, error_msg):
        return {"error": error_msg}


class MediaInfoEmit(BaseEmit):
    emit_msg = "mediaInfo"

    def convert_palylist_data_to_message(self):
        pass

    def convert_data_to_message(self, mediaInfo):
        mediaInfoDict = {
        PlaylistInfo.TITLE.value: mediaInfo.title,
        PlaylistInfo.ALBUM.value: mediaInfo.album ,
        PlaylistInfo.ARTIST.value: mediaInfo.artist,
        PlaylistInfo.YOUTUBE_HASH.value: mediaInfo.ytHash,
        PlaylistInfo.URL.value: mediaInfo.url
        }
        return {"data": [mediaInfoDict]}

    def convert_playlist_data_to_message(self, playlistInfo, playlistName):
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


class DownloadErrorEmit():
    emit_msg = "downloadError"
    format_not_specified = "Format not specified"
    empty_url = "Youtube URL empty"

