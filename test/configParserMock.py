import configparser
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
import os

class TestVariables():
    clear = "clear"
    test_playlist = "test_playlist"
    new_playlist = "new_playlist"
    wrong_url = "wrong_url"
    playlists = "playlists"
    test_url = "testURL"
    wrong_playlist = "wrong_playlist"
    nowy_swiat = "nowy_swiat"
    newUrl = "newURL"
    swung_dash = "~"
    music = "Music"
    global_var = "global"
    path = "path"
    test_name = "test_name"
    new_test_playlist = "new_test_playlist"
    playlist_name = "playlistName"

    config_file = "/test/config_file.ini"
    download_path = "/home/rszczygielski/pythonVSC/youtube_files"

    url_test_playlist = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    url_nowy_swiat = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    test_url = "testURL.com"

class ConfigParserMock(configparser.ConfigParser):
    readStringForMock = "[global]\npath = /home/rszczygielski/pythonVSC/youtube_files\n[playlists]\ntest_playlist = https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO\nnowy_swiat = https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"

    def read(self, file_path):
        self.read_string(self.readStringForMock)


class ConfigParserMockWithEmptyData(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("")


class ConfigManagerMock(ConfigParserManager):
    def __init__(self, config_file_path, config_parser=ConfigParserMock()):
        self.config_file_path = config_file_path
        self.config_parser = config_parser
        super().__init__(config_file_path, config_parser)
        homePath = os.path.expanduser(TestVariables.swung_dash)
        self.musicPath = os.path.join(homePath, TestVariables.music)
        print("ConfigManagerMock")

    def create_default_config_file(self):
        pass

    def get_save_path(self):
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            self.create_default_config_file()
        return self.config_parser[TestVariables.global_var][TestVariables.path]

    def handle_default_dir(self, dirPath):
        pass

    def save_config(self):
        pass
