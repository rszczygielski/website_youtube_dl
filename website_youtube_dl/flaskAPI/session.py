from flask import current_app as app


class SessionClient():

    def __init__(self, session):
        self.session = session

    def addElemtoSession(self, key, value):
        self.session[key] = value

    def deleteElemFormSession(self, key):
        self.checkIfElemInSession(key)
        self.session.pop(key)

    def checkIfElemInSession(self, key):
        if key not in self.session.keys():
            app.logger.error(f"Session doesn't have a key: {key}")
            return "test"

    def getSessionElem(self, key):
        self.checkIfElemInSession(key)
        return self.session[key]

    def printSessionKeys(self):
        app.logger.info(self.session.keys())

    def clearSession(self):
        self.session.clear()

    def __del__(self):
        self.clearSession()
