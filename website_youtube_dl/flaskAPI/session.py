from flask import current_app as app

import os


class SessionDownloadData():
    fileName = None
    fileDirectoryPath = None

    def __init__(self, fullFilePath) -> None:
        self.setSessionDownloadData(fullFilePath)

    def setSessionDownloadData(self, fullFilePath):
        if not os.path.isfile(fullFilePath):
            raise FileNotFoundError(
                f"File {fullFilePath} doesn't exist - something went wrong")
        splitedFilePath = fullFilePath.split("/")
        self.fileName = splitedFilePath[-1]
        self.fileDirectoryPath = "/".join(splitedFilePath[:-1])


class SessionClient():

    def __init__(self, session):
        self.session = session

    def addElemtoSession(self, key, value):
        self.session[key] = value

    def deleteElemFormSession(self, key):
        if not self.ifElemInSession(key):
            return
        self.session.pop(key)

    def ifElemInSession(self, key):
        if key not in self.session.keys():
            app.logger.error(f"Session doesn't have a key: {key}")
            return False
        return True

    def getSessionElem(self, key):
        if not self.ifElemInSession(key):
            return
        return self.session[key]

    def printSessionKeys(self):  # pragma: no_cover
        app.logger.info(self.session.keys())

    def clearSession(self):  # pragma: no_cover
        self.session.clear()

    def getAllSessionKeys(self):  # pragma: no_cover
        return self.session.keys()

    # def __del__(self):
    #     self.clearSession()
