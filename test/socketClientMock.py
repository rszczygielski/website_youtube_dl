from website_youtube_dl.flaskAPI.session import SessionClient


class SessionClientMock(SessionClient):
    sessionData = {}

    def __init__(self, session):
        super().__init__(session)

    def clearSession(self):
        pass

    def addElemtoSession(self, key, value):
        self.sessionData[key] = value

    def getSessionElem(self, key):
        return self.sessionData[key]

    def ifElemInSession(self, key):
        if key not in self.session.keys():
            return False
