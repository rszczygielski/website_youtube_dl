from enum import Enum

class Urls(Enum):
    URL_TEST_PLAYLIST = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    URL_NOWY_SWIAT = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    TEST_URL = "testURL.com"

class Paths(Enum):
    READ_STRING_FOR_MOCK = "[global]\npath = /home/rszczygielski/pythonVSC/youtube_files\n[playlists]\ntest_playlist = https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO\nnowy_swiat = https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    CONFIG_INI_PATH = "/test/config_file.ini"
    DOWNLOAD_PATH = "/home/rszczygielski/pythonVSC/youtube_files"

class ConfigTestAttributes(Enum):
    CLEAR = "clear"
    TEST_PLAYLIST = "test_playlist"
    WRONG_URL = "wrong_url"
    SAVE_CONFIG = "saveConfig"
    PLAYLISTS = "playlists"
    TEST_URL = "testURL"
    WRONG_PLAYLIST = "wrongPlaylist"
    NOWY_SWIAT = "nowy_swiat"
    NEW_URL = "newURL"
    SWUNG_DASH = "~"
    MUSIC = "Music"
    GLOBAL = "global"
    PATH = "path"
    TEST_NAME = "test_name"
    NEW_TEST_PLAYLIST = "newTestPlaylist"
    PLAYLIST_NAME = "playlistName"