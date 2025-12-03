import os
from unittest import TestCase, main
from unittest.mock import patch, MagicMock
from website_youtube_dl.flaskAPI.services.youtubeHelper import YoutubeHelper
from website_youtube_dl.common.youtubeDL import YoutubeDL
from website_youtube_dl.common.easyID3Manager import EasyID3Manager
from website_youtube_dl import create_app, socketio
from website_youtube_dl.config import TestingConfig
from website_youtube_dl.common.youtubeAPI import (SingleMedia,
                                                  ResultOfYoutube,
                                                  Format360p,
                                                  FormatMP3)
from website_youtube_dl.common.youtubeLogKeys import YoutubeLogs

from website_youtube_dl.common.youtubeOptions import (YoutubeAudioOptions,
                                                      YoutubeVideoOptions)


class TestYoutubeHelper(TestCase):

    actual_youtube_url1 = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    actual_youtube_url2 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    test_path = "/home/test_path/"
    folder_path = os.path.abspath(__file__)
    test_title1 = "Society"
    test_album1 = "Into The Wild"
    test_artist1 = "Eddie Vedder"
    test_ext1 = "mp4"
    test_playlistIndex1 = 1
    test_original_url1 = 'https://www.youtube.com/watch?v=ABsslEoL0-c'
    testId1 = 'ABsslEoL0-c'
    test_full_path1 = f"{folder_path}/{test_title1}.{test_ext1}"
    test_playlist_name = "playlistName"
    test_generated_hash = "Kpdwgh"
    hd_720p = "720"
    mp3 = "mp3"

    out_template = folder_path + \
        f"{test_title1}.%(ext)s"
    audio_options = YoutubeAudioOptions(out_template)
    video_options = YoutubeVideoOptions(out_template)
    format_mp3 = FormatMP3()
    format_360p = Format360p()

    def setUp(self):
        app = create_app(TestingConfig)
        app.config_parser_manager = MagicMock()
        app.youtube_helper = YoutubeHelper(app.config_parser_manager)
        app.config_parser_manager.get_save_path = MagicMock(
            return_value=self.test_path)
        app.config["TESTING"] = True
        self.socket_io_test_client = socketio.test_client(app)
        self.flask = app.test_client()
        self.app = app

        # create fresh SingleMedia and ResultOfYoutube instances per test
        self.single_media = SingleMedia(file_path=self.test_full_path1,
                                        title=self.test_title1,
                                        album=self.test_album1,
                                        artist=self.test_artist1,
                                        yt_hash=self.testId1,
                                        url=self.test_original_url1,
                                        extension=self.test_ext1)
        
        self.single_media_mp3 = SingleMedia(file_path=self.test_full_path1.replace("mp4", "mp3"),
                                        title=self.test_title1,
                                        album=self.test_album1,
                                        artist=self.test_artist1,
                                        yt_hash=self.testId1,
                                        url=self.test_original_url1,
                                        extension="mp3")

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
                self.actual_youtube_url1, self.format_360p)
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
            YoutubeHelper, "get_youtube_download_options", return_value=self.video_options)
        mock_download_video = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single)
        self._run_download_single_media_video_test(
            expected_result=self.test_full_path1,
            expected_emit_count=0
        )
        self.app.config_parser_manager.get_save_path.assert_called_once()
        mock_download_video.assert_called_once_with(
            self.actual_youtube_url1, self.video_options)
        mock_get_video_options.assert_called_once_with(self.format_360p)

    def test_download_single_media_video_with_error(self):
        mock_get_video_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.video_options)
        mock_download_video_error = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_with_error)
        self._run_download_single_media_video_test(
            expected_result=None,
            expected_emit_count=0
        )
        mock_download_video_error.assert_called_once_with(
            self.actual_youtube_url1, self.video_options)
        mock_get_video_options.assert_called_once_with(self.format_360p)

    def _run_download_single_media_audio_test(self,
                                              expected_result,
                                              expected_emit_count=0):
        """
        Helper to test download_single_audio with different download return values and expected results.
        """
        with self.app.app_context():
            result = self.app.youtube_helper.download_single_audio(
                self.actual_youtube_url1, self.format_mp3)
        python_emit = self.socket_io_test_client.get_received()
        no_emit_data = len(python_emit)
        self.assertEqual(result, expected_result)
        self.assertEqual(no_emit_data, expected_emit_count)

    def test_download_single_media_audio(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.audio_options)
        mock_save_meta_data = self.mock_method(
            EasyID3Manager, "save_meta_data")
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_mp3)
        self._run_download_single_media_audio_test(
            expected_result=self.test_full_path1.replace("mp4", "mp3"),
            expected_emit_count=0
        )
        self.app.config_parser_manager.get_save_path.assert_called_once()
        mock_download_audio.assert_called_once_with(
            self.actual_youtube_url1, self.audio_options)
        mock_save_meta_data.assert_called_once()
        mock_get_audio_options.assert_called_once_with(self.format_mp3)

    def test_download_single_media_audio_with_error(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.audio_options)
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_with_error)
        self._run_download_single_media_audio_test(
            expected_result=None,
            expected_emit_count=0
        )
        mock_download_audio.assert_called_once_with(
            self.actual_youtube_url1, self.audio_options)
        mock_get_audio_options.assert_called_once_with(self.format_mp3)

    def _run_download_audio_from_playlist_test(self,
                                               expected_result,
                                               expected_emit_count=0):
        """
        Helper to test download_audio_from_playlist with different download return values and expected results.
        """
        with self.app.app_context():
            result = self.app.youtube_helper.download_audio_from_playlist(
                single_media_url=self.actual_youtube_url1,
                req_format=self.format_mp3,
                playlist_name=self.test_playlist_name,
                index=1
            )
        python_emit = self.socket_io_test_client.get_received()
        no_emit_data = len(python_emit)
        self.assertEqual(result, expected_result)
        self.assertEqual(no_emit_data, expected_emit_count)

    def test_download_audio_from_playlist(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.audio_options)
        mock_save_meta_data = self.mock_method(
            EasyID3Manager, "save_meta_data")
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_mp3)
        self._run_download_audio_from_playlist_test(
            expected_result=self.test_full_path1.replace("mp4", "mp3"),
            expected_emit_count=0
        )
        mock_download_audio.assert_called_once_with(
            self.actual_youtube_url1, self.audio_options)
        mock_save_meta_data.assert_called_once()
        mock_get_audio_options.assert_called_once_with(self.format_mp3)

    def test_download_audio_from_playlist_with_error(self):
        mock_get_audio_options = self.mock_method(
            YoutubeHelper, "get_youtube_download_options", return_value=self.audio_options)
        mock_download_audio = self.mock_method(
            YoutubeDL, "download_yt_media", return_value=self.result_of_youtube_single_with_error)
        self._run_download_audio_from_playlist_test(
            expected_result=None,
            expected_emit_count=0
        )
        mock_download_audio.assert_called_once_with(
            self.actual_youtube_url1, self.audio_options)
        mock_get_audio_options.assert_called_once_with(self.format_mp3)


if __name__ == "__main__":
    main()
