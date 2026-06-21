import threading
import time
from flask import current_app as app
from ..sockets.session_data import DownloadFileInfo, UserMessage, BrowserSession

class UserSocketContext:
    """
    Facade (Adapter) for SocketManager binding operations to a specific
    user and namespace. Simplifies method calls in event handlers.
    """
    def __init__(self, manager: 'SocketManager', user_browser_id: str, namespace: str):
        self.manager = manager
        self.user_browser_id = user_browser_id
        self.namespace = namespace

    def emit(self, data, emit_type, add_to_queue=True):
        self.manager.process_emit(data, emit_type, self.user_browser_id, self.namespace, add_to_queue)

    def emit_error(self, error_msg, emit_type, add_to_queue=True):
        self.manager.process_emit_error(error_msg, emit_type, self.user_browser_id, self.namespace, add_to_queue)

    def set_downloading(self, is_downloading: bool):
        self.manager.set_downloading_status(self.user_browser_id, self.namespace, is_downloading)

    @property
    def is_downloading(self) -> bool:
        return self.manager.is_user_downloading(self.user_browser_id, self.namespace)

    def set_cancel_flag(self):
        self.manager.set_cancel_flag(self.user_browser_id, self.namespace)

    @property
    def is_cancelled(self) -> bool:
        return self.manager.is_cancelled(self.user_browser_id, self.namespace)

    def clear_cancel_flag(self):
        self.manager.clear_cancel_flag(self.user_browser_id, self.namespace)

    # Convenience methods for user data
    def get_messages(self):
        return self.manager.get_user_messages(self.user_browser_id)

    def clear_data(self):
        self.manager.clear_user_data(self.user_browser_id)


class SocketManager:
    """Manages Socket.IO connections, user message queues, and download states.

    This class serves as the Single Source of Truth (SSOT) for real-time client
    interactions. It handles:
    - Active WebSocket connections tracking
    - Event-driven session cleanup triggered by disconnections
    - User message queues for history and reconnection
    - Tracking active download states for accurate UI synchronization (State Machine)
    - Tracking and managing user-requested download cancellations
    - Download file registry mapping hashes to file metadata

    Attributes:
        SESSION_TIMEOUT (int): Delay in seconds before cleaning up a disconnected session.
        active_connections (dict): Maps user_browser_id to BrowserSession.
        message_queues (dict): Maps user_browser_id to a list of UserMessage objects.
        download_registry (dict): Maps generated hash to DownloadFileInfo.
        cancelled_downloads (set): Stores user_browser_ids of users who requested download cancellation.
        active_downloads (set): Stores user_browser_ids of users who currently have an active, ongoing download.
    """
    SESSION_TIMEOUT = 1800  # Testing value: 30 seconds

    def __init__(self):
        """Initialize SocketManager and prepare cleanup timer registry."""
        self.active_connections = {}
        self.message_queues = {}
        self.download_registry = {}
        self.cancelled_downloads = set()
        self._cleanup_timers = {}
        self.active_downloads = set()

    # ==========================================
    # PUBLIC METHODS (API for Namespaces)
    # ==========================================

    def process_emit(self, data, emit_type, user_browser_id: str, namespace: str, add_to_queue=True):
        """
        Process and send a successful Socket.IO emit to a specific user.

        Args:
            data (Any): The payload to send to the client.
            emit_type (Type): The class representing the specific emit event.
            user_browser_id (str): Unique identifier for the user's browser session.
            namespace (str): The Socket.IO namespace to broadcast on.
            add_to_queue (bool, optional): Whether to store this emit in the user's history queue. Defaults to True.
        """
        process_emit_type = emit_type()
        app.logger.debug(f'Processing emit {process_emit_type.emit_msg} for {user_browser_id}')

        if add_to_queue:
            self._add_msg_to_users_queue(user_browser_id, emit_type, data, namespace)

        self._update_activity_timestamp(user_browser_id)
        session_id = self._get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit(data, session_id, namespace)

    def process_emit_error(self, error_msg, emit_type, user_browser_id: str, namespace: str, add_to_queue=True):
        """
        Process and send an error Socket.IO emit to a specific user.

        Args:
            error_msg (str): The error message payload.
            emit_type (Type): The class representing the specific emit event.
            user_browser_id (str): Unique identifier for the user's browser session.
            namespace (str): The Socket.IO namespace to broadcast on.
            add_to_queue (bool, optional): Whether to store this error in the user's history queue. Defaults to True.
        """
        process_emit_type = emit_type()
        app.logger.debug(f'Processing error emit {process_emit_type.emit_msg} for {user_browser_id}')

        if add_to_queue:
            self._add_msg_to_users_queue(user_browser_id, emit_type, error_msg, namespace, is_error=True)

        self._update_activity_timestamp(user_browser_id)
        session_id = self._get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit_error(error_msg, session_id, namespace)

    def add_user_session(self, user_browser_id, session_id):
        """
        Register or update an active WebSocket connection for a user.

        Also cancels any pending cleanup timers if the user reconnects within the timeout window.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            session_id (str): The current Socket.IO session ID.
        """
        now = time.time()

        # If user reconnects, abort the deletion process
        self._cancel_cleanup_timer(user_browser_id)

        if user_browser_id in self.active_connections:
            app.logger.debug(f"Updating connection for user_browser_id: {user_browser_id}")

        self.active_connections[user_browser_id] = BrowserSession(
            session_id=session_id, last_activity_timestamp=now)

    def on_user_disconnect(self, user_browser_id):
        """
        Schedule a cleanup task when a user disconnects from the socket.

        This initiates a timer. If the user does not reconnect before SESSION_TIMEOUT expires,
        their queues and session data will be purged.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
        """
        if not user_browser_id:
            return

        # Cancel any existing timer before starting a new one
        self._cancel_cleanup_timer(user_browser_id)

        # Get the actual underlying app object to pass to the thread
        actual_app = app._get_current_object()

        app.logger.info(f"User {user_browser_id} disconnected. Cleanup scheduled in {self.SESSION_TIMEOUT}s")

        # Start a delayed thread to clean up session data, passing the app instance
        timer = threading.Timer(
            self.SESSION_TIMEOUT,
            self._cleanup_session,
            args=[user_browser_id, actual_app]
        )
        self._cleanup_timers[user_browser_id] = timer
        timer.start()

    def set_downloading_status(self, user_browser_id, namespace: str, is_downloading: bool):
        """
        Update the official downloading status for a specific user.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            namespace (str): The Socket.IO namespace to broadcast on.
            is_downloading (bool): True if a download has started, False if finished/cancelled.
        """
        if is_downloading:
            self.active_downloads.add((user_browser_id, namespace))
            app.logger.debug(f"User {user_browser_id} set to DOWNLOADING state in namespace {namespace}.")
        else:
            self.active_downloads.discard((user_browser_id, namespace))
            app.logger.debug(f"User {user_browser_id} set to IDLE state in namespace {namespace}.")

    def is_user_downloading(self, user_browser_id, namespace: str) -> bool:
        """
        Check if the user currently has an active download process running.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            namespace (str): The Socket.IO namespace to check.

        Returns:
            bool: True if downloading, False otherwise.
        """
        return (user_browser_id, namespace) in self.active_downloads

    def set_cancel_flag(self, user_browser_id, namespace: str):
        """
        Set the download cancellation flag for a specific user in a specific namespace.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            namespace (str): The Socket.IO namespace.
        """
        if user_browser_id:
            self.cancelled_downloads.add((user_browser_id, namespace))
            app.logger.info(f"Cancel flag set for user: {user_browser_id} in {namespace}")

    def is_cancelled(self, user_browser_id, namespace: str):
        """
        Check if the user has requested to cancel the ongoing download.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            namespace (str): The Socket.IO namespace to check.

        Returns:
            bool: True if a cancellation was requested, False otherwise.
        """
        return (user_browser_id, namespace) in self.cancelled_downloads

    def clear_cancel_flag(self, user_browser_id, namespace: str):
        """
        Clear the cancellation flag for a user (e.g., before starting a new download).

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            namespace (str): The Socket.IO namespace to clear the flag from.
        """
        self.cancelled_downloads.discard((user_browser_id, namespace))

    def get_user_messages(self, user_browser_id):
        """
        Retrieve all queued messages for a specific user.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.

        Returns:
            list[UserMessage]: A list of stored messages for the user. Returns an empty list if none exist.
        """
        return self.message_queues.get(user_browser_id, [])

    def clear_user_data(self, user_browser_id):
        """
        Clear all messages from a user's message queue.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
        """
        if user_browser_id in self.message_queues:
            self.message_queues[user_browser_id] = []
        app.logger.debug(f"Cleared user data for {user_browser_id}")

    def add_message_to_session_hash(self, generated_hash, download_file_info: DownloadFileInfo):
        """
        Store download file metadata in the registry mapped to a unique hash.

        Args:
            generated_hash (str): The unique identifier string for the download link.
            download_file_info (DownloadFileInfo): The object containing file path and playlist status.
        """
        self.download_registry[generated_hash] = download_file_info

    def get_session_data_by_hash(self, generated_hash):
        """
        Retrieve download file metadata from the registry using its hash.

        Args:
            generated_hash (str): The unique identifier string.

        Returns:
            DownloadFileInfo | None: The metadata object if found, None otherwise.
        """
        return self.download_registry.get(generated_hash, None)

    def get_user_browser_id_by_session(self, session_id):
        """
        Look up a user_browser_id associated with a specific Socket.IO session ID.

        Args:
            session_id (str): The Socket.IO session identifier.

        Returns:
            str | None: The matching user_browser_id, or None if not found.
        """
        for user_browser_id, session in self.active_connections.items():
            if session.session_id == session_id:
                return user_browser_id
        return None

    def get_context(self, user_browser_id: str, namespace: str) -> UserSocketContext:
        """
        Creates a bound context for a specific user and namespace.
        Use this in Namespace controllers to simplify API calls.
        """
        return UserSocketContext(self, user_browser_id, namespace)

    # ==========================================
    # PROTECTED METHODS
    # ==========================================

    def _get_session_id_by_user_browser_id(self, user_browser_id):
        """
        Retrieve the Socket.IO session ID for a given user.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.

        Returns:
            str | None: The session ID if active, None otherwise.
        """
        session = self.active_connections.get(user_browser_id, None)
        return session.session_id if session else None

    def _add_msg_to_users_queue(self, user_browser_id, emit_type, data, namespace, is_error=False):
        """
        Append a new message object to the user's history queue.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            emit_type (Type): The class representing the specific emit event.
            data (Any): The payload of the message.
            namespace (str): The relevant Socket.IO namespace.
            is_error (bool, optional): Indicates if the message is an error. Defaults to False.
        """
        if user_browser_id is None:
            app.logger.warning("Cannot add message to queue: user_browser_id is None")
            return

        app.logger.debug(f"Adding message to users queue for: {user_browser_id}")
        if user_browser_id not in self.message_queues:
            self.message_queues[user_browser_id] = []

        message = UserMessage(emit_type=emit_type, data=data, namespace=namespace, is_error=is_error)
        self.message_queues[user_browser_id].append(message)
        self._update_activity_timestamp(user_browser_id)

    def _update_activity_timestamp(self, user_browser_id):
        """
        Refresh the last activity timestamp for a user's active connection.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
        """
        if user_browser_id in self.active_connections:
            session = self.active_connections[user_browser_id]
            self.active_connections[user_browser_id] = BrowserSession(
                session_id=session.session_id,
                last_activity_timestamp=time.time())
        else:
            app.logger.warning(f"User {user_browser_id} not found in active connections.")

    def _cleanup_session(self, user_browser_id, app_instance):
        """
        Permanently remove session data, message queues, and timers for a disconnected user.

        Runs within the provided application context to safely access resources like the logger.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
            app_instance (Flask): The actual Flask application instance.
        """
        with app_instance.app_context():
            app_instance.logger.info(f"Cleanup triggered: Removing data for user_browser_id: {user_browser_id}")
            self.active_connections.pop(user_browser_id, None)
            self.message_queues.pop(user_browser_id, None)
            self._cleanup_timers.pop(user_browser_id, None)

            active_to_remove = [item for item in self.active_downloads if item[0] == user_browser_id]
            for item in active_to_remove:
                self.active_downloads.discard(item)

            cancelled_to_remove = [item for item in self.cancelled_downloads if item[0] == user_browser_id]
            for item in cancelled_to_remove:
                self.cancelled_downloads.discard(item)

    def _cancel_cleanup_timer(self, user_browser_id):
        """
        Abort a scheduled cleanup task for a user.

        Args:
            user_browser_id (str): Unique identifier for the user's browser session.
        """
        timer = self._cleanup_timers.get(user_browser_id)
        if timer:
            timer.cancel()
            self._cleanup_timers.pop(user_browser_id, None)
            app.logger.debug(f"Cleanup timer cancelled for user_browser_id: {user_browser_id}")