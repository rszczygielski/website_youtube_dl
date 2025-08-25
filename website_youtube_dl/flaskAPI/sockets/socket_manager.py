class SocketManager:

    def __init__(self):
        self.user_sessions = {}
        self.user_session_data = {}
        self.hash_to_session_data = {}

    def add_user_session(self, user_browser_id, session_id):
        self.user_sessions[user_browser_id] = session_id

    def get_user_session(self, user_browser_id):
        return self.user_sessions.get(user_browser_id)

    def get_browser_id_by_session(self, session_id):
        for browser_id, sess_id in self.user_sessions.items():
            if sess_id == session_id:
                return browser_id
        return None

    def remove_user_session(self, user_browser_id):
        if user_browser_id in self.user_sessions:
            del self.user_sessions[user_browser_id]

    def has_user_session(self, user_browser_id: str) -> bool:
        return user_browser_id in self.user_sessions

    def get_all_user_sessions(self):
        return list(self.user_sessions.keys())

    def add_msg_to_users_queue(self,
                               user_browser_id: str,
                               hash: str,
                               session_download_data):
        if user_browser_id not in self.user_session_data:
            self.user_session_data[user_browser_id] = {}
        if hash not in self.user_session_data[user_browser_id]:
            self.user_session_data[user_browser_id][hash] = []
        self.user_session_data[user_browser_id][hash].append(
            session_download_data)

        if hash not in self.hash_to_session_data:
            self.hash_to_session_data[hash] = []
        self.hash_to_session_data[hash].append(session_download_data)

    def get_user_session_data(self, user_browser_id: str):
        return self.user_session_data.get(user_browser_id, {})

    def clear_user_session_data(self, user_browser_id: str):
        if user_browser_id in self.user_session_data:
            self.user_session_data.pop(user_browser_id, None)

    def clear_user_msg_queue(self, user_browser_id: str):
        if user_browser_id in self.user_session_data:
            self.user_session_data[user_browser_id] = []

    def clear_all_sessions(self):
        self.user_sessions.clear()
        self.user_session_data.clear()

    def get_session_data_by_hash(self, hash: str):
        return self.hash_to_session_data.get(hash)

    def remove_session_data_by_hash(self, hash: str):
        self.hash_to_session_data.pop(hash, None)

    def process_emit(self,
                     data,
                     emit_type,
                     user_browser_id: str):
        process_emit_type = emit_type()
        process_emit_type.send_emit(data, user_browser_id)
