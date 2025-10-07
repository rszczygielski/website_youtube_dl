import threading
import time
import time
from flask import current_app as app
from ..sockets.session_data import DownloadFileInfo


# user_browser_id - lives longer so it should be the key


class SocketManager:
    SESSION_TIMEOUT = 1800

    def __init__(self):
        self.browser_sessions = {}
        self.user_session_data = {}
        self.session_data_by_hash = {}
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        def cleanup_loop():
            while True:
                now = time.time()
                to_remove = []
                for user_browser_id, (session_id, last_ts) in list(self.browser_sessions.items()):
                    if now - last_ts > self.SESSION_TIMEOUT:
                        to_remove.append(user_browser_id)
                for user_browser_id in to_remove:
                    self.browser_sessions.pop(user_browser_id, None)
                    self.user_session_data.pop(user_browser_id, None)
                time.sleep(60)
        t = threading.Thread(target=cleanup_loop, daemon=True)
        t.start()

    def __init__(self):
        self.browser_sessions = {}
        self.user_session_data = {}
        self.session_data_by_hash = {}

    def add_user_session(self, user_browser_id, session_id):
        now = time.time()
        if user_browser_id in self.browser_sessions:
            app.logger.debug(
                f"Updating session for user_browser_id: {user_browser_id}")
        self.browser_sessions[user_browser_id] = (session_id, now)

    def add_msg_to_users_queue(self, user_browser_id, emit_type, data):
        if user_browser_id not in self.user_session_data:
            self.user_session_data[user_browser_id] = []
        self.user_session_data[user_browser_id].append((emit_type, data))
        # update activity timestamp
        if user_browser_id in self.browser_sessions:
            session_id, _ = self.browser_sessions[user_browser_id]
            self.browser_sessions[user_browser_id] = (session_id, time.time())

    def get_user_messages(self, user_browser_id):
        return self.user_session_data.get(user_browser_id, [])

    def add_message_to_session_hash(self, genereted_hash, download_file_info: DownloadFileInfo):
        self.session_data_by_hash[genereted_hash] = download_file_info

    def get_session_data_by_hash(self, genereted_hash):
        return self.session_data_by_hash.get(genereted_hash, None)

    def get_user_browser_id_by_session(self, session_id):
        for user_browser_id, sessions in self.browser_sessions.items():
            if sessions[0] == session_id:
                return user_browser_id
        return None

    def get_session_id_by_user_browser_id(self, user_browser_id):
        return self.browser_sessions.get(user_browser_id, (None,))[0]

    def clear_user_data(self, user_browser_id):
        self.user_session_data[user_browser_id] = []

    # TODO unify those to methids into one
    def process_emit(self,
                     data,
                     emit_type,
                     user_browser_id: str):
        process_emit_type = emit_type()
        app.logger.debug(f'Processing emit {process_emit_type.emit_msg} for user_browser_id {user_browser_id}')
        self.add_msg_to_users_queue(user_browser_id, emit_type, data)
        session_id = self.get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit(data, session_id)

    def process_emit_error(self,
                     error_msg,
                     emit_type,
                     user_browser_id: str):
        process_emit_type = emit_type()
        app.logger.debug(f'Processing error emit {process_emit_type.emit_msg} for user_browser_id {user_browser_id}')
        self.add_msg_to_users_queue(user_browser_id, emit_type, error_msg)
        session_id = self.get_session_id_by_user_browser_id(user_browser_id)
        process_emit_type.send_emit_error(error_msg, session_id)
