import configparser
import os
from unittest import TestCase, main
from unittest.mock import patch
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
from configManagerKeys import Urls, Paths, ConfigTestAttributes


class ConfigParserMock(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string(Paths.READ_STRING_FOR_MOCK.value)


class ConfigParserMockWithEmptyData(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("")


class TestconfigParserManagerWithMockConfigClass(TestCase):
    # dodać klasę z zmiennymi żeby równiez ConfigParserMock mógł tego używać

    def setUp(self):
        self.configParserMock = ConfigParserMock()
        self.config = ConfigParserManager(
            Paths.CONFIG_INI_PATH.value, self.configParserMock)

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    def testGetSavePath(self, mockClear):
        save_path = self.config.getSavePath()
        self.assertEqual(
            save_path, Paths.DOWNLOAD_PATH.value)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    def testGetUrlOfPlaylists(self, mockClear):
        testPlaylistLists = self.config.getUrlOfPlaylists()
        self.assertEqual([Urls.URL_TEST_PLAYLIST.value,
                          Urls.URL_NOWY_SWIAT.value], testPlaylistLists)
        mockClear.assert_called_once()

    def testGetPlaylistUrl(self):
        result = self.config.getPlaylistUrl(
            ConfigTestAttributes.TEST_PLAYLIST.value)
        self.assertEqual(result,
                         Urls.URL_TEST_PLAYLIST.value)

    def testGetPlaylistWrongUrl(self):
        result = self.config.getPlaylistUrl(
            ConfigTestAttributes.WRONG_URL.value)
        self.assertEqual(result, None)

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testAddPlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist(
            ConfigTestAttributes.TEST_PLAYLIST.value, ConfigTestAttributes.TEST_URL.value)
        self.assertEqual(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value][ConfigTestAttributes.TEST_PLAYLIST.value], ConfigTestAttributes.TEST_URL.value)
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 3)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testAddPlaylistWithTheSameName(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist(
            ConfigTestAttributes.TEST_PLAYLIST.value, ConfigTestAttributes.TEST_URL.value)
        self.assertEqual(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value][ConfigTestAttributes.TEST_PLAYLIST.value], ConfigTestAttributes.TEST_URL.value)
        self.config.addPlaylist(
            ConfigTestAttributes.TEST_PLAYLIST.value, ConfigTestAttributes.NEW_URL.value)
        self.assertEqual(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value][ConfigTestAttributes.TEST_PLAYLIST.value], ConfigTestAttributes.NEW_URL.value)
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 3)
        self.assertEqual(mockSave.call_count, 2)
        self.assertEqual(mockClear.call_count, 3)

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testDeletePlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlaylist(ConfigTestAttributes.TEST_PLAYLIST.value)
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 1)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testWrongPlaylistToDelete(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlaylist(ConfigTestAttributes.WRONG_PLAYLIST.value)
        plalistsListCount = len(
            self.configParserMock[ConfigTestAttributes.PLAYLISTS.value])
        self.assertEqual(plalistsListCount, 2)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    def testGetPlaylists(self):
        testPlaylistDict = self.config.getPlaylists()
        self.assertEqual({
            ConfigTestAttributes.TEST_PLAYLIST.value: Urls.URL_TEST_PLAYLIST.value,
            ConfigTestAttributes.NOWY_SWIAT.value: Urls.URL_NOWY_SWIAT.value
        }, testPlaylistDict)


class TestConfingManagerWithEmptyConfig(TestCase):

    def setUp(self):
        self.configParserMock = ConfigParserMockWithEmptyData()
        self.config = ConfigParserManager(
            Paths.CONFIG_INI_PATH.value, self.configParserMock)
        homePath = os.path.expanduser(ConfigTestAttributes.SWUNG_DASH.value)
        self.musicPath = os.path.join(
            homePath, ConfigTestAttributes.MUSIC.value)

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testGetSavePath(self, mockSave, mockClear):
        save_path = self.config.getSavePath()
        self.assertEqual(save_path, self.musicPath)
        mockSave.assert_called_once()
        mockClear.assert_called_once()

    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testGetPlaylists(self, mockSave):
        testPlaylistDict = self.config.getPlaylists()
        self.assertEqual(testPlaylistDict, {})
        self.assertEqual(
            self.configParserMock[ConfigTestAttributes.GLOBAL.value][ConfigTestAttributes.PATH.value], self.musicPath)
        mockSave.assert_called_once()

    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testGetPlaylistUrls(self, mockSave):
        result = self.config.getPlaylistUrl(
            ConfigTestAttributes.TEST_NAME.value)
        self.assertEqual(None, result)
        self.assertEqual(
            self.configParserMock[ConfigTestAttributes.GLOBAL.value][ConfigTestAttributes.PATH.value], self.musicPath)
        mockSave.assert_called_once()

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    @patch.object(ConfigParserManager, ConfigTestAttributes.SAVE_CONFIG.value)
    def testGetUrlOfPlaylists(self, mockSave, mockClear):
        testPlaylistUrls = self.config.getUrlOfPlaylists()
        self.assertEqual(testPlaylistUrls, [])
        self.assertEqual(
            self.configParserMock[ConfigTestAttributes.GLOBAL.value][ConfigTestAttributes.PATH.value], self.musicPath)
        mockSave.assert_called_once()
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    def testAddPlaylist(self, mockClear):
        addPlyalistFlag = self.config.addPlaylist(
            ConfigTestAttributes.NEW_TEST_PLAYLIST.value, Urls.TEST_URL.value)
        self.assertFalse(addPlyalistFlag)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, ConfigTestAttributes.CLEAR.value)
    def testDeletePlaylist(self, mockClear):
        deletePlaylistFlag = self.config.deletePlaylist(
            ConfigTestAttributes.PLAYLIST_NAME.value)
        self.assertFalse(deletePlaylistFlag)
        mockClear.assert_called_once()


if __name__ == "__main__":
    main()
