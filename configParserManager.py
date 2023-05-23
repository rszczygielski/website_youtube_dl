import configparser

class ConfigParserManager():
    def __init__(self, configFilePath, configParser=configparser.ConfigParser()):
        self.configFilePath = configFilePath
        self.configParser = configParser

    def getSavePath(self):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        return self.configParser["global"]["path"]

    def getUrlOfPlaylists(self):
        playlistList = []
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        for key in self.configParser["playlists"]:
            playlistList.append(self.configParser["playlists"][key])
        return playlistList

    def saveConfig(self): #pragma: no_cover
        with open(self.configFilePath, 'w') as configfile:
            self.configParser.write(configfile)

    def addPlaylist(self, playlistName, playlistURL):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        self.configParser["playlists"][playlistName] = playlistURL
        self.saveConfig(self.configParser)

    def deletePlylist(self, playlistName):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        self.configParser.remove_option("playlists", playlistName)
        self.saveConfig(self.configParser)