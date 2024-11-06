from website_youtube_dl.flaskAPI.session import SessionClient


class SessionClientMock(SessionClient):

    def __init__(self, session):
        super().__init__(session)

    def clearSession(self):
        pass

    def ifElemInSession(self, key):
        if key not in self.session.keys():
            return False
