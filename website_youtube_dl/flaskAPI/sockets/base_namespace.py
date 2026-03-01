from flask import request, current_app as app
from flask_socketio import Namespace
from ..utils.general_funcions import generate_hash
from .session_data import DownloadFileInfo
from ..handlers.youtube_emit import send_emit_media_finish_error
from ..sockets.emits import DownloadMediaFinishEmit

class BaseMediaNamespace(Namespace):
    """Base class handling shared Socket.IO logic across different namespaces.

    This class provides common event handlers for session management,
    message history retrieval, and a unified method for finalizing
    media downloads.
    """

    def on_userSession(self, data):
        """Map the Socket.IO session ID to a unique browser identifier.

        Args:
            data (dict): Contains 'userBrowserId' provided by the client.
        """
        user_browser_id = data["userBrowserId"]
        request_sid = request.sid
        app.socket_manager.add_user_session(user_browser_id, request_sid)
        app.logger.info(f"[{self.namespace}] Mapping {request_sid} -> {user_browser_id}")

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
            send_emit_media_finish_error(
                error_msg="Failed download - try again",
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )
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