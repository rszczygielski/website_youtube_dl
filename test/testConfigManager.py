import configparser
import os
from unittest import TestCase, main
from unittest.mock import patch
from website_youtube_dl.common.youtubeConfigManager import BaseConfigParser, ConfigParserManager
from test.configParserMock import ConfigParserMock, ConfigParserMockWithEmptyData


class TestVariables():
    clear = "clear"
    test_playlist = "test_playlist"
    new_playlist = "new_playlist"
    wrong_url = "wrong_url"
    save_config = "save_config"
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

    save_config = "/test/config_file.ini"
    download_path = "/home/rszczygielski/pythonVSC/youtube_files"

    url_test_playlist = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    url_nowy_swiat = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    test_url = "testURL.com"


class Testconfig_parser_managerWithMockConfigClass(TestCase):
    # dodać klasę z zmiennymi żeby równiez ConfigParserMock mógł tego używać

    def setUp(self):
        self.config_parser_mock = ConfigParserMock()
        self.base_config = BaseConfigParser(
            TestVariables.save_config, self.config_parser_mock)
        self.main_config = ConfigParserManager(
            TestVariables.save_config, self.config_parser_mock)

    @patch.object(configparser.ConfigParser, "clear")
    def test_get_save_path(self, mock_clear):
        save_path = self.main_config.get_save_path()
        self.assertEqual(
            save_path, TestVariables.download_path)
        mock_clear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def test_get_url_of_playlists(self, mock_clear):
        test_playlistLists = self.main_config.get_url_of_playlists()
        self.assertEqual([TestVariables.url_test_playlist,
                          TestVariables.url_nowy_swiat], test_playlistLists)
        mock_clear.assert_called_once()

    def test_get_playlist_url(self):
        result = self.main_config.get_playlist_url(
            TestVariables.test_playlist)
        self.assertEqual(result,
                         TestVariables.url_test_playlist)

    def test_get_playlist_wrong_url(self):
        result = self.main_config.get_playlist_url(
            TestVariables.wrong_url)
        self.assertEqual(result, None)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "save_config")
    def test_add_playlist(self, mock_save, mock_clear):
        self.main_config.get_url_of_playlists()
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        self.main_config.add_playlist(
            TestVariables.new_playlist, TestVariables.test_url)
        self.assertEqual(
            self.config_parser_mock[TestVariables.playlists][TestVariables.new_playlist],
            TestVariables.test_url)
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 3)
        mock_save.assert_called_once()
        self.assertEqual(mock_clear.call_count, 2)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "save_config")
    def test_add_playlist_with_the_same_name(self, mock_save, mock_clear):
        self.main_config.get_url_of_playlists()
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        self.main_config.add_playlist(
            TestVariables.new_playlist, TestVariables.test_url)
        self.assertEqual(
            self.config_parser_mock[TestVariables.playlists][TestVariables.new_playlist], TestVariables.test_url)
        self.main_config.add_playlist(
            TestVariables.new_playlist, TestVariables.newUrl)
        self.assertEqual(
            self.config_parser_mock[TestVariables.playlists][TestVariables.new_playlist], TestVariables.newUrl)
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 3)
        self.assertEqual(mock_save.call_count, 2)
        self.assertEqual(mock_clear.call_count, 3)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "save_config")
    def test_delete_playlist(self, mock_save, mock_clear):
        self.main_config.get_url_of_playlists()
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        self.main_config.delete_playlist(TestVariables.test_playlist)
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 1)
        mock_save.assert_called_once()
        self.assertEqual(mock_clear.call_count, 2)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(ConfigParserManager, "save_config")
    def test_wrong_playlist_to_delete(self, mock_save, mock_clear):
        self.main_config.get_url_of_playlists()
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        self.main_config.delete_playlist(TestVariables.wrong_playlist)
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        mock_save.assert_called_once()
        self.assertEqual(mock_clear.call_count, 2)

    def test_get_playlists(self):
        test_playlistDict = self.main_config.get_playlists()
        self.assertEqual({
            TestVariables.test_playlist: TestVariables.url_test_playlist,
            TestVariables.nowy_swiat: TestVariables.url_nowy_swiat
        }, test_playlistDict)


class TestConfingManagerWithEmptyConfig(TestCase):

    def setUp(self):
        self.config_parser_mock = ConfigParserMockWithEmptyData()
        self.config = ConfigParserManager(
            "save_config", self.config_parser_mock)
        homePath = os.path.expanduser(TestVariables.swung_dash)
        self.musicPath = os.path.join(
            homePath, TestVariables.music)

    def test_get_save_path(self):
        save_path = self.config.get_save_path()
        self.assertIsNone(save_path)

    def test_get_playlists(self):
        test_playlistDict = self.config.get_playlists()
        self.assertEqual(test_playlistDict, {})
        self.assertEqual(
            self.config_parser_mock[TestVariables.global_var][TestVariables.path], self.musicPath)

    @patch.object(ConfigParserManager, "save_config")
    def test_get_playlist_urls(self, mock_save):
        result = self.config.get_playlist_url(
            TestVariables.test_name)
        self.assertEqual(None, result)
        self.assertEqual(
            self.config_parser_mock[TestVariables.global_var][TestVariables.path], self.musicPath)
        mock_save.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(BaseConfigParser, "save_config")
    def test_get_url_of_playlists(self, mock_save, mock_clear):
        test_playlistUrls = self.config.get_url_of_playlists()
        self.assertEqual(test_playlistUrls, [])
        self.assertEqual(
            self.config_parser_mock[TestVariables.global_var][TestVariables.path], self.musicPath)
        mock_save.assert_called_once()
        mock_clear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def test_add_playlist(self, mock_clear):
        add_plyalist_flag = self.config.add_playlist(
            TestVariables.new_test_playlist, TestVariables.test_url)
        self.assertFalse(add_plyalist_flag)
        mock_clear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def test_delete_playlist(self, mock_clear):
        delete_playlist_flag = self.config.delete_playlist(
            TestVariables.playlist_name)
        self.assertFalse(delete_playlist_flag)
        mock_clear.assert_called_once()


if __name__ == "__main__":
    main()
