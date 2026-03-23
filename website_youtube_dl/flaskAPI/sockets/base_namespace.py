from flask import request, current_app as app
from flask_socketio import Namespace
from ..utils.general_funcions import generate_hash, get_files_from_dir
from .session_data import DownloadFileInfo
from ..sockets.emits import DownloadMediaFinishEmit, PlaylistTrackFinish
from ..sockets.youtube_media_info_handler import YoutubeMediaInfoHandler
from ..services.flask_youtube_downloader import FlaskYoutubeDownloader

class BaseMediaNamespace(Namespace):
    """Base class handling shared Socket.IO logic across different namespaces.

    This class provides common event handlers for session management,
    message history retrieval, and a unified method for finalizing
    media downloads. It also triggers session cleanup on disconnect.
    """

    def __init__(self, namespace=None):
        """
        Initialize the namespace and its associated services.

        Args:
            namespace (str, optional): The Socket.IO namespace (e.g., '/youtube', '/playlist').
        """
        super().__init__(namespace)  # Initialize the base Namespace class from Flask-SocketIO

        # Create service instances once at the base class level.
        # InfoHandler receives the target namespace when this instance is created.
        self.info_handler = YoutubeMediaInfoHandler(namespace=self.namespace)
        self.downloader = FlaskYoutubeDownloader()

    def on_userSession(self, data):
        """Map the Socket.IO session ID to a unique browser identifier.

        Args:
            data (dict): Contains 'userBrowserId' provided by the client.
        """
        user_browser_id = data["userBrowserId"]
        request_sid = request.sid
        app.socket_manager.add_user_session(user_browser_id, request_sid)
        app.logger.info(f"[{self.namespace}] Mapping {request_sid} -> {user_browser_id}")

    def on_disconnect(self):
        """Handle WebSocket disconnection by scheduling a session cleanup.

        Retrieves the browser ID associated with the current session and
        notifies the SocketManager to start the expiration timer.
        """
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)
        if user_browser_id:
            app.logger.info(f"[{self.namespace}] User {user_browser_id} disconnected")
            app.socket_manager.on_user_disconnect(user_browser_id)

    def on_getHistory(self, data):
        """Retrieve and replay the message history for a specific user.

        Filters messages by the current namespace to ensure users only receive
        relevant history for the page they are on.

        Args:
            data (dict): Contains 'userBrowserId'.
        """
        user_browser_id = data.get("userBrowserId")
        user_data = app.socket_manager.get_user_messages(user_browser_id)

        for message in user_data:
            # Only replay messages belonging to the current namespace
            if message.namespace != self.namespace:
                continue

            if message.is_error:
                app.socket_manager.process_emit_error(
                    error_msg=message.data,
                    emit_type=message.emit_type,
                    user_browser_id=user_browser_id,
                    add_to_queue=False,
                    namespace=self.namespace
                )
            else:
                app.socket_manager.process_emit(
                    data=message.data,
                    emit_type=message.emit_type,
                    user_browser_id=user_browser_id,
                    add_to_queue=False,
                    namespace=self.namespace
                )


    def _handle_playlist_download(self,
                                  youtube_url,
                                  request_format,
                                  user_browser_id):
        """
        Orchestrates the process of downloading an entire playlist.
        """
        # 1. Fetch playlist information and emit the initial data to the frontend
        playlist_media = self.info_handler.send_emit_playlist_media(youtube_url, user_browser_id)
        if not playlist_media:
            self.info_handler.send_emit_media_finish_error(f"Failed to get data from {youtube_url}", user_browser_id)
            return

        file_paths = []
        directory_path = app.config_parser_manager.get_save_path()
        downloaded_files = get_files_from_dir(directory_path)

        # 2. Iterate through the tracks, download them, and emit status updates
        for index, playlistTrack in enumerate(playlist_media.media_from_playlist_list):
            full_path, title_template = self.downloader.process_playlist_track(
                playlistTrack=playlistTrack,
                req_format=request_format,
                playlist_name=playlist_media.playlist_name,
                index=index,
                downloaded_files=downloaded_files
            )

            if full_path:
                file_paths.append(full_path)
                downloaded_files.append(title_template)

                app.socket_manager.process_emit(
                    data=index,
                    emit_type=PlaylistTrackFinish,
                    user_browser_id=user_browser_id,
                    namespace=self.namespace
                )
            else:
                app.logger.error(f"{playlistTrack.title} song not downloaded")

                app.socket_manager.process_emit_error(
                    error_msg=index,
                    emit_type=PlaylistTrackFinish,
                    user_browser_id=user_browser_id,
                    namespace=self.namespace
                )

        # 3. Zip all files after the loop finishes successfully
        full_zip_path = self.downloader.zip_downloaded_playlist(
            directory_path, playlist_media.playlist_name, file_paths
        )

        # 4. Finalize the download process and provide the download link
        self.finalize_download(full_zip_path, is_playlist=True, user_browser_id=user_browser_id)

    def _handle_single_track_download(self,
                                      youtube_url,
                                      request_format,
                                      user_browser_id):
        """
        Orchestrates the process of downloading a single track.
        """
        if not self.info_handler.send_emit_single_media_info_from_youtube(youtube_url, user_browser_id):
            return

        full_file_path = self.downloader.download_single_track_data(youtube_url, request_format)

        self.finalize_download(full_file_path, is_playlist=False, user_browser_id=user_browser_id)

    def finalize_download(self, full_file_path, is_playlist, user_browser_id):
        """Finalize the download process by registering the file and notifying the client.

        Generates a unique download hash, stores file metadata in the registry,
        and emits a finish event. Clears user history upon successful completion.

        Args:
            full_file_path (str | None): Absolute path to the downloaded file.
            is_playlist (bool): Whether the download was a playlist.
            user_browser_id (str): Unique identifier for the user's browser.
        """
        if not full_file_path:
            app.logger.error(f"[{self.namespace}] No file path returned - download failed")

            app.socket_manager.process_emit_error(error_msg="Failed download - try again",
                                        emit_type=DownloadMediaFinishEmit,
                                        user_browser_id=user_browser_id,
                                        namespace=self.namespace)
            return

        # Register file for the download endpoint
        generated_hash = generate_hash()
        app.socket_manager.add_message_to_session_hash(
            generated_hash,
            DownloadFileInfo(full_file_path, is_playlist)
        )

        # Notify client with the download hash
        app.socket_manager.process_emit(
            data=generated_hash,
            emit_type=DownloadMediaFinishEmit,
            user_browser_id=user_browser_id,
            namespace=self.namespace
        )

        # Clear session history after successful finalize
        app.socket_manager.clear_user_data(user_browser_id)