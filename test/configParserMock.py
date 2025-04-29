import configparser
from website_youtube_dl.common.configKeys import ConfigKeys
from website_youtube_dl.common.youtubeConfigManager import BaseConfigParser
import os


class ConfigParserMock(configparser.ConfigParser):
    readStringForMock = "[global]\npath = /home/rszczygielski/pythonVSC/youtube_files\n[playlists]\ntest_playlist = https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO\nnowy_swiat = https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"

    def read(self, file_path):
        self.read_string(self.readStringForMock)


class ConfigParserMockWithEmptyData(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("")


class ConfigManagerMock(BaseConfigParser):
    def __init__(self, configFilePath, configParser=ConfigParserMock()):
        self.configFilePath = configFilePath
        self.configParser = configParser
        homePath = os.path.expanduser(ConfigKeys.SWUNG_DASH.value)
        self.musicPath = os.path.join(homePath, ConfigKeys.MUSIC.value)

    def create_default_config_file(self):
        pass

    def get_save_path(self):
        self.configParser.clear()
        self.configParser.read(self.configFilePath)
        if len(self.configParser.sections()) == 0:
            self.createDefaultConfigFile()
        return self.configParser[ConfigKeys.GLOBAL.value][ConfigKeys.PATH.value]

    def handle_default_dir(self, dirPath):
        pass

    def save_config(self):
        pass
