import threading
import time
from flask import current_app as app
from ..sockets.session_data import DownloadFileInfo, UserMessage, BrowserSession




class SocketManager:
    """Manages Socket.IO connections, user message queues, and download file registry.
    
    This class handles:
    - Active WebSocket connections tracking with timeout management
    - User message queues for history and reconnection
    - Download file registry mapping hashes to file metadata
    
    Attributes:
        SESSION_TIMEOUT (int): Connection timeout in seconds (default: 1800 = 30 minutes).
        active_connections (dict): Maps user_browser_id to BrowserSession.
        message_queues (dict): Maps user_browser_id to list of UserMessage.
        download_registry (dict): Maps hash to DownloadFileInfo.
    """
    SESSION_TIMEOUT = 1800 # 30 minutes

    def __init__(self):
        """Initialize SocketManager and start cleanup thread."""
        self.active_connections = {}
        self.message_queues = {}
        self.download_registry = {}
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start background thread to clean up expired connections.
        
        The cleanup thread runs every 60 seconds and removes connections that have
        exceeded SESSION_TIMEOUT. This prevents memory leaks from stale connections.
        """
        def cleanup_loop():
            while True:
                now = time.time()
                to_remove = []
                for user_browser_id, session in list(self.active_connections.items()):
                    if now - session.last_activity_timestamp > self.SESSION_TIMEOUT:
                        to_remove.append(user_browser_id)
                        print(f"Connection timed out for user_browser_id: {user_browser_id}")
                for user_browser_id in to_remove:
                    print(f"Removing connection for user_browser_id: {user_browser_id}")
                    self.active_connections.pop(user_browser_id, None)
                    self.message_queues.pop(user_browser_id, None)
                time.sleep(60)
        t = threading.Thread(target=cleanup_loop, daemon=True)
        t.start()

    def add_user_session(self, user_browser_id, session_id):
        """Add or update a user's active connection.
        
        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            session_id (str): Socket.IO session ID.
        """
        now = time.time()
        if user_browser_id in self.active_connections:
            app.logger.debug(
                f"Updating connection for user_browser_id: {user_browser_id}")
        self.active_connections[user_browser_id] = BrowserSession(
            session_id=session_id, last_activity_timestamp=now)

    def add_msg_to_users_queue(self, user_browser_id, emit_type, data, is_error=False):
        """Add a message to user's message queue for history and reconnection.
        
        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            emit_type (Type): The emit type class (e.g., DownloadMediaFinishEmit).
            data (Any): The data to be stored with the message.
            is_error (bool): Whether this message represents an error. Defaults to False.
            
        Returns:
            None: Returns None if user_browser_id is None (logs warning).
            
        Note:
            This method also updates the activity timestamp for the user connection.
        """
        if user_browser_id is None:
            app.logger.warning("Cannot add message to queue: user_browser_id is None")
            return None
        app.logger.debug(f"Adding message to users queue for user_browser_id: {user_browser_id}")
        if user_browser_id not in self.message_queues:
            self.message_queues[user_browser_id] = []
        message = UserMessage(emit_type=emit_type, data=data, is_error=is_error)
        self.message_queues[user_browser_id].append(message)
        # update activity timestamp
        self.update_activity_timestamp(user_browser_id)

    def update_activity_timestamp(self, user_browser_id):
        """Update the last activity timestamp for a user connection.
        
        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            
        Note:
            Logs a warning if the user_browser_id is not found in active connections.
        """
        if user_browser_id in self.active_connections:
            session = self.active_connections[user_browser_id]
            self.active_connections[user_browser_id] = BrowserSession(
                session_id=session.session_id, 
                last_activity_timestamp=time.time())
            app.logger.debug(f"Updated activity timestamp for user_browser_id: {user_browser_id}")
        else:
            app.logger.warning(f"User browser ID {user_browser_id} not found in active connections.")

    def get_user_messages(self, user_browser_id):
        """Get all messages in user's message queue.
        
        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            
        Returns:
            list[UserMessage]: List of UserMessage objects for the user.
                Returns empty list if user_browser_id not found.
        """
        return self.message_queues.get(user_browser_id, [])

    def add_message_to_session_hash(self, genereted_hash, download_file_info: DownloadFileInfo):
        """Store download file information in download registry by hash.
        
        Args:
            genereted_hash (str): Unique hash identifier for the download.
            download_file_info (DownloadFileInfo): File information to store.
        """
        self.download_registry[genereted_hash] = download_file_info

    def get_session_data_by_hash(self, genereted_hash):
        """Retrieve download file information from download registry by hash.
        
        Args:
            genereted_hash (str): Unique hash identifier for the download.
            
        Returns:
            DownloadFileInfo | None: Download file information if found, None otherwise.
        """
        return self.download_registry.get(genereted_hash, None)

    def get_user_browser_id_by_session(self, session_id):
        """Get user_browser_id from Socket.IO session_id.
        
        Args:
            session_id (str): Socket.IO session ID.
            
        Returns:
            str | None: user_browser_id if found, None otherwise.
        """
        for user_browser_id, session in self.active_connections.items():
            if session.session_id == session_id:
                return user_browser_id
        return None

    def get_session_id_by_user_browser_id(self, user_browser_id):
        """Get Socket.IO session_id from user_browser_id.
        
        Args:
            user_browser_id (str): Unique identifier for the user's browser.
            
        Returns:
            str | None: Socket.IO session_id if found, None otherwise.
        """
        session = self.active_connections.get(user_browser_id, None)
        return session.session_id if session else None

    def clear_user_data(self, user_browser_id):
        """Clear all messages from user's message queue.
        
        Args:
            user_browser_id (str): Unique identifier for the user's browser.
        """
        self.message_queues[user_browser_id] = []
        app.logger.debug(f"Cleared user data for {user_browser_id}")

    def process_emit(self,
                     data,
                     emit_type,
                     user_browser_id: str,
                     add_to_queue=True):
        """Process and send a Socket.IO emit to the user.
        
        Args:
            data (Any): Data to be sent with the emit.
            emit_type (Type): The emit type class (e.g., DownloadMediaFinishEmit).
            user_browser_id (str): Unique identifier for the user's browser.
            add_to_queue (bool): Whether to add message to user's queue for history.
                Defaults to True.
        """
        process_emit_type = emit_type()
        app.logger.debug(f'Processing emit {process_emit_type.emit_msg} for user_browser_id {user_browser_id}')
        if add_to_queue:
            self.add_msg_to_users_queue(user_browser_id, emit_type, data)
        self.update_activity_timestamp(user_browser_id)
        session_id = self.get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit(data, session_id)

    def process_emit_error(self,
                     error_msg,
                     emit_type,
                     user_browser_id: str,
                     add_to_queue=True):
        """Process and send a Socket.IO error emit to the user.
        
        Args:
            error_msg (str): Error message to be sent.
            emit_type (Type): The emit type class (e.g., DownloadMediaFinishEmit).
            user_browser_id (str): Unique identifier for the user's browser.
            add_to_queue (bool): Whether to add error message to user's queue for history.
                Defaults to True.
        """
        process_emit_type = emit_type()
        app.logger.debug(f'Processing error emit {process_emit_type.emit_msg} for user_browser_id {user_browser_id}')
        if add_to_queue:
            self.add_msg_to_users_queue(user_browser_id, emit_type, error_msg, is_error=True)
        self.update_activity_timestamp(user_browser_id)
        session_id = self.get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit_error(error_msg, session_id)

