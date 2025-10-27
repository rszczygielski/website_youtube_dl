import configparser
import os
from unittest import TestCase, main
from unittest.mock import patch
from test.configParserMock import (ConfigParserMock,
                                   ConfigParserMockWithEmptyData,
                                   TestVariables,
                                   ConfigManagerMock)


class TestConfigParserManager(TestCase):

    def setUp(self):
        self.clear_patcher = patch.object(configparser.ConfigParser, "clear")
        self.mock_clear = self.clear_patcher.start()
        self.addCleanup(self.clear_patcher.stop)

        self.config_parser_mock = ConfigParserMock()
        self.main_config = ConfigManagerMock(
            TestVariables.config_file, self.config_parser_mock)

    def test_get_save_path(self):
        save_path = self.main_config.get_save_path()
        self.assertEqual(
            save_path, TestVariables.download_path)
        self.mock_clear.assert_called_once()

    def test_get_url_of_playlists(self):
        test_playlistLists = self.main_config.get_url_of_playlists()
        self.assertEqual([TestVariables.url_test_playlist,
                          TestVariables.url_nowy_swiat], test_playlistLists)
        self.mock_clear.assert_called_once()

    def test_get_playlist_url(self):
        result = self.main_config.get_playlist_url(
            TestVariables.test_playlist)
        self.assertEqual(result,
                         TestVariables.url_test_playlist)

    def test_get_playlist_wrong_url(self):
        result = self.main_config.get_playlist_url(
            TestVariables.wrong_url)
        self.assertEqual(result, None)

    def test_add_playlist(self):
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
        self.assertEqual(self.mock_clear.call_count, 2)

    def test_add_playlist_with_the_same_name(self):
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
        self.assertEqual(self.mock_clear.call_count, 3)

    def test_delete_playlist(self):
        self.main_config.get_url_of_playlists()
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        self.main_config.delete_playlist(TestVariables.test_playlist)
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 1)
        self.assertEqual(self.mock_clear.call_count, 2)

    def test_wrong_playlist_to_delete(self):
        self.main_config.get_url_of_playlists()
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        self.main_config.delete_playlist(TestVariables.wrong_playlist)
        plalists_list_count = len(
            self.config_parser_mock[TestVariables.playlists])
        self.assertEqual(plalists_list_count, 2)
        self.assertEqual(self.mock_clear.call_count, 2)

    def test_get_playlists(self):
        test_playlistDict = self.main_config.get_playlists()
        self.assertEqual({
            TestVariables.test_playlist: TestVariables.url_test_playlist,
            TestVariables.nowy_swiat: TestVariables.url_nowy_swiat
        }, test_playlistDict)


class TestConfigManagerWithEmptyConfig(TestCase):

    def setUp(self):
        self.clear_patcher = patch.object(configparser.ConfigParser, "clear")
        self.mock_clear = self.clear_patcher.start()
        self.addCleanup(self.clear_patcher.stop)

        self.musicPath = ConfigManagerMock._get_home_music_path()
        self.config_parser_mock = ConfigParserMockWithEmptyData()
        self.config = ConfigManagerMock(
            "save_config", self.config_parser_mock)

    def test_get_save_path(self):
        save_path = self.config.get_save_path()
        self.assertEqual(save_path, self.musicPath)

    def test_get_playlists(self):
        test_playlistDict = self.config.get_playlists()
        self.assertEqual(test_playlistDict, {})
        self.assertEqual(
            self.config_parser_mock[TestVariables.global_var][TestVariables.path], self.musicPath)

    def test_get_playlist_urls(self):
        result = self.config.get_playlist_url(
            TestVariables.test_name)
        self.assertEqual(None, result)
        self.assertEqual(
            self.config_parser_mock[TestVariables.global_var][TestVariables.path], self.musicPath)

    def test_get_url_of_playlists(self):
        test_playlistUrls = self.config.get_url_of_playlists()
        self.assertEqual(test_playlistUrls, [])
        self.assertEqual(
            self.config_parser_mock[TestVariables.global_var][TestVariables.path], self.musicPath)
        self.mock_clear.assert_called_once()

    def test_add_playlist(self):
        add_playlist_flag = self.config.add_playlist(
            TestVariables.new_test_playlist, TestVariables.test_url)
        self.assertTrue(add_playlist_flag)
        self.mock_clear.assert_called_once()

    def test_delete_playlist(self):
        delete_playlist_flag = self.config.delete_playlist(
            TestVariables.playlist_name)
        self.assertTrue(delete_playlist_flag)
        self.mock_clear.assert_called_once()


if __name__ == "__main__":
    main()
