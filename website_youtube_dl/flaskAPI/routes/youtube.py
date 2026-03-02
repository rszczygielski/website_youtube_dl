import os
from flask import send_file, render_template, Blueprint, request
from flask import current_app as app

from ...common.youtubeLogKeys import YoutubeLogs
from ..handlers.youtube_download import download_playlist_data, download_single_track_data
from ..handlers.youtube_utils import (
    extract_youtube_url, extract_request_format, is_playlist_in_url
)
from ..sockets.base_namespace import BaseMediaNamespace

# --- Blueprints for standard HTTP routes ---
youtube = Blueprint("youtube", __name__)

@youtube.route("/downloadFile/<name>")
def download_file(name):
    """Serve the downloaded file to the user as an attachment.

    Args:
        name (str): The unique hash identifying the file in the download registry.

    Returns:
        Response: The file as an attachment or a 404 error if not found.
    """
    session_download_data = app.socket_manager.get_session_data_by_hash(name)
    if not session_download_data:
        app.logger.warning(f"No session data for hash: {name}")
        return "File not found", 404

    full_path = os.path.join(
        session_download_data.file_directory_path,
        session_download_data.file_name
    )
    app.logger.info(YoutubeLogs.SENDING_TO_ATTACHMENT.value)
    return send_file(full_path, as_attachment=True)

@youtube.route("/youtube.html")
def youtube_html():
    """Render the YouTube downloader interface."""
    return render_template("youtube.html")

@youtube.route("/")
@youtube.route("/index.html")
def index():
    """Render the main index page."""
    return render_template('index.html')


# --- SocketIO Namespace Class ---
class YoutubeNamespace(BaseMediaNamespace):
    """Socket.IO Namespace handler for /youtube.

    This class manages real-time communication for single track and playlist
    downloads from YouTube. It inherits session and history management
    from BaseMediaNamespace.
    """

    def on_FormData(self, formData):
        """Handle the main download form submission via WebSocket.

        Processes the provided URL and format, triggers the appropriate
        download handler, and finalizes the download process by emitting
        the result back to the client.

        Args:
            formData (dict): Data from the client containing 'url' and 'format'.
        """
        app.logger.debug(f"[{self.namespace}] Received FormData: {formData}")

        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)
        if user_browser_id is None:
            app.logger.warning("No user browser id found for session")
            return

        # Prepare for a new process by clearing previous history
        app.socket_manager.clear_user_data(user_browser_id)

        youtube_url = extract_youtube_url(formData, user_browser_id, namespace=self.namespace)
        request_format = extract_request_format(formData, user_browser_id, namespace=self.namespace)

        if not youtube_url or not request_format:
            return

        is_playlist = is_playlist_in_url(youtube_url)
        app.logger.debug(f"Is playlist: {is_playlist}")

        # Execute physical file download
        if is_playlist:
            full_file_path = download_playlist_data(
                youtube_url, request_format, user_browser_id, self.namespace
            )
        else:
            full_file_path = download_single_track_data(
                youtube_url, request_format, user_browser_id, self.namespace
            )

        # Finalize download using base class method
        # This handles error reporting, hashing, and success emission
        self.finalize_download(full_file_path, is_playlist, user_browser_id)