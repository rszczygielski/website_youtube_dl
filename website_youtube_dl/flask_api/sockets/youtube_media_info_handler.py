from flask import current_app as app

from ...common.youtube_api import (
    SingleMedia, PlaylistMedia, ResultOfYoutube
)
from ..services.flask_media import FlaskPlaylistMedia, FlaskSingleMedia
from .emits import (
    SingleMediaInfoEmit, PlaylistMediaInfoEmit, DownloadMediaFinishEmit
)
from ...common.youtube_log_keys import YoutubeLogs


class YoutubeMediaInfoHandler:
    """
    Service responsible for fetching media metadata from YouTube
    and emitting real-time Socket.IO events to the client.
    """

    def __init__(self, namespace: str = None) -> None:
        """
        Initialize the info handler with a specific Socket.IO namespace.

        Args:
            namespace (str, optional): The Socket.IO namespace to emit events to.
        """
        self.namespace = namespace

    def send_emit_single_media_info_from_youtube(self, single_media_url: str, user_browser_id: str) -> bool:
        """
        Fetch single media information from YouTube and emit it to the client.

        Args:
            single_media_url (str): The YouTube URL of the single media track.
            user_browser_id (str): Unique identifier for the user's browser session.

        Returns:
            bool: True if the info was successfully fetched and emitted, False otherwise.
        """
        socket_ctx = app.socket_manager.get_context(user_browser_id, self.namespace)

        single_media_info_result: ResultOfYoutube = app.youtube_downloader.request_single_media_info(
            single_media_url
        )

        if single_media_info_result.is_error():
            app.logger.error("Failed to get single media info")
            return False

        app.logger.debug(f"Got single media info, processing emit {single_media_url}")

        media_info: SingleMedia = single_media_info_result.get_data()

        flask_single_media = FlaskSingleMedia(
            media_info.title, media_info.artist, media_info.url
        )

        socket_ctx.emit(
            data=flask_single_media,
            emit_type=SingleMediaInfoEmit
        )

        return True

    def send_emit_playlist_media(self, youtube_url: str, user_browser_id: str) -> PlaylistMedia | None:
        """
        Fetch playlist information from YouTube and emit it to the client.

        Args:
            youtube_url (str): The YouTube URL of the playlist.
            user_browser_id (str): Unique identifier for the user's browser session.

        Returns:
            PlaylistMedia | None: The fetched playlist media object, or None if it fails.
        """
        socket_ctx = app.socket_manager.get_context(user_browser_id, self.namespace)

        app.logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)

        playlist_media_info_result = app.youtube_downloader.request_playlist_media_info(
            youtube_url
        )

        if playlist_media_info_result.is_error():
            app.logger.error("Failed to get playlist media info")
            return None

        app.logger.debug(f"Got playlist media info, processing emit {youtube_url}")

        playlist_media: PlaylistMedia = playlist_media_info_result.get_data()
        playlist_name = playlist_media.playlist_name

        flask_playlist_media = FlaskPlaylistMedia.init_from_playlist_media(
            playlist_name, playlist_media.media_from_playlist_list
        )

        app.logger.debug(f"Playlist name: {playlist_name} tracks: {len(playlist_media.media_from_playlist_list)}")
        app.logger.debug(f"Browser ID: {user_browser_id} for playlist emit")

        socket_ctx.emit(
            data=flask_playlist_media,
            emit_type=PlaylistMediaInfoEmit
        )

        return playlist_media

    def send_emit_media_finish_error(self, error_msg: str, user_browser_id: str) -> None:
        """
        Log an error message and emit a finish error event to the client.

        Args:
            error_msg (str): The error message to log and send.
            user_browser_id (str): Unique identifier for the user's browser session.
        """
        socket_ctx = app.socket_manager.get_context(user_browser_id, self.namespace)

        app.logger.warning(error_msg)

        socket_ctx.emit_error(
            error_msg=error_msg,
            emit_type=DownloadMediaFinishEmit
        )