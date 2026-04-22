import os
from flask import send_file, render_template, Blueprint, request
from flask import current_app as app
from website_youtube_dl.flask_api.utils.general_funcions import get_format_instance
from website_youtube_dl.common.youtube_data_keys import MainYoutubeKeys
from website_youtube_dl.common.youtube_log_keys import YoutubeLogs
from .base_namespace import BaseMediaNamespace
from ..emits import DownloadMediaFinishEmit


# --- SocketIO Namespace Class ---
class YoutubeNamespace(BaseMediaNamespace):
    """Socket.IO Namespace handler for /youtube.

    This class manages real-time communication for single track and playlist
    downloads from YouTube. It inherits session and history management
    from BaseMediaNamespace.
    """

    def on_FormData(self, formData):
        """
        Main entry point for handling the download form submission.

        Extracts the URL and format from the incoming data, determines if it is
        a single track or a playlist, and routes the request to the appropriate handler.

        Args:
            formData (dict): Incoming data from the client containing 'url' and 'format'.
        """
        app.logger.debug(f"[{self.namespace}] Received FormData: {formData}")

        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)
        if not user_browser_id:
            return

        app.socket_manager.clear_user_data(user_browser_id)

        # Using the new private methods
        youtube_url = self._extract_youtube_url(formData, user_browser_id)
        request_format = self._extract_request_format(formData, user_browser_id)

        if not youtube_url or not request_format:
            return

        is_playlist = self._is_playlist_in_url(youtube_url)

        # Route to the appropriate download handler
        if is_playlist:
            self._handle_playlist_download(youtube_url,
                                           request_format,
                                           user_browser_id)
        else:
            self._handle_single_track_download(youtube_url,
                                               request_format,
                                               user_browser_id)

    def _extract_youtube_url(self, formData, user_browser_id):
        """
        Extracts and validates the YouTube URL from the incoming form data.
        Emits an error to the client if the URL is missing.

        Args:
            formData (dict): Incoming data from the client.
            user_browser_id (str): Unique identifier for the user's browser session.

        Returns:
            str | None: The extracted YouTube URL, or None if missing.
        """
        youtube_url = formData.get(MainYoutubeKeys.YOUTUBE_URL.value)
        if not youtube_url:
            app.logger.warning(YoutubeLogs.NO_URL.value)

            app.socket_manager.process_emit(
                data=YoutubeLogs.NO_URL.value,
                emit_type=DownloadMediaFinishEmit,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )
            return None

        return youtube_url

    def _extract_request_format(self, formData, user_browser_id):
        """
        Extracts and validates the requested download format from the form data.
        Emits an error to the client if the format is missing.

        Args:
            formData (dict): Incoming data from the client.
            user_browser_id (str): Unique identifier for the user's browser session.

        Returns:
            Format instance | None: The requested format object, or None if missing.
        """
        if MainYoutubeKeys.DOWNLOAD_TYP.value not in formData:
            app.logger.warning(YoutubeLogs.NO_FORMAT.value)

            app.socket_manager.process_emit(
                data=YoutubeLogs.NO_FORMAT.value,
                emit_type=DownloadMediaFinishEmit,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )
            return None

        format_type = formData[MainYoutubeKeys.DOWNLOAD_TYP.value]
        app.logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {format_type}")
        request_format = get_format_instance(format_type)
        return request_format

    @staticmethod
    def _is_playlist_in_url(youtube_url):
        """
        Determines if the provided URL belongs to a YouTube playlist rather than a single video.

        Args:
            youtube_url (str): The URL to evaluate.

        Returns:
            bool: True if it's a playlist, False otherwise.
        """
        if not youtube_url:
            return False
        return MainYoutubeKeys.URL_LIST.value in youtube_url and MainYoutubeKeys.URL_VIDEO.value not in youtube_url