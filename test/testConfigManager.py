import configparser
import os
from unittest import TestCase, main
from unittest.mock import patch
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
from test.configParserMock import ConfigParserMock, ConfigParserMockWithEmptyData

class TestVariables():
    clear = "clear"
    testPlaylist = "test_playlist"
    newPlaylist = "new_playlist"
    wrongUrl = "wrong_url"
    saveConfig = "saveConfig"
    playlists = "playlists"
    testUrl = "testURL"
    wrongPlaylist = "wrongPlaylist"
    nowySwiat = "nowy_swiat"
    newUrl = "newURL"
    swungDash = "~"
    music = "Music"
    globalVar = "global"
    path = "path"
    testName = "test_name"
    newTestPlaylist = "newTestPlaylist"
    playlistName = "playlistName"

    saveConfig = "/test/config_file.ini"
    downloadPath = "/home/rszczygielski/pythonVSC/youtube_files"

    urlTestPlaylist = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    urlNowySwiat = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    testUrl = "testURL.com"


class TestconfigParserManagerWithMockConfigClass(TestCase):
    # dodać klasę z zmiennymi żeby równiez ConfigParserMock mógł tego używać

    def setUp(self):
        self.configParserMock = ConfigParserMock()
        self.config = ConfigParserManager(
            TestVariables.saveConfig, self.configParserMock)

    @patch.object(configparser.ConfigParser, "clear")
    def testGetSavePath(self, mockClear):
        save_path = self.config.getSavePath()
        self.assertEqual(
            save_path, TestVariables.downloadPath)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testGetUrlOfPlaylists(self, mockClear):
        testPlaylistLists = self.config.getUrlOfPlaylists()
        self.assertEqual([TestVariables.urlTestPlaylist,
                          TestVariables.urlNowySwiat], testPlaylistLists)
        mockClear.assert_called_once()

    def testGetPlaylistUrl(self):
        result = self.config.getPlaylistUrl(
            TestVariables.testPlaylist)
        self.assertEqual(result,
                         TestVariables.urlTestPlaylist)

    def testGetPlaylistWrongUrl(self):
        result = self.config.getPlaylistUrl(
            TestVariables.wrongUrl)
        self.assertEqual(result, None)


    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testAddPlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist(TestVariables.newPlaylist, TestVariables.testUrl)
        self.assertEqual(
            self.configParserMock[TestVariables.playlists][TestVariables.newPlaylist],
            TestVariables.testUrl)
        plalistsListCount = len(self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 3)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)


    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testAddPlaylistWithTheSameName(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist(TestVariables.newPlaylist, TestVariables.testUrl)
        self.assertEqual(
            self.configParserMock[TestVariables.playlists][TestVariables.newPlaylist], TestVariables.testUrl)
        self.config.addPlaylist(TestVariables.newPlaylist, TestVariables.newUrl)
        self.assertEqual(
            self.configParserMock[TestVariables.playlists][TestVariables.newPlaylist], TestVariables.newUrl)
        plalistsListCount = len(self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 3)
        self.assertEqual(mockSave.call_count, 2)
        self.assertEqual(mockClear.call_count, 3)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testDeletePlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(
            self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlaylist(TestVariables.testPlaylist)
        plalistsListCount = len(
            self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 1)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testWrongPlaylistToDelete(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(
            self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlaylist(TestVariables.wrongPlaylist)
        plalistsListCount = len(
            self.configParserMock[TestVariables.playlists])
        self.assertEqual(plalistsListCount, 2)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    def testGetPlaylists(self):
        testPlaylistDict = self.config.getPlaylists()
        self.assertEqual({
            TestVariables.testPlaylist: TestVariables.urlTestPlaylist,
            TestVariables.nowySwiat: TestVariables.urlNowySwiat
        }, testPlaylistDict)


class TestConfingManagerWithEmptyConfig(TestCase):

    def setUp(self):
        self.configParserMock = ConfigParserMockWithEmptyData()
        self.config = ConfigParserManager(
            "saveConfig", self.configParserMock)
        homePath = os.path.expanduser(TestVariables.swungDash)
        self.musicPath = os.path.join(
            homePath, TestVariables.music)

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
            self.configParserMock[TestVariables.globalVar][TestVariables.path], self.musicPath)
        mockSave.assert_called_once()

    @patch.object(ConfigParserManager, "saveConfig")
    def testGetPlaylistUrls(self, mockSave):
        result = self.config.getPlaylistUrl(
            TestVariables.testName)
        self.assertEqual(None, result)
        self.assertEqual(
            self.configParserMock[TestVariables.globalVar][TestVariables.path], self.musicPath)
        mockSave.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "saveConfig")
    def testGetUrlOfPlaylists(self, mockSave, mockClear):
        testPlaylistUrls = self.config.getUrlOfPlaylists()
        self.assertEqual(testPlaylistUrls, [])
        self.assertEqual(
            self.configParserMock[TestVariables.globalVar][TestVariables.path], self.musicPath)
        mockSave.assert_called_once()
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testAddPlaylist(self, mockClear):
        addPlyalistFlag = self.config.addPlaylist(
            TestVariables.newTestPlaylist, TestVariables.testUrl)
        self.assertFalse(addPlyalistFlag)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testDeletePlaylist(self, mockClear):
        deletePlaylistFlag = self.config.deletePlaylist(
            TestVariables.playlistName)
        self.assertFalse(deletePlaylistFlag)
        mockClear.assert_called_once()


if __name__ == "__main__":
    main()
