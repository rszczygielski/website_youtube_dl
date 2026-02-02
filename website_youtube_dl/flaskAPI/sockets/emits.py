from abc import ABC, abstractmethod
from ...common.youtubeDataKeys import PlaylistInfo, MediaInfo
from ... import socketio
from flask import current_app as app

class BaseEmit(ABC):
    data_str = "data"
    error_str = "error"

    def __init__(self, emit_msg) -> None:
        self.emit_msg = emit_msg

    def send_emit(self, data, session_id):
        converted_data = self.convert_data_to_message(data)
        app.logger.debug(f'Sending emit {self.emit_msg} to session {session_id} with data {converted_data}')
        socketio.emit(self.emit_msg, {
                      self.data_str: converted_data}, to=session_id)

    def send_emit_error(self, error_msg, session_id):
        socketio.emit(self.emit_msg, {
                      self.error_str: error_msg}, to=session_id)

    @abstractmethod
    def convert_data_to_message(self):  # pragma: no_cover
        pass


class DownloadMediaFinishEmit(BaseEmit):
    hash_data_key = "HASH"

    def __init__(self) -> None:
        emit_msg = "downloadMediaFinish"
        super().__init__(emit_msg)

    def convert_data_to_message(self, genereted_hash):
        return {self.hash_data_key: genereted_hash}


class SingleMediaInfoEmit(BaseEmit):
    def __init__(self) -> None:
        emit_msg = "mediaInfo"
        super().__init__(emit_msg)

    def convert_data_to_message(self, flask_single_media):
        media_info_dict = {
            MediaInfo.TITLE.value: flask_single_media.title,
            MediaInfo.ARTIST.value: flask_single_media.artist,
            MediaInfo.URL.value: flask_single_media.url
        }
        return media_info_dict


class PlaylistMediaInfoEmit(BaseEmit):
    playlist_name_data_key = "playlistName"
    track_list_data_key = "trackList"

    def __init__(self) -> None:
        emit_msg = "playlistMediaInfo"
        super().__init__(emit_msg)

    def convert_data_to_message(self, flask_playlist_media):
        playlist_name_value = flask_playlist_media.playlist_name
        playlist_track_list = []
        for track in flask_playlist_media.track_list:
            track_info_dict = {
                PlaylistInfo.TITLE.value: track.title,
                PlaylistInfo.URL.value: track.url,
            }
            playlist_track_list.append(track_info_dict)
        return {self.playlist_name_data_key: playlist_name_value,
                self.track_list_data_key: playlist_track_list}


class UploadPlaylistToConfigEmit(BaseEmit):
    playlist_list_data_key = "playlistList"

    def __init__(self):
        emit_msg = "uploadPlaylists"
        super().__init__(emit_msg)

    def convert_data_to_message(self, playlist_list):
        return {self.playlist_list_data_key: playlist_list}


class GetPlaylistUrlEmit(BaseEmit):
    playlist_url_data_key = "playlistUrl"

    def __init__(self):
        emit_msg = "playlistUrl"
        super().__init__(emit_msg)

    def convert_data_to_message(self, playlistUrl):
        return {self.playlist_url_data_key: playlistUrl}


class PlaylistTrackFinish(BaseEmit):
    index_data_key = "index"

    def __init__(self):
        emit_msg = "playlistTrackFinish"
        super().__init__(emit_msg)

    def convert_data_to_message(self, index):
        return {self.index_data_key: index}