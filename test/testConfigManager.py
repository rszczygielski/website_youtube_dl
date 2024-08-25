import configparser
import os
from unittest import TestCase, main
from unittest.mock import patch
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager


class ConfigParserMock(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("[global]\npath = /home/rszczygielski/pythonVSC/youtube_files\n[playlists]\ntest_playlist = https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO\nnowy_swiat = https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU")


class ConfigParserMockWithEmptyData(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("")


class TestconfigParserManagerWithMockConfigClass(TestCase):
    def setUp(self):
        self.configParserMock = ConfigParserMock()
        self.config = ConfigParserManager(
            "/test/config_file.ini", self.configParserMock)

    @patch.object(configparser.ConfigParser, "clear")
    def testGetSavePath(self, mockClear):
        save_path = self.config.getSavePath()
        self.assertEqual(
            save_path, "/home/rszczygielski/pythonVSC/youtube_files")
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testGetUrlOfPlaylists(self, mockClear):
        testPlaylistLists = self.config.getUrlOfPlaylists()
        self.assertEqual(["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO",
                          "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"], testPlaylistLists)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testAddPlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist("testPlaylist", "testURL")
        self.assertEqual(
            self.configParserMock["playlists"]["testPlaylist"], "testURL")
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
        self.assertEqual(
            self.configParserMock["playlists"]["testPlaylist"], "testURL")
        self.config.addPlaylist("testPlaylist", "newURL")
        self.assertEqual(
            self.configParserMock["playlists"]["testPlaylist"], "newURL")
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
        self.config.deletePlaylist("test_playlist")
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
        self.config.deletePlaylist("wrongPlaylist")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    def testGetPlaylists(self):
        testPlaylistDict = self.config.getPlaylists()
        self.assertEqual({
            "test_playlist": "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO",
            "nowy_swiat": "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
        }, testPlaylistDict)


class TestConfingManagerWithEmptyConfig(TestCase):

    def setUp(self):
        self.configParserMock = ConfigParserMockWithEmptyData()
        self.config = ConfigParserManager(
            "/test/config_file.ini", self.configParserMock)
        homePath = os.path.expanduser("~")
        self.musicPath = os.path.join(homePath, "Music")

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testGetSavePath(self, mockSave, mockClear):
        save_path = self.config.getSavePath()
        self.assertEqual(save_path, self.musicPath)
        mockSave.assert_called_once()
        mockClear.assert_called_once()

    @patch.object(ConfigParserManager, "saveConfig")
    def testGetPlaylists(self, mockSave):
        testPlaylistDict = self.config.getPlaylists()
        self.assertEqual(testPlaylistDict, {})
        self.assertEqual(
            self.configParserMock["global"]["path"], self.musicPath)
        mockSave.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testGetUrlOfPlaylists(self, mockSave, mockClear):
        testPlaylistUrls = self.config.getUrlOfPlaylists()
        self.assertEqual(testPlaylistUrls, [])
        self.assertEqual(
            self.configParserMock["global"]["path"], self.musicPath)
        mockSave.assert_called_once()
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testAddPlaylist(self, mockClear):
        addPlyalistFlag = self.config.addPlaylist(
            "newTestPlaylist", "testURL.com")
        self.assertFalse(addPlyalistFlag)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testDeletePlaylist(self, mockClear):
        deletePlaylistFlag = self.config.deletePlaylist("palylistName")
        self.assertFalse(deletePlaylistFlag)
        mockClear.assert_called_once()


if __name__ == "__main__":
    main()
