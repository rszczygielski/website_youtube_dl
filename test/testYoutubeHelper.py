import os
from unittest import TestCase, main
from unittest.mock import patch, MagicMock
from website_youtube_dl.flaskAPI.services.youtubeHelper import YoutubeHelper
from website_youtube_dl.common.youtubeDL import YoutubeDL
from website_youtube_dl.common.easyID3Manager import EasyID3Manager
from website_youtube_dl import create_app, socketio
from website_youtube_dl.config import TestingConfig
from website_youtube_dl.common.youtubeAPI import (
    SingleMedia,
    ResultOfYoutube,
    Format360p,
    FormatMP3,
)
from website_youtube_dl.common.youtubeLogKeys import YoutubeLogs
from website_youtube_dl.common.youtubeOptions import (
    YoutubeAudioOptions,
    YoutubeVideoOptions,
)


class TestYoutubeHelper(TestCase):
    """Unit tests for YoutubeHelper service."""

    # --- Test constants ---

    URL_SINGLE_VIDEO = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    URL_PLAYLIST_WITH_VIDEO = (
        "https://www.youtube.com/watch?v=ABsslEoL0-c"
        "&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    )

    DOWNLOAD_BASE_PATH = "/home/test_path/"

    TEST_FOLDER_PATH = os.path.abspath(__file__)
    SAMPLE_TITLE_SOCIETY = "Society"
    SAMPLE_ALBUM_INTO_THE_WILD = "Into The Wild"
    SAMPLE_ARTIST_E_VEDDER = "Eddie Vedder"
    SAMPLE_EXTENSION_MP4 = "mp4"
    SAMPLE_PLAYLIST_INDEX_1 = 1
    URL_SINGLE_VIDEO_ORIGINAL = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    SAMPLE_VIDEO_ID = "ABsslEoL0-c"
    SAMPLE_FULL_PATH_VIDEO = f"{TEST_FOLDER_PATH}/{SAMPLE_TITLE_SOCIETY}.{SAMPLE_EXTENSION_MP4}"
    SAMPLE_PLAYLIST_NAME = "playlistName"
    SAMPLE_GENERATED_HASH = "Kpdwgh"
    QUALITY_720P = "720"
    FORMAT_KEY_MP3 = "mp3"

    OUTPUT_TEMPLATE = TEST_FOLDER_PATH + f"{SAMPLE_TITLE_SOCIETY}.%(ext)s"
    AUDIO_OPTIONS = YoutubeAudioOptions(OUTPUT_TEMPLATE)
    VIDEO_OPTIONS = YoutubeVideoOptions(OUTPUT_TEMPLATE)
    FORMAT_MP3_INSTANCE = FormatMP3()
    FORMAT_360P_INSTANCE = Format360p()

    def setUp(self):
        app = create_app(TestingConfig)
        app.config_parser_manager = MagicMock()
        app.youtube_helper = YoutubeHelper(app.config_parser_manager)
        app.config_parser_manager.get_save_path = MagicMock(
            return_value=self.DOWNLOAD_BASE_PATH
        )
        app.config["TESTING"] = True
        self.socket_io_test_client = socketio.test_client(app)
        self.flask = app.test_client()
        self.app = app

        # create fresh SingleMedia and ResultOfYoutube instances per test
        self.single_media = SingleMedia(
            file_path=self.SAMPLE_FULL_PATH_VIDEO,
            title=self.SAMPLE_TITLE_SOCIETY,
            album=self.SAMPLE_ALBUM_INTO_THE_WILD,
            artist=self.SAMPLE_ARTIST_E_VEDDER,
            yt_hash=self.SAMPLE_VIDEO_ID,
            url=self.URL_SINGLE_VIDEO_ORIGINAL,
            extension=self.SAMPLE_EXTENSION_MP4,
        )
        
        self.single_media_mp3 = SingleMedia(
            file_path=self.SAMPLE_FULL_PATH_VIDEO.replace("mp4", "mp3"),
            title=self.SAMPLE_TITLE_SOCIETY,
            album=self.SAMPLE_ALBUM_INTO_THE_WILD,
            artist=self.SAMPLE_ARTIST_E_VEDDER,
            yt_hash=self.SAMPLE_VIDEO_ID,
            url=self.URL_SINGLE_VIDEO_ORIGINAL,
            extension="mp3",
        )

        self.result_of_youtube_single = ResultOfYoutube(self.single_media)
        self.result_of_youtube_single_mp3 = ResultOfYoutube(self.single_media_mp3)
        self.result_of_youtube_single_with_error = ResultOfYoutube()
        self.result_of_youtube_single_with_error.set_error(
            YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value)

    def _run_download_single_media_video_test(self,
                                              expected_result,
                                              expected_emit_count=0):
        with self.app.app_context():
            result = self.app.youtube_helper.download_single_video(
                self.URL_SINGLE_VIDEO, self.FORMAT_360P_INSTANCE)
        python_emit = self.socket_io_test_client.get_received()
        no_emit_data = len(python_emit)
        self.assertEqual(result, expected_result)
        self.assertEqual(no_emit_data, expected_emit_count)

    def mock_method(self, target, method_name, return_value=None, side_effect=None):
        patcher = patch.object(target,
                               method_name,
                               return_value=return_value,
                               side_effect=side_effect)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock

    def test_download_single_media_video(self):
        mock_get_video_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.VIDEO_OPTIONS)
        mock_download_video = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single)
        self._run_download_single_media_video_test(
            expected_result=self.SAMPLE_FULL_PATH_VIDEO,
            expected_emit_count=0
        )
        self.app.config_parser_manager.get_save_path.assert_called_once()
        mock_download_video.assert_called_once_with(
            self.URL_SINGLE_VIDEO, self.VIDEO_OPTIONS)
        mock_get_video_options.assert_called_once_with(self.FORMAT_360P_INSTANCE)

    def test_download_single_media_video_with_error(self):
        mock_get_video_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.VIDEO_OPTIONS)
        mock_download_video_error = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_with_error)
        self._run_download_single_media_video_test(
            expected_result=None,
            expected_emit_count=0
        )
        mock_download_video_error.assert_called_once_with(
            self.URL_SINGLE_VIDEO, self.VIDEO_OPTIONS)
        mock_get_video_options.assert_called_once_with(self.FORMAT_360P_INSTANCE)

    def _run_download_single_media_audio_test(self,
                                              expected_result,
                                              expected_emit_count=0):
        """
        Helper to test download_single_audio with different download return values and expected results.
        """
        with self.app.app_context():
            result = self.app.youtube_helper.download_single_audio(
                self.URL_SINGLE_VIDEO, self.FORMAT_MP3_INSTANCE)
        python_emit = self.socket_io_test_client.get_received()
        no_emit_data = len(python_emit)
        self.assertEqual(result, expected_result)
        self.assertEqual(no_emit_data, expected_emit_count)

    def test_download_single_media_audio(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.AUDIO_OPTIONS)
        mock_save_meta_data = self.mock_method(
            EasyID3Manager, "save_meta_data")
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_mp3)
        self._run_download_single_media_audio_test(
            expected_result=self.SAMPLE_FULL_PATH_VIDEO.replace("mp4", "mp3"),
            expected_emit_count=0
        )
        self.app.config_parser_manager.get_save_path.assert_called_once()
        mock_download_audio.assert_called_once_with(
            self.URL_SINGLE_VIDEO, self.AUDIO_OPTIONS)
        mock_save_meta_data.assert_called_once()
        mock_get_audio_options.assert_called_once_with(self.FORMAT_MP3_INSTANCE)

    def test_download_single_media_audio_with_error(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.AUDIO_OPTIONS)
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_with_error)
        self._run_download_single_media_audio_test(
            expected_result=None,
            expected_emit_count=0
        )
        mock_download_audio.assert_called_once_with(
            self.URL_SINGLE_VIDEO, self.AUDIO_OPTIONS)
        mock_get_audio_options.assert_called_once_with(self.FORMAT_MP3_INSTANCE)

    def _run_download_audio_from_playlist_test(self,
                                               expected_result,
                                               expected_emit_count=0):
        """
        Helper to test download_audio_from_playlist with different download return values and expected results.
        """
        with self.app.app_context():
            result = self.app.youtube_helper.download_audio_from_playlist(
                single_media_url=self.URL_SINGLE_VIDEO,
                req_format=self.FORMAT_MP3_INSTANCE,
                playlist_name=self.SAMPLE_PLAYLIST_NAME,
                index=1
            )
        python_emit = self.socket_io_test_client.get_received()
        no_emit_data = len(python_emit)
        self.assertEqual(result, expected_result)
        self.assertEqual(no_emit_data, expected_emit_count)

    def test_download_audio_from_playlist(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.AUDIO_OPTIONS)
        mock_save_meta_data = self.mock_method(
            EasyID3Manager, "save_meta_data")
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_mp3)
        self._run_download_audio_from_playlist_test(
            expected_result=self.SAMPLE_FULL_PATH_VIDEO.replace("mp4", "mp3"),
            expected_emit_count=0
        )
        mock_download_audio.assert_called_once_with(
            self.URL_SINGLE_VIDEO, self.AUDIO_OPTIONS)
        mock_save_meta_data.assert_called_once()
        mock_get_audio_options.assert_called_once_with(self.FORMAT_MP3_INSTANCE)

    def test_download_audio_from_playlist_with_error(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.AUDIO_OPTIONS)
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_with_error)
        self._run_download_audio_from_playlist_test(
            expected_result=None,
            expected_emit_count=0
        )
        mock_download_audio.assert_called_once_with(
            self.URL_SINGLE_VIDEO, self.AUDIO_OPTIONS)
        mock_get_audio_options.assert_called_once_with(self.FORMAT_MP3_INSTANCE)


if __name__ == "__main__":
    main()
