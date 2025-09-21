from flask import current_app as app
from ...common.youtubeAPI import (
    SingleMedia, PlaylistMedia, ResultOfYoutube
)
from ..services.flaskMedia import FlaskPlaylistMedia, FlaskSingleMedia
from ..sockets.emits import (
    SingleMediaInfoEmit, PlaylistMediaInfoEmit, DownloadMediaFinishEmit
)
from ...common.youtubeLogKeys import YoutubeLogs


def send_emit_single_media_info_from_youtube(single_media_url, user_browser_id):
    single_media_info_result: ResultOfYoutube = app.youtube_helper.request_single_media_info(
        single_media_url)
    if single_media_info_result.is_error():
        return False
    mediaInfo: SingleMedia = single_media_info_result.get_data()
    flask_single_media = FlaskSingleMedia(
        mediaInfo.title, mediaInfo.artist, mediaInfo.url)
    app.socket_manager.process_emit(data=flask_single_media,
                                    emit_type=SingleMediaInfoEmit,
                                    user_browser_id=user_browser_id)
    return True


def send_emit_playlist_media(youtube_url, user_browser_id):
    app.logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
    playlist_media_info_result = app.youtube_helper.request_playlist_media_info(
        youtube_url)
    if playlist_media_info_result.is_error():
        return None
    playlist_media: PlaylistMedia = playlist_media_info_result.get_data()
    playlist_name = playlist_media.playlist_name
    flask_playlist_media = FlaskPlaylistMedia.init_from_playlist_media(
        playlist_name, playlist_media.media_from_playlist_list)
    app.socket_manager.process_emit(data=flask_playlist_media,
                                    emit_type=PlaylistMediaInfoEmit,
                                    user_browser_id=user_browser_id)
    return playlist_media

def send_emit_media_finish_error(error_msg, user_browser_id):
        app.logger.warning(error_msg)
        app.socket_manager.process_emit(data=error_msg,
                                        emit_type=DownloadMediaFinishEmit,
                                        user_browser_id=user_browser_id)

def handle_error(error_msg, user_browser_id):  # pragma: no_cover
    app.socket_manager.process_emit(data=error_msg,
                                    emit_type=DownloadMediaFinishEmit,
                                    user_browser_id=user_browser_id)