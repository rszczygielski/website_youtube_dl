from flask import current_app as app
from ...common.youtubeAPI import (
    SingleMedia, PlaylistMedia, ResultOfYoutube
)
from ..services.flaskMedia import FlaskPlaylistMedia, FlaskSingleMedia
from .emits import (
    SingleMediaInfoEmit, PlaylistMediaInfoEmit, DownloadMediaFinishEmit
)
from ...common.youtubeLogKeys import YoutubeLogs

class YoutubeMediaInfoHandler():
    def __init__(self, namespace=None):
        self.namespace = namespace

    def send_emit_single_media_info_from_youtube(self, single_media_url, user_browser_id):
        single_media_info_result: ResultOfYoutube = app.youtube_helper.request_single_media_info(
            single_media_url)
        if single_media_info_result.is_error():
            app.logger.error("Failed to get single media info")
            return False
        app.logger.debug(f'Got single media info, processing emit {single_media_url}')
        mediaInfo: SingleMedia = single_media_info_result.get_data()
        flask_single_media = FlaskSingleMedia(
            mediaInfo.title, mediaInfo.artist, mediaInfo.url)

        app.socket_manager.process_emit(data=flask_single_media,
                                        emit_type=SingleMediaInfoEmit,
                                        user_browser_id=user_browser_id,
                                        namespace=self.namespace)
        return True


    def send_emit_playlist_media(self, youtube_url, user_browser_id):
        app.logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
        playlist_media_info_result = app.youtube_helper.request_playlist_media_info(
            youtube_url)
        if playlist_media_info_result.is_error():
            app.logger.error("Failed to get playlist media info")
            return None
        app.logger.debug(f'Got playlist media info, processing emit {youtube_url}')
        playlist_media: PlaylistMedia = playlist_media_info_result.get_data()
        playlist_name = playlist_media.playlist_name
        flask_playlist_media = FlaskPlaylistMedia.init_from_playlist_media(
            playlist_name, playlist_media.media_from_playlist_list)
        app.logger.debug(f'Playlist name: {playlist_name} tracks: {len(playlist_media.media_from_playlist_list)}')
        app.logger.debug(f'Browser ID: {user_browser_id} for playlist emit')

        app.socket_manager.process_emit(data=flask_playlist_media,
                                        emit_type=PlaylistMediaInfoEmit,
                                        user_browser_id=user_browser_id,
                                        namespace=self.namespace)
        return playlist_media


    def send_emit_media_finish_error(self, error_msg, user_browser_id):
        app.logger.warning(error_msg)
        app.socket_manager.process_emit_error(error_msg=error_msg,
                                            emit_type=DownloadMediaFinishEmit,
                                            user_browser_id=user_browser_id,
                                            namespace=self.namespace)