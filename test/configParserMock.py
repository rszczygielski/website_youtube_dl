import os
import configparser
from website_youtube_dl.common.youtube_config_manager import ConfigParserManager

class TestConstants:
    """Centralized constants for unit testing configuration logic."""
    SECTION_GLOBAL = "global"
    SECTION_PLAYLISTS = "playlists"
    
    KEY_PATH = "path"
    KEY_PLAYLIST_NAME = "playlistName"
    
    # Mock Data Values
    DEFAULT_MUSIC_DIR = "Music"
    TEST_PLAYLIST_ID = "test_playlist"
    NEW_PLAYLIST_ID = "new_playlist"
    NOWY_SWIAT_ID = "nowy_swiat"
    
    # Mock Paths and URLs
    MOCK_CONFIG_PATH = "/test/config_file.ini"
    LEGACY_DOWNLOAD_PATH = "/home/rszczygielski/pythonVSC/youtube_files"
    
    URL_TEST_PLAYLIST = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    URL_NOWY_SWIAT = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    URL_GENERIC_TEST = "testURL.com"


class ConfigParserMock(configparser.ConfigParser):
    """Mocks a ConfigParser populated with predefined test data."""
    MOCK_INI_CONTENT = (
        f"[{TestConstants.SECTION_GLOBAL}]\n"
        f"path = {TestConstants.LEGACY_DOWNLOAD_PATH}\n"
        f"[{TestConstants.SECTION_PLAYLISTS}]\n"
        f"{TestConstants.TEST_PLAYLIST_ID} = {TestConstants.URL_TEST_PLAYLIST}\n"
        f"{TestConstants.NOWY_SWIAT_ID} = {TestConstants.URL_NOWY_SWIAT}"
    )

    def read(self, file_path):
        """Overrides file reading to inject mock string content."""
        self.read_string(self.MOCK_INI_CONTENT)


class ConfigParserEmptyMock(configparser.ConfigParser):
    """Mocks an empty configuration file."""
    def read(self, file_path):
        self.read_string("")


class ConfigManagerMock(ConfigParserManager):
    """
    Subclass of the production ConfigParserManager to safely test 
    logic without performing actual I/O operations.
    """
    def __init__(self, config_file_path, config_parser=None):
        # Default to standard Mock if none provided
        self.config_parser = config_parser or ConfigParserMock()
        self.config_file_path = config_file_path
        self.music_path = self._get_home_music_path()
        super().__init__(config_file_path, self.config_parser)

    @staticmethod
    def _get_home_music_path():
        """Calculates the user's home music directory."""
        home_path = os.path.expanduser("~")
        return os.path.join(home_path, TestConstants.DEFAULT_MUSIC_DIR)

    def create_default_config_file(self):
        """Simulates initial config file generation."""
        self.config_parser.add_section(TestConstants.SECTION_GLOBAL)
        self.config_parser.add_section(TestConstants.SECTION_PLAYLISTS)
        self.config_parser[TestConstants.SECTION_GLOBAL][TestConstants.KEY_PATH] = self._get_home_music_path()

    def get_save_path(self):
        """Logic to resolve the download path from the mock config."""
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        
        if not self.config_parser.sections():
            print("INFO: Creating default configuration.")
            self.create_default_config_file()
            
        return self.config_parser[TestConstants.SECTION_GLOBAL][TestConstants.KEY_PATH]

    def handle_default_dir(self, dir_path):
        """Nop override to prevent filesystem interference during tests."""
        pass

    def save_config(self):
        """Nop override to prevent disk writing during tests."""
        pass