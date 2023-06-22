import configparser
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
        if "playlists" not in self.configParser:
            print(f"{bcolors.FAIL}Config file is not correct{bcolors.ENDC}")
            return False
        self.configParser["playlists"][playlistName] = playlistURL
        self.saveConfig(self.configParser)

    def deletePlaylist(self, playlistName):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            print(f"{bcolors.FAIL}Config file is not correct{bcolors.ENDC}")
            return False
        self.configParser.remove_option("playlists", playlistName)
        self.saveConfig(self.configParser)

if __name__ == "__main__":
    config = ConfigParserManager("/home/rszczygielski/pythonVSC/personal_classes/website/youtube_config.ini")
    print(config.getPlaylists())