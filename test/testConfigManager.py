import configparser
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call
from configParserManager import ConfigParserManager



class ConfigParserMock(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("[global]\npath = /home/rszczygielski/pythonVSC/youtube_files\n[playlists]\ntest_playlist = https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO\nnowy_swiat = https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU")

class TestConfigParserMenagerWithMockConfigClass(TestCase):
    def setUp(self):
        self.configParserMock = ConfigParserMock()
        self.config = ConfigParserManager("/test/config_file.ini", self.configParserMock)

    @patch.object(configparser.ConfigParser, "clear")
    def testGetSavePath(self, mockClear):
        save_path = self.config.getSavePath()
        self.assertEqual(save_path, "/home/rszczygielski/pythonVSC/youtube_files")
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testGetUrlOfPlaylists(self, mockClear):
        testPlaylistLists = self.config.getUrlOfPlaylists()
        self.assertEqual(["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO",\
                          "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"], testPlaylistLists)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testAddPlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist("testPlaylist", "testURL")
        self.assertEqual(self.configParserMock["playlists"]["testPlaylist"], "testURL")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 3)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testAddPlaylistWithTheSameName(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist("testPlaylist", "testURL")
        self.assertEqual(self.configParserMock["playlists"]["testPlaylist"], "testURL")
        self.config.addPlaylist("testPlaylist", "newURL")
        self.assertEqual(self.configParserMock["playlists"]["testPlaylist"], "newURL")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 3)
        self.assertEqual(mockSave.call_count, 2)
        self.assertEqual(mockClear.call_count, 3)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testDeletePlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlylist("test_playlist")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 1)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testWrongPlaylistToDelete(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlylist("wrongPlaylist")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

if __name__ == "__main__":
    main()