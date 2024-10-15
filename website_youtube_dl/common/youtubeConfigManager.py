import configparser
import os
import logging
from .configKeys import ConfigKeys

logger = logging.getLogger("__main__")


class ConfigParserManager():
    def __init__(self, configFilePath, configParser=configparser.ConfigParser()):
        self.configFilePath = configFilePath
        self.configParser = configParser

    def createDefaultConfigFile(self):
        self.configParser.add_section(ConfigKeys.GLOBAL.value)
        self.configParser.add_section(ConfigKeys.PLAYLISTS.value)
        homePath = os.path.expanduser(ConfigKeys.SWUNG_DASH.value)
        musicPath = os.path.join(homePath, ConfigKeys.MUSIC.value)
        self.configParser[ConfigKeys.GLOBAL.value][ConfigKeys.PATH.value] = musicPath
        self.saveConfig()

    def getSavePath(self):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        return self.configParser[ConfigKeys.GLOBAL.value][ConfigKeys.PATH.value]

    def getPlaylistUrl(self, playlistName):
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        for configPlaylistName in self.configParser[ConfigKeys.PLAYLISTS.value]:
            if configPlaylistName == playlistName:
                return self.configParser[ConfigKeys.PLAYLISTS.value][playlistName]
        return None

    def getPlaylists(self):
        playlistsFromConfig = {}
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        for playlistName in self.configParser[ConfigKeys.PLAYLISTS.value]:
            playlistsFromConfig[playlistName] = self.configParser[ConfigKeys.PLAYLISTS.value][playlistName]
        return playlistsFromConfig

    def getUrlOfPlaylists(self):
        playlistList = []
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        for playlistName in self.configParser[ConfigKeys.PLAYLISTS.value]:
            playlistList.append(self.configParser[ConfigKeys.PLAYLISTS.value][playlistName])
        return playlistList

    def saveConfig(self): #pragma: no_cover
        with open(self.configFilePath, ConfigKeys.WRITE.value) as configfile:
            self.configParser.write(configfile)

    def addPlaylist(self, playlistName, playlistURL):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if ConfigKeys.PLAYLISTS.value not in self.configParser:
            logger.error(ConfigKeys.CONFIG_ERROR.value)
            return False
        self.configParser[ConfigKeys.PLAYLISTS.value][playlistName] = playlistURL
        logger.info(f"Playlist {playlistName}: {playlistURL} added")
        self.saveConfig()

    def deletePlaylist(self, playlistName):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            logger.error(ConfigKeys.CONFIG_ERROR.value)
            return False
        self.configParser.remove_option(ConfigKeys.PLAYLISTS.value, playlistName)
        self.saveConfig()

if __name__ == "__main__":
    config = ConfigParserManager("/home/rszczygielski/pythonVSC/personal_classes/website/youtube_config.ini")