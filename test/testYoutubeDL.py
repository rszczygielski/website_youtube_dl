import os
import yt_dlp
from unittest import TestCase, main
from unittest.mock import patch, call, MagicMock

from website_youtube_dl.common.youtube_config_manager import BaseConfigParser
from website_youtube_dl.common.youtube_data_keys import PlaylistInfo, MediaInfo, MainYoutubeKeys
import website_youtube_dl.common.youtube_dl as youtube_dl
from website_youtube_dl.common.youtube_api import (
    SingleMedia,
    MediaFromPlaylist,
    PlaylistMedia
)
from website_youtube_dl.common.youtube_options import (
    YoutubeAudioOptions,
    YoutubeVideoOptions,
    YoutubeOptiones
)
from test.configParserMock import ConfigParserMock, TestConstants
from test.easyID3ManagerMock import EasyID3ManagerMock


class TestYoutubeDL(TestCase):
    # Base URLs and Hashes
    URL_SINGLE = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    URL_PLAYLIST_WITH_VIDEO = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    URL_PLAYLIST_ONLY_1 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    URL_PLAYLIST_ONLY_2 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    URL_PLAYLIST_WITH_INDEX = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO&index=1"
    
    PLAYLIST_HASH = "PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    MSG_DOWNLOAD_ERROR = "Download media info error ValueError"
    MSG_PLAYLIST_ONLY_ERROR = 'This a playlist only - without video hash to download'

    # Test Metadata
    FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
    TEST_PLAYLIST_NAME = "test_playlist"
    TEST_TITLE_1 = "Society"
    TEST_ALBUM_1 = "Into The Wild"
    TEST_ARTIST_1 = "Eddie Vedder"
    TEST_EXT_1 = "webm"
    TEST_INDEX_1 = 1
    TEST_URL_1 = 'https://www.youtube.com/watch?v=ABsslEoL0-c'
    TEST_ID_1 = 'ABsslEoL0-c'
    TEST_FULL_PATH_1 = os.path.join(FOLDER_PATH, f"{TEST_TITLE_1}.webm")

    TEST_TITLE_2 = 'Hard Sun'
    TEST_ARTIST_2 = "Eddie Vedder"
    TEST_EXT_2 = "webm"
    TEST_INDEX_2 = 2
    TEST_URL_2 = 'https://www.youtube.com/watch?v=_EZUfnMv3Lg'
    TEST_ID_2 = '_EZUfnMv3Lg'
    TEST_FULL_PATH_2 = os.path.join(FOLDER_PATH, f"{TEST_TITLE_2}.webm")

    # Mock Data Dictionaries
    SONG_META_1 = {
        MediaInfo.TITLE.value: TEST_TITLE_1,
        MediaInfo.ALBUM.value: TEST_ALBUM_1,
        MediaInfo.ARTIST.value: TEST_ARTIST_1,
        MediaInfo.EXTENSION.value: TEST_EXT_1,
        PlaylistInfo.PLAYLIST_INDEX.value: TEST_INDEX_1,
        MediaInfo.URL.value: TEST_URL_1,
        MediaInfo.YOUTUBE_HASH.value: TEST_ID_1,
        MainYoutubeKeys.REQUESTED_DOWNLOADS.value: [
            {MainYoutubeKeys.FUL_PATH.value: TEST_FULL_PATH_1}]
    }

    SONG_META_2 = {
        MediaInfo.TITLE.value: TEST_TITLE_2,
        MediaInfo.ARTIST.value: TEST_ARTIST_2,
        MediaInfo.ALBUM.value: TEST_ALBUM_1,
        MediaInfo.EXTENSION.value: TEST_EXT_2,
        PlaylistInfo.PLAYLIST_INDEX.value: TEST_INDEX_2,
        MediaInfo.URL.value: TEST_URL_2,
        MediaInfo.YOUTUBE_HASH.value: TEST_ID_2,
        MainYoutubeKeys.REQUESTED_DOWNLOADS.value: [
            {MainYoutubeKeys.FUL_PATH.value: TEST_FULL_PATH_2}]
    }

    PLAYLIST_ENTRY_1 = {PlaylistInfo.TITLE.value: TEST_TITLE_1, PlaylistInfo.URL.value: TEST_ID_1}
    PLAYLIST_ENTRY_2 = {PlaylistInfo.TITLE.value: TEST_TITLE_2, PlaylistInfo.URL.value: TEST_ID_2}

    TEST_PLAYLIST_FULL_ENTRIES = [SONG_META_1, SONG_META_2, None]
    TEST_PLAYLIST_SIMPLE_ENTRIES = [PLAYLIST_ENTRY_1, PLAYLIST_ENTRY_2, None]
    TEST_PLAYLIST_URLS = [URL_PLAYLIST_ONLY_1, URL_PLAYLIST_ONLY_2]

    # API Objects for Comparison
    EXPECTED_SINGLE_MEDIA = SingleMedia(TEST_FULL_PATH_1, TEST_TITLE_1, TEST_ALBUM_1,
                                       TEST_ARTIST_1, TEST_ID_1, TEST_URL_1, TEST_EXT_1)
    
    EXPECTED_PLAYLIST_MEDIA = PlaylistMedia(TEST_PLAYLIST_NAME, [
        MediaFromPlaylist(TEST_TITLE_1, TEST_ID_1),
        MediaFromPlaylist(TEST_TITLE_2, TEST_ID_2)
    ])

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        config_parser_manager = BaseConfigParser(
            f'{self.test_dir}/test_youtube_config.ini',
            ConfigParserMock()
        )
        
        self.youtube_dl = youtube_dl.YoutubeDL(config_parser_manager)
        self.youtube_playlists = youtube_dl.YoutubeDlPlaylists(config_parser_manager, MagicMock())
        
        # Configure test path and template
        self.youtube_dl._savePath = self.test_dir
        self.youtube_dl._ydl_opts.overwrite_option(
            YoutubeOptiones.OUT_TEMPLATE,
            os.path.join(self.test_dir, '%(title)s.%(ext)s')
        )
        
        # Mocking metadata manager
        self.meta_manager = EasyID3ManagerMock()
        self.meta_manager.set_params(
            file_path=self.test_dir,
            title=self.TEST_TITLE_1,
            album=self.TEST_ALBUM_1,
            artist=self.TEST_ARTIST_1,
            track_number=self.TEST_INDEX_1,
            playlist_name=self.TEST_PLAYLIST_NAME,
        )

    # --- Assertion Helpers ---

    def assert_single_media_equal(self, actual, expected):
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.album, expected.album)
        self.assertEqual(actual.artist, expected.artist)
        self.assertEqual(actual.extension, expected.extension)
        self.assertEqual(actual.url, expected.url)
        self.assertEqual(actual.yt_hash, expected.yt_hash)

    def assert_playlist_media_equal(self, actual, expected):
        self.assertEqual(actual.playlist_name, expected.playlist_name)
        self.assertEqual(len(actual.media_from_playlist_list), len(expected.media_from_playlist_list))
        for act_track, exp_track in zip(actual.media_from_playlist_list, expected.media_from_playlist_list):
            self.assertEqual(act_track.title, exp_track.title)
            self.assertEqual(act_track.yt_hash, exp_track.yt_hash)

    def mock_extract(self, return_value=None, side_effect=None):
        patcher = patch.object(yt_dlp.YoutubeDL, "extract_info",
                               return_value=return_value, side_effect=side_effect)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj

    # --- Core Download Tests ---

    def test_download_file_success(self):
        mock_info = self.mock_extract(return_value=self.SONG_META_1)
        result = self.youtube_dl._download_file(self.URL_SINGLE)
        
        self.assertFalse(result.is_error())
        mock_info.assert_called_once_with(self.URL_SINGLE)
        self.assert_single_media_equal(result.get_data(), self.EXPECTED_SINGLE_MEDIA)

    def test_download_file_with_one_time_template(self):
        self.youtube_dl.set_title_template_one_time("temp_template")
        self.assertEqual("temp_template", self.youtube_dl.title_template)
        
        self.mock_extract(return_value=self.SONG_META_1)
        result = self.youtube_dl._download_file(self.URL_SINGLE)
        
        self.assertFalse(result.is_error())
        # Verify template reset
        self.assertEqual('/%(title)s', self.youtube_dl.title_template)

    def test_download_file_error(self):
        self.mock_extract(side_effect=ValueError(self.MSG_DOWNLOAD_ERROR))
        result = self.youtube_dl._download_file(self.URL_SINGLE)
        
        self.assertTrue(result.is_error())
        self.assertEqual(result.get_error_info(), self.MSG_DOWNLOAD_ERROR)

    # --- Hash Extraction Tests ---

    def test_get_media_result_hash(self):
        # Test various URL formats
        urls = [self.URL_SINGLE, self.URL_PLAYLIST_WITH_VIDEO, self.URL_PLAYLIST_WITH_INDEX, self.TEST_ID_1]
        for url in urls:
            self.assertEqual(self.youtube_dl._get_media_result_hash(url), self.TEST_ID_1)

        with self.assertRaises(ValueError) as context:
            self.youtube_dl._get_media_result_hash(self.URL_PLAYLIST_ONLY_1)
        self.assertIn(self.MSG_PLAYLIST_ONLY_ERROR, str(context.exception))

    def test_get_playlist_hash_success(self):
        urls = [self.URL_PLAYLIST_ONLY_1, self.URL_PLAYLIST_WITH_VIDEO, self.URL_PLAYLIST_WITH_INDEX]
        for url in urls:
            self.assertEqual(self.youtube_dl._get_playlist_hash(url), self.PLAYLIST_HASH)

    # --- Playlist Download Tests ---

    def test_download_whole_audio_playlist(self):
        mock_info = self.mock_extract(return_value={
            "title": self.TEST_PLAYLIST_NAME,
            "entries": self.TEST_PLAYLIST_FULL_ENTRIES
        })
        
        result_meta = self.youtube_playlists.download_whole_audio_playlist(self.URL_PLAYLIST_ONLY_1)
        mock_info.assert_called_once_with(self.PLAYLIST_HASH)
        self.assertEqual(result_meta[PlaylistInfo.TITLE.value], self.TEST_PLAYLIST_NAME)

    @patch.object(youtube_dl.YoutubeDlPlaylists, "download_whole_audio_playlist")
    @patch.object(youtube_dl.BaseConfigParser, "get_url_of_playlists")
    def test_download_all_config_playlists_audio(self, mock_get_urls, mock_download):
        mock_get_urls.return_value = self.TEST_PLAYLIST_URLS
        
        success = self.youtube_playlists.downolad_all_config_playlists_audio()
        
        self.assertTrue(success)
        self.assertEqual(mock_download.call_count, 2)
        mock_get_urls.assert_called_once()

    # --- Verification Tests ---

    @patch("os.listdir")
    @patch("os.path.isfile")
    @patch.object(youtube_dl.YoutubeDL, "if_video_exist_on_youtube")
    def test_verify_local_mp3_files_detection(self, mock_exists, mock_isfile, mock_listdir):
        mock_listdir.return_value = ["valid.mp3", "broken.mp3", "notes.txt"]
        mock_isfile.side_effect = lambda p: p.endswith(".mp3")
        # valid.mp3 exists on YT (True), broken.mp3 does not (False)
        mock_exists.side_effect = [True, False]

        invalid_files = self.youtube_dl.verify_local_mp3_files(self.test_dir, EasyID3ManagerMock)
        
        self.assertEqual(len(invalid_files), 1)
        self.assertIn("broken.mp3", invalid_files[0])


if __name__ == "__main__":
    main()