import threading
import time
from flask import current_app as app
from ..sockets.session_data import DownloadFileInfo, UserMessage, BrowserSession

class SocketManager:
    """Manages Socket.IO connections, user message queues, and download file registry.

    This class handles:
    - Active WebSocket connections tracking
    - Event-driven session cleanup triggered by disconnections
    - User message queues for history and reconnection
    - Download file registry mapping hashes to file metadata

    Attributes:
        SESSION_TIMEOUT (int): Delay in seconds before cleaning up a disconnected session.
        active_connections (dict): Maps user_browser_id to BrowserSession.
        message_queues (dict): Maps user_browser_id to list of UserMessage.
        download_registry (dict): Maps hash to DownloadFileInfo.
    """
    SESSION_TIMEOUT = 1800  # Testing value: 30 seconds

    def __init__(self):
        """Initialize SocketManager and prepare cleanup timer registry."""
        self.active_connections = {}
        self.message_queues = {}
        self.download_registry = {}
        # Stores active threading.Timer objects mapped to user_browser_id
        self._cleanup_timers = {}

    def _cleanup_session(self, user_browser_id, app_instance):
        """Permanently remove session data and message queues for a user.

        Runs within the application context to allow safe access to app resources
        like the logger from a background thread.

        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            app_instance (Flask): The actual Flask application instance.
        """
        with app_instance.app_context():
            app_instance.logger.info(f"Cleanup triggered: Removing data for user_browser_id: {user_browser_id}")
            self.active_connections.pop(user_browser_id, None)
            self.message_queues.pop(user_browser_id, None)
            self._cleanup_timers.pop(user_browser_id, None)

    def on_user_disconnect(self, user_browser_id):
        """Schedule a cleanup task when a user disconnects from the socket.

        Args:
            user_browser_id (str): Unique identifier for the user's browser.
        """
        if not user_browser_id:
            return

        # Cancel any existing timer before starting a new one
        self.cancel_cleanup_timer(user_browser_id)

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

    def cancel_cleanup_timer(self, user_browser_id):
        """Cancel the scheduled cleanup if the user reconnects before the timeout.

        Args:
            user_browser_id (str): Unique identifier for the user's browser.
        """
        timer = self._cleanup_timers.get(user_browser_id)
        if timer:
            timer.cancel()
            self._cleanup_timers.pop(user_browser_id, None)
            app.logger.debug(f"Cleanup timer cancelled for user_browser_id: {user_browser_id}")

    def add_user_session(self, user_browser_id, session_id):
        """Add or update a user's active connection and cancel pending cleanup.

        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            session_id (str): Socket.IO session ID.
        """
        now = time.time()

        # If user reconnects, abort the deletion process
        self.cancel_cleanup_timer(user_browser_id)

        if user_browser_id in self.active_connections:
            app.logger.debug(f"Updating connection for user_browser_id: {user_browser_id}")

        self.active_connections[user_browser_id] = BrowserSession(
            session_id=session_id, last_activity_timestamp=now)

    def add_msg_to_users_queue(self, user_browser_id, emit_type, data, namespace, is_error=False):
        """Add a message to user's message queue for history and reconnection.

        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            emit_type (Type): The emit type class.
            data (Any): The data to be stored.
            namespace (str): The namespace for the event.
            is_error (bool): Whether this message represents an error.
        """
        if user_browser_id is None:
            app.logger.warning("Cannot add message to queue: user_browser_id is None")
            return

        app.logger.debug(f"Adding message to users queue for: {user_browser_id}")
        if user_browser_id not in self.message_queues:
            self.message_queues[user_browser_id] = []

        message = UserMessage(emit_type=emit_type, data=data, namespace=namespace, is_error=is_error)
        self.message_queues[user_browser_id].append(message)
        self.update_activity_timestamp(user_browser_id)

    def update_activity_timestamp(self, user_browser_id):
        """Update the last activity timestamp for a user connection."""
        if user_browser_id in self.active_connections:
            session = self.active_connections[user_browser_id]
            self.active_connections[user_browser_id] = BrowserSession(
                session_id=session.session_id,
                last_activity_timestamp=time.time())
        else:
            app.logger.warning(f"User {user_browser_id} not found in active connections.")

    def get_user_messages(self, user_browser_id):
        """Get all messages in user's message queue."""
        return self.message_queues.get(user_browser_id, [])

    def add_message_to_session_hash(self, generated_hash, download_file_info: DownloadFileInfo):
        """Store download file information in registry by hash."""
        self.download_registry[generated_hash] = download_file_info

    def get_session_data_by_hash(self, generated_hash):
        """Retrieve download file information from registry by hash."""
        return self.download_registry.get(generated_hash, None)

    def get_user_browser_id_by_session(self, session_id):
        """Get user_browser_id from Socket.IO session_id."""
        for user_browser_id, session in self.active_connections.items():
            if session.session_id == session_id:
                return user_browser_id
        return None

    def get_session_id_by_user_browser_id(self, user_browser_id):
        """Get Socket.IO session_id from user_browser_id."""
        session = self.active_connections.get(user_browser_id, None)
        return session.session_id if session else None

    def clear_user_data(self, user_browser_id):
        """Clear all messages from user's message queue."""
        if user_browser_id in self.message_queues:
            self.message_queues[user_browser_id] = []
        app.logger.debug(f"Cleared user data for {user_browser_id}")

    def process_emit(self, data, emit_type, user_browser_id: str, namespace: str, add_to_queue=True):
        """Process and send a Socket.IO emit to the user."""
        process_emit_type = emit_type()
        app.logger.debug(f'Processing emit {process_emit_type.emit_msg} for {user_browser_id}')

        if add_to_queue:
            self.add_msg_to_users_queue(user_browser_id, emit_type, data, namespace)

        self.update_activity_timestamp(user_browser_id)
        session_id = self.get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit(data, session_id, namespace)

    def process_emit_error(self, error_msg, emit_type, user_browser_id: str, namespace: str, add_to_queue=True):
        """Process and send a Socket.IO error emit to the user."""
        process_emit_type = emit_type()
        app.logger.debug(f'Processing error emit {process_emit_type.emit_msg} for {user_browser_id}')

        if add_to_queue:
            self.add_msg_to_users_queue(user_browser_id, emit_type, error_msg, namespace, is_error=True)

        self.update_activity_timestamp(user_browser_id)
        session_id = self.get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit_error(error_msg, session_id, namespace)