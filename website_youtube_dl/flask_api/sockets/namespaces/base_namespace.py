from abc import ABC
from flask import request, current_app as app
from flask_socketio import Namespace
from website_youtube_dl.flask_api.utils.general_funcions import generate_hash, get_files_from_dir
from ..session_data import DownloadFileInfo
from ..emits import DownloadMediaFinishEmit, PlaylistTrackFinish
from ..youtube_media_info_handler import YoutubeMediaInfoHandler

class SessionBaseNamespace(Namespace, ABC):
    """Base class handling core Socket.IO infrastructure and session management.

    This class provides common event handlers for mapping user sessions,
    retrieving message history, processing download cancellations, and
    triggering session cleanup upon disconnection. It is strictly limited
    to connection lifecycle management and is completely decoupled from
    any media or business logic.

    As an Abstract Base Class (ABC), it cannot be instantiated directly.
    """

    def __init__(self, namespace=None):
        """
        Initialize the namespace and its associated services.

        Args:
            namespace (str, optional): The Socket.IO namespace (e.g., '/youtube', '/playlist').
        """
        super().__init__(namespace)  # Initialize the base Namespace class from Flask-SocketIO

    # ==========================================
    # PUBLIC METHODS (Event Handlers & API)
    # ==========================================

    def on_userSession(self, data):
        """
        Map the Socket.IO session ID to a unique browser identifier.

        This event is triggered when a client connects. It registers the user's
        browser ID with their current WebSocket session ID (`request.sid`) in the
        SocketManager to ensure messages are routed correctly across reconnections.

        Args:
            data (dict): A dictionary containing the 'userBrowserId' provided by the client.
        """
        user_browser_id = data["userBrowserId"]
        request_sid = request.sid
        app.socket_manager.add_user_session(user_browser_id, request_sid)
        app.logger.info(f"[{self.namespace}] Mapping {request_sid} -> {user_browser_id}")

    def on_getHistory(self, data):
        """
        Retrieve and replay the message history for a specific user session.

        This method fetches all previously emitted messages for the user from the
        SocketManager and resends them to the client. It strictly filters messages
        by the current namespace to ensure users only see relevant UI updates for
        the page they are currently viewing.

        Args:
            data (dict): A dictionary containing the 'userBrowserId' provided by the client.
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

    def on_getDownloadState(self, data):
        """
        Retrieve the current download state for a specific user session.

        This method acts as a dedicated endpoint to query the State Machine
        (SocketManager) and determine if the user currently has an active
        download process running. The returned value triggers an acknowledgment
        callback on the client side to lock or unlock the UI accordingly.

        Args:
            data (dict): A dictionary containing the 'userBrowserId' provided by the client.

        Returns:
            dict: A dictionary with a single key 'isDownloading' mapping to a boolean
                  indicating the user's current download status.
        """
        user_browser_id = data.get("userBrowserId")
        is_active = app.socket_manager.is_user_downloading(user_browser_id, self.namespace)
        return {"isDownloading": is_active}

    def on_cancelDownload(self, data):
        """
        Handle a download cancellation request from the client.

        Retrieves the unique browser ID from the incoming data and sets the
        cancellation flag in the SocketManager to stop the ongoing process.

        Args:
            data (dict): Contains 'userBrowserId' provided by the client.
        """
        user_browser_id = data.get("userBrowserId")
        if user_browser_id:
            app.logger.info(f"[{self.namespace}] User {user_browser_id} requested download cancellation.")
            app.socket_manager.set_cancel_flag(user_browser_id, self.namespace)

    def on_disconnect(self):
        """
        Handle WebSocket disconnection by scheduling a session cleanup.

        When a client disconnects, this method retrieves the associated browser ID
        and notifies the SocketManager. The manager will start a countdown timer
        to purge the user's history and session data if they do not reconnect in time.
        """
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)
        if user_browser_id:
            app.logger.info(f"[{self.namespace}] User {user_browser_id} disconnected")
            app.socket_manager.on_user_disconnect(user_browser_id)

class MediaBaseNamespace(SessionBaseNamespace):
    """Intermediate base class orchestrating media downloading processes.

    Inherits core session management from SessionBaseNamespace and integrates
    business logic services such as media information fetching and file downloading.
    It provides the foundational methods needed to handle the end-to-end flow
    of processing single tracks and playlists.

    As it inherits from an Abstract Base Class, it cannot be instantiated directly.
    """

    def __init__(self, namespace=None):
        super().__init__(namespace)

        # Create service instances once at the base class level.
        # InfoHandler receives the target namespace when this instance is created.
        self.info_handler = YoutubeMediaInfoHandler(namespace=self.namespace)

    def finalize_download(self, full_file_path, is_playlist, user_browser_id):
        """
        Finalize the download process by registering the file and notifying the client.

        Generates a unique download hash, stores file metadata in the registry,
        and emits a finish event. Clears user history upon successful completion.

        Args:
            full_file_path (str | None): Absolute path to the downloaded file.
            is_playlist (bool): Whether the download was a playlist.
            user_browser_id (str): Unique identifier for the user's browser.
        """
        if not full_file_path:
            app.logger.error(f"[{self.namespace}] No file path returned - download failed")

            app.socket_manager.process_emit_error(
                error_msg="Failed download - try again",
                emit_type=DownloadMediaFinishEmit,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )
            # Release the lock if finalization failed
            app.socket_manager.set_downloading_status(user_browser_id, False, self.namespace)
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

        # [STATE MACHINE] Release the lock - download is successfully completed
        app.socket_manager.set_downloading_status(user_browser_id, False, self.namespace)

        # Clear session history after successful finalize
        app.socket_manager.clear_user_data(user_browser_id)

    # ==========================================
    # PROTECTED METHODS
    # ==========================================

    def _handle_playlist_download(self,
                                  youtube_url,
                                  request_format,
                                  user_browser_id):
        """
        Orchestrate the end-to-end process of downloading an entire playlist.

        This method fetches the playlist metadata, iterates through each track
        to download it, checks for user cancellation, emits real-time progress,
        compresses the downloaded files into a ZIP archive, and triggers finalization.

        Args:
            youtube_url (str): The URL of the YouTube playlist to download.
            request_format (Format): The requested media format object (e.g., FormatMP3).
            user_browser_id (str): The unique identifier for the user's browser session.
        """

        # [STATE MACHINE] Lock the session - download started
        app.socket_manager.set_downloading_status(user_browser_id, True, self.namespace)

        # Always clear the cancel flag at the start of a new download
        app.socket_manager.clear_cancel_flag(user_browser_id, self.namespace)

        # Fetch playlist information and emit the initial data to the frontend
        playlist_media = self.info_handler.send_emit_playlist_media(youtube_url, user_browser_id)
        if not playlist_media:
            self.info_handler.send_emit_media_finish_error(f"Failed to get data from {youtube_url}", user_browser_id)
            app.socket_manager.set_downloading_status(user_browser_id, False, self.namespace)
            return

        file_paths = []
        directory_path = app.config_parser_manager.get_save_path()
        downloaded_files = get_files_from_dir(directory_path)

        # Iterate through the tracks, download them, and emit status updates
        for index, playlistTrack in enumerate(playlist_media.media_from_playlist_list):

            # Check if the user requested to cancel the download
            if app.socket_manager.is_cancelled(user_browser_id, self.namespace):
                self._process_download_cancellation(user_browser_id)
                return  # Abort the loop and the entire method immediately

            # Download the single track
            full_path, title_template = app.youtube_downloader.process_playlist_track(
                playlistTrack=playlistTrack,
                req_format=request_format,
                playlist_name=playlist_media.playlist_name,
                index=index,
                downloaded_files=downloaded_files
            )

            # Process result and emit status via helper method
            if full_path:
                file_paths.append(full_path)
                downloaded_files.append(title_template)
                self._emit_track_download_status(
                    index=index,
                    is_success=True,
                    track_title=playlistTrack.title,
                    user_browser_id=user_browser_id
                    )
            else:
                self._emit_track_download_status(
                    index=index,
                    is_success=False,
                    track_title=playlistTrack.title,
                    user_browser_id=user_browser_id
                )

        # Zip all files after the loop finishes successfully (if not cancelled)
        full_zip_path = app.youtube_downloader.zip_downloaded_playlist(
            directory_path, playlist_media.playlist_name, file_paths
        )

        # Finalize the download process and provide the download link
        self.finalize_download(full_zip_path, is_playlist=True, user_browser_id=user_browser_id)

    def _handle_single_track_download(self,
                                      youtube_url,
                                      request_format,
                                      user_browser_id):
        """
        Orchestrate the end-to-end process of downloading a single media track.

        This method fetches the media metadata, initiates the physical download
        of the requested video or audio file, and hands over the resulting file
        path to the finalization method to notify the client.

        Args:
            youtube_url (str): The URL of the specific YouTube video to download.
            request_format (Format): The requested media format object (e.g., FormatMP3).
            user_browser_id (str): The unique identifier for the user's browser session.
        """
        # [STATE MACHINE] Lock the session - download started
        app.socket_manager.set_downloading_status(user_browser_id, True, self.namespace)

        if not self.info_handler.send_emit_single_media_info_from_youtube(youtube_url, user_browser_id):
            app.socket_manager.set_downloading_status(user_browser_id, False, self.namespace)
            return

        full_file_path = app.youtube_downloader.download_single_track(youtube_url, request_format)

        self.finalize_download(full_file_path, is_playlist=False, user_browser_id=user_browser_id)

    def _process_download_cancellation(self, user_browser_id):
        """
        Process the cancellation of an ongoing download.

        Logs the cancellation, emits an error event to the client to update the UI,
        and clears the cancellation flag in the SocketManager.

        Args:
            user_browser_id (str): The unique identifier for the user's browser session.
        """
        app.logger.warning(f"[{self.namespace}] Playlist download cancelled by user {user_browser_id}.")

        app.socket_manager.process_emit_error(
            error_msg="Download cancelled by user.",
            emit_type=DownloadMediaFinishEmit,
            user_browser_id=user_browser_id,
            namespace=self.namespace
        )

        # [STATE MACHINE] Release the lock - download is aborted
        app.socket_manager.set_downloading_status(user_browser_id, False, self.namespace)

        # Clear history upon cancellation so the UI resets completely
        app.socket_manager.clear_user_data(user_browser_id)

        # Clean up the flag after successfully catching the cancellation
        app.socket_manager.clear_cancel_flag(user_browser_id, self.namespace)

    def _emit_track_download_status(self, index, is_success, track_title, user_browser_id):
        """
        Emit the success or error status of a single track download to the client.

        Args:
            index (int): The index of the track in the playlist.
            is_success (bool): Whether the download was successful.
            track_title (str): The title of the track (used for logging errors).
            user_browser_id (str): The unique identifier for the user's browser session.
        """
        if is_success:
            app.socket_manager.process_emit(
                data=index,
                emit_type=PlaylistTrackFinish,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )
        else:
            app.logger.error(f"{track_title} song not downloaded")
            app.socket_manager.process_emit_error(
                error_msg=index,
                emit_type=PlaylistTrackFinish,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )