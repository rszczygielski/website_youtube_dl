import os
from flask import render_template, send_file
from flask.views import MethodView
from flask import current_app as app

class IndexView(MethodView):
    """Render the main index page."""
    def get(self):
        return render_template('index.html')

class YoutubeView(MethodView):
    """Render the YouTube downloader interface."""
    def get(self):
        return render_template("youtube.html")

class ModifyPlaylistView(MethodView):
    """Render the playlist management interface."""
    def get(self):
        playlist_list = app.config_parser_manager.get_playlists()
        playlists_names = list(playlist_list.keys())
        app.logger.debug(f"Rendering modify_playlist.html with {len(playlists_names)} playlists")
        return render_template("modify_playlist.html", playlists_names=playlists_names)

class DownloadFileView(MethodView):
    """Serve the downloaded file to the user as an attachment."""

    def get(self, name):
        """
        Handle GET request to download a finalized media file.

        Args:
            name (str): The unique hash identifier generated during the
                        finalization of the download process.

        Returns:
            flask.Response: The file served as an attachment.
            tuple: A warning message and a 404 status code if the hash
                   is not found or expired.
        """
        session_download_data = app.socket_manager.get_session_data_by_hash(name)
        if not session_download_data:
            app.logger.warning(f"No session data for hash: {name}")
            return "File not found", 404

        full_path = os.path.join(
            session_download_data.file_directory_path,
            session_download_data.file_name
        )
        app.logger.info("Sending file as attachment")
        return send_file(full_path, as_attachment=True)