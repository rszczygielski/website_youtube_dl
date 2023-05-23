import configparser
import os

class ConfigParserManager():
    def __init__(self, configFilePath, configParser=configparser.ConfigParser()):
        self.configFilePath = configFilePath
        self.configParser = configParser

    def createDefaultConfigFile(self):
        self.configParser.add_section("global")
        self.configParser.add_section("playlists")
        homePath = os.path.expanduser("~")
        musicPath = os.path.join(homePath, "Music")
        self.configParser["global"]["path"] = musicPath

    def getSavePath(self):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        return self.configParser["global"]["path"]

    def getPlaylists(self):
        playlistsFromConfig = {}
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        for key in self.configParser["playlists"]:
            playlistsFromConfig[key] = self.configParser["playlists"][key]
        return playlistsFromConfig

    def getUrlOfPlaylists(self):
        playlistList = []
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        for key in self.configParser["playlists"]:
            playlistList.append(self.configParser["playlists"][key])
        return playlistList

    def saveConfig(self): #pragma: no_cover
        with open(self.configFilePath, 'w') as configfile:
            self.configParser.write(configfile)

    def addPlaylist(self, playlistName, playlistURL):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        self.configParser["playlists"][playlistName] = playlistURL
        self.saveConfig(self.configParser)

    def deletePlylist(self, playlistName):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        self.configParser.remove_option("playlists", playlistName)
        self.saveConfig(self.configParser)