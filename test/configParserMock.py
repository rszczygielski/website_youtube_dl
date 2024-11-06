import configparser
# from testConfigManager import TestVariables

class ConfigParserMock(configparser.ConfigParser):
    readStringForMock = "[global]\npath = /home/rszczygielski/pythonVSC/youtube_files\n[playlists]\ntest_playlist = https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO\nnowy_swiat = https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"

    def read(self, file_path):
        self.read_string(self.readStringForMock)


class ConfigParserMockWithEmptyData(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("")