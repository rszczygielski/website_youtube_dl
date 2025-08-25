from website_youtube_dl.flaskAPI.sessions.session import SessionClient


class SessionClientMock(SessionClient):
    session_data = {}

    def __init__(self, session):
        super().__init__(session)

    def clear_session(self):
        pass

    def add_elem_to_session(self, key, value):
        self.session_data[key] = value

    def get_session_elem(self, key):
        return self.session_data[key]

    def if_elem_in_session(self, key):
        if key not in self.session.keys():
            return False
