import configparser
from unittest import TestCase, main
from unittest.mock import patch

from test.configParserMock import (
    ConfigParserMock,
    ConfigParserEmptyMock,
    TestConstants,
    ConfigManagerMock
)

class TestConfigParserManager(TestCase):

    def setUp(self):
        # Patch ConfigParser.clear to verify re-loading behavior
        self.clear_patcher = patch.object(configparser.ConfigParser, "clear")
        self.mock_clear = self.clear_patcher.start()
        self.addCleanup(self.clear_patcher.stop)

        self.config_parser_mock = ConfigParserMock()
        self.config_manager = ConfigManagerMock(
            TestConstants.MOCK_CONFIG_PATH, 
            self.config_parser_mock
        )

    # --- Helper Methods ---

    def assert_playlist_state(self, expected_count, expected_clear_calls):
        """Helper to verify the number of playlists and clear() calls."""
        playlists = self.config_parser_mock[TestConstants.SECTION_PLAYLISTS]
        self.assertEqual(len(playlists), expected_count)
        self.assertEqual(self.mock_clear.call_count, expected_clear_calls)

    # --- Test Cases ---

    def test_get_save_path(self):
        save_path = self.config_manager.get_save_path()
        self.assertEqual(save_path, TestConstants.LEGACY_DOWNLOAD_PATH)
        self.mock_clear.assert_called_once()

    def test_get_url_of_playlists(self):
        urls = self.config_manager.get_url_of_playlists()
        expected_urls = [TestConstants.URL_TEST_PLAYLIST, TestConstants.URL_NOWY_SWIAT]
        self.assertEqual(urls, expected_urls)
        self.mock_clear.assert_called_once()

    def test_get_playlist_url_success(self):
        result = self.config_manager.get_playlist_url(TestConstants.TEST_PLAYLIST_ID)
        self.assertEqual(result, TestConstants.URL_TEST_PLAYLIST)

    def test_get_playlist_url_not_found(self):
        # wrong_url represents a name/key that doesn't exist
        result = self.config_manager.get_playlist_url("non_existent_key")
        self.assertIsNone(result)

    def test_add_playlist(self):
        # Initial state (from Mock)
        self.config_manager.get_url_of_playlists()  # Triggers 1st clear
        self.assert_playlist_state(expected_count=2, expected_clear_calls=1)
        
        # Action
        self.config_manager.add_playlist(TestConstants.NEW_PLAYLIST_ID, TestConstants.URL_GENERIC_TEST)
        
        # Verify result
        self.assertEqual(
            self.config_parser_mock[TestConstants.SECTION_PLAYLISTS][TestConstants.NEW_PLAYLIST_ID],
            TestConstants.URL_GENERIC_TEST
        )
        self.assert_playlist_state(expected_count=3, expected_clear_calls=2)

    def test_add_playlist_overwrite_existing(self):
        self.config_manager.get_url_of_playlists()
        self.config_manager.add_playlist(TestConstants.NEW_PLAYLIST_ID, TestConstants.URL_GENERIC_TEST)
        
        # Update existing
        new_url = "https://updated-url.com"
        self.config_manager.add_playlist(TestConstants.NEW_PLAYLIST_ID, new_url)
        
        self.assertEqual(
            self.config_parser_mock[TestConstants.SECTION_PLAYLISTS][TestConstants.NEW_PLAYLIST_ID], 
            new_url
        )
        self.assert_playlist_state(expected_count=3, expected_clear_calls=3)

    def test_delete_playlist_success(self):
        self.config_manager.get_url_of_playlists()
        self.assert_playlist_state(expected_count=2, expected_clear_calls=1)
        
        self.config_manager.delete_playlist(TestConstants.TEST_PLAYLIST_ID)
        self.assert_playlist_state(expected_count=1, expected_clear_calls=2)

    def test_delete_playlist_not_found(self):
        self.config_manager.get_url_of_playlists()
        self.config_manager.delete_playlist("invalid_key")
        self.assert_playlist_state(expected_count=2, expected_clear_calls=2)

    def test_get_playlists_dict(self):
        playlists_dict = self.config_manager.get_playlists()
        expected = {
            TestConstants.TEST_PLAYLIST_ID: TestConstants.URL_TEST_PLAYLIST,
            TestConstants.NOWY_SWIAT_ID: TestConstants.URL_NOWY_SWIAT
        }
        self.assertEqual(playlists_dict, expected)


class TestConfigManagerWithEmptyConfig(TestCase):

    def setUp(self):
        self.clear_patcher = patch.object(configparser.ConfigParser, "clear")
        self.mock_clear = self.clear_patcher.start()
        self.addCleanup(self.clear_patcher.stop)

        self.expected_music_path = ConfigManagerMock._get_home_music_path()
        self.config_parser_mock = ConfigParserEmptyMock()
        self.config_manager = ConfigManagerMock("dummy_path", self.config_parser_mock)

    def test_get_save_path_creates_default(self):
        save_path = self.config_manager.get_save_path()
        self.assertEqual(save_path, self.expected_music_path)

    def test_get_playlists_empty(self):
        playlists = self.config_manager.get_playlists()
        self.assertEqual(playlists, {})
        # Verify that accessing path initializes the default global config
        self.assertEqual(
            self.config_parser_mock[TestConstants.SECTION_GLOBAL][TestConstants.KEY_PATH], 
            self.expected_music_path
        )

    def test_get_playlist_url_empty_config(self):
        result = self.config_manager.get_playlist_url("any_name")
        self.assertIsNone(result)
        self.assertEqual(
            self.config_parser_mock[TestConstants.SECTION_GLOBAL][TestConstants.KEY_PATH], 
            self.expected_music_path
        )

    def test_get_url_of_playlists_empty(self):
        urls = self.config_manager.get_url_of_playlists()
        self.assertEqual(urls, [])
        self.mock_clear.assert_called_once()

    def test_add_playlist_in_empty_config(self):
        success = self.config_manager.add_playlist("new_item", TestConstants.URL_GENERIC_TEST)
        self.assertTrue(success)
        self.mock_clear.assert_called_once()

    def test_delete_playlist_in_empty_config(self):
        success = self.config_manager.delete_playlist("non_existent")
        self.assertFalse(success)
        self.mock_clear.assert_called_once()


if __name__ == "__main__":
    main()