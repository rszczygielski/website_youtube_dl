from website_youtube_dl import create_app, socketio
import os
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from website_youtube_dl.common.youtubeLogKeys import YoutubeLogs
from website_youtube_dl.common import utils
from unittest import TestCase, main
from unittest.mock import patch, call
from website_youtube_dl.config import TestingConfig
from website_youtube_dl.flaskAPI import youtube
from website_youtube_dl.flaskAPI.youtubeHelper import YoutubeHelper
from website_youtube_dl.flaskAPI.flaskMedia import (FlaskSingleMedia,
                                                    FlaskPlaylistMedia,
                                                    FormatMP3,
                                                    Format360p,
                                                    Format480p,
                                                    Format720p,
                                                    Format1080p,
                                                    Format2160p)
from website_youtube_dl.flaskAPI.session import SessionDownloadData
from website_youtube_dl.common.youtubeDL import YoutubeDL
from website_youtube_dl.common.youtubeAPI import (SingleMedia,
                                                  PlaylistMedia,
                                                  ResultOfYoutube)
from website_youtube_dl.flaskAPI.emits import (DownloadMediaFinishEmit,
                                               SingleMediaInfoEmit,
                                               PlaylistMediaInfoEmit)
from website_youtube_dl.common.easyID3Manager import EasyID3Manager
from website_youtube_dl.common.youtubeDataKeys import PlaylistInfo, MediaInfo
from website_youtube_dl.flaskAPI import emits
from website_youtube_dl.flaskAPI import youtubeModifyPlaylist
from test.socketClientMock import SessionClientMock
from test.emitData import EmitData
from unittest.mock import MagicMock


class testYoutubeWeb(TestCase):
    download_media_finish_emit = DownloadMediaFinishEmit()
    single_media_info_emit = SingleMediaInfoEmit()
    playlist_media_info_emit = PlaylistMediaInfoEmit()

    actual_youtube_url1 = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    actual_youtube_url2 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    actual_youtube_playlist_url1 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"

    folder_path = os.path.abspath(__file__)

    test_playlist_name = "playlistName"
    test_title1 = "Society"
    test_album1 = "Into The Wild"
    test_artist1 = "Eddie Vedder"
    test_ext1 = "webm"
    test_playlistIndex1 = 1
    test_original_url1 = 'https://www.youtube.com/watch?v=ABsslEoL0-c'
    testId1 = 'ABsslEoL0-c'
    test_full_path1 = f"{folder_path}/{test_title1}.webm"

    test_title2 = 'Hard Sun'
    test_artist2 = "Eddie Vedder"
    test_ext2 = "webm"
    test_playlist_index2 = 2
    test_original_url2 = 'https://www.youtube.com/watch?v=_EZUfnMv3Lg'
    testId2 = '_EZUfnMv3Lg'
    test_full_path2 = f"{folder_path}/{test_title2}.webm"

    playlist_url_str = "playlistUrl"
    data_str = "data"
    test_path = "/home/test_path/"
    track_list = "trackList"
    test_generated_hash = "Kpdwgh"
    error = "error"
    hd_720p = "720"
    mp3 = "mp3"

    format_mp3 = FormatMP3()
    format_720p = Format720p()
    format_360p = Format360p()
    format_480p = Format480p()
    format_1080p = Format1080p()
    format_2160p = Format2160p()

    path_files = [os.path.join(test_path, test_title1),
                  os.path.join(test_path, test_title2)]

    fileNotFoundError = f"File {test_path}  doesn't exist - something went wrong"

    sucessEmitData1 = {'title': 'Society',
                       'artist': 'Eddie Vedder',
                       'webpage_url': 'https://www.youtube.com/watch?v=ABsslEoL0-c'}

    single_media1 = SingleMedia(file_name=test_full_path1,
                                title=test_title1,
                                album=test_album1,
                                artist=test_artist1,
                                yt_hash=testId1,
                                url=test_original_url1,
                                extension=test_ext1)

    single_media2 = SingleMedia(file_name=test_full_path2,
                                title=test_title2,
                                album=test_album1,
                                artist=test_artist2,
                                yt_hash=testId2,
                                url=test_original_url2,
                                extension=test_ext2)

    expected_result_single_medi_info = {MediaInfo.TITLE.value:  test_title1,
                                        MediaInfo.ARTIST.value: test_artist1,
                                        MediaInfo.URL.value: test_original_url1}

    expected_result_playlist_media_info = {test_playlist_name: test_playlist_name,
                                           track_list: [{PlaylistInfo.TITLE.value: test_title1,
                                                         PlaylistInfo.URL.value: testId1},
                                                        {PlaylistInfo.TITLE.value: test_title2,
                                                         PlaylistInfo.URL.value: testId2}]}

    playlist_media = PlaylistMedia(playlist_name=test_playlist_name,
                                   media_from_playlist_list=[single_media1, single_media2])

    result_of_youtube_single = ResultOfYoutube(single_media1)
    result_of_youtube_single_with_error1 = ResultOfYoutube()
    result_of_youtube_single_with_error1.set_error(
        YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value)

    result_of_youtube_playlist = ResultOfYoutube(playlist_media)
    result_of_youtube_playlist_with_error = ResultOfYoutube()
    result_of_youtube_playlist_with_error.set_error(
        YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value)

    def setUp(self):
        app = create_app(TestingConfig)
        app.config_parser_manager = MagicMock()
        app.config_parser_manager.get_save_path = MagicMock(
            return_value=self.test_path)
        app.config["TESTING"] = True
        session_dict = {}
        self.socket_io_test_client = socketio.test_client(app)
        self.flask = app.test_client()
        self.app = app
        self.app.session = SessionClientMock(session_dict)

    def create_flask_single_media(self, data):
        title = data["title"]
        artist = data["artist"]
        url = data["original_url"]
        return FlaskSingleMedia(title, artist, url)

    def create_flask_playlist_media(self, data):
        flask_single_media_list = []
        for track in data["trackList"]:
            flask_single_media_list.append(
                self.create_flask_single_media(track))
        return FlaskPlaylistMedia.init_from_playlist_media(data["playlistName"], flask_single_media_list)

    @patch.object(youtube, "send_file")
    @patch.object(os.path, "isfile", return_value=True)
    def test_download_file(self, is_file_mock, send_file_mock):
        session_data = SessionDownloadData(self.test_path)
        test_key = "test_key"
        self.app.session.add_elem_to_session(test_key, session_data)
        response = self.flask.get('/downloadFile/test_key')
        self.assertEqual(len(is_file_mock.mock_calls), 2)
        send_file_mock.assert_called_once_with(
            self.test_path, as_attachment=True)
        self.assertEqual(response.status_code, 200)

    def test_session_wrong_path(self):
        with self.assertRaises(FileNotFoundError) as context:
            session_data = SessionDownloadData(self.test_path)
            self.assertTrue(
                self.fileNotFoundError in str(context.exception))

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(youtube, "download_correct_data")
    def test_socket_download_server_success(self, mock_download_data, is_file):
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, {
                MainYoutubeKeys.YOUTUBE_URL.value: self.actual_youtube_url1,
                MainYoutubeKeys.DOWNLOAD_TYP.value: self.mp3
            }
        )
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        self.assertEqual(len(python_emit), 1)
        mock_download_data.assert_called_once()
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.data_str, emit_data.data)
        self.assertIn(MainYoutubeKeys.HASH.value,
                      emit_data.data[self.data_str])

    def test_socket_download_server_no_download_type(self):
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, {
                MainYoutubeKeys.YOUTUBE_URL.value: self.actual_youtube_url1
            }
        )
        python_emit = self.socket_io_test_client.get_received()
        self.assertEqual(len(python_emit), 1)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertIn(MainYoutubeKeys.NAME.value, received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(MainYoutubeKeys.ERROR.value, emit_data.data)
        self.assertEqual(emit_data.data[MainYoutubeKeys.ERROR.value],
                         YoutubeLogs.NO_FORMAT.value)

    def test_socket_download_server_no_youtube_url(self):
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, {
                MainYoutubeKeys.YOUTUBE_URL.value: "",
                MainYoutubeKeys.DOWNLOAD_TYP.value: self.mp3
            }
        )
        python_emit = self.socket_io_test_client.get_received()
        self.assertEqual(len(python_emit), 1)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertIn(MainYoutubeKeys.NAME.value, received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(MainYoutubeKeys.ERROR.value, emit_data.data)
        self.assertEqual(emit_data.data[MainYoutubeKeys.ERROR.value],
                         YoutubeLogs.NO_URL.value)

    @patch.object(youtube, "generate_hash", return_value=test_generated_hash)
    @patch.object(SessionDownloadData, "set_session_download_data")
    @patch.object(youtube, "download_correct_data")
    @patch.object(youtube, "get_format_instance", return_value=format_mp3)
    def test_socket_download_playlist_and_video_hash(self,
                                                     mock_get_format,
                                                     mock_download_data,
                                                     mock_set_session_download_data,
                                                     mock_generate_hash):
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, {
                MainYoutubeKeys.YOUTUBE_URL.value: self.actual_youtube_url2,
                MainYoutubeKeys.DOWNLOAD_TYP.value: self.mp3
            }
        )
        mock_generate_hash.assert_called_once()
        mock_set_session_download_data.assert_called_once()
        python_emit = self.socket_io_test_client.get_received()
        self.assertEqual(len(python_emit), 1)
        mock_get_format.assert_called_once_with(self.mp3)
        mock_download_data.assert_called_once_with(self.actual_youtube_url2,
                                                   self.format_mp3,
                                                   False)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertIn(MainYoutubeKeys.NAME.value, received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        expecte_data = self.download_media_finish_emit.convert_data_to_message(
            self.test_generated_hash)
        expected_restult = {self.data_str: expecte_data}
        self.assertEqual(emit_data.data, expected_restult)

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(youtube, "download_correct_data")
    def test_socket_download_playlist(self, mock_download_data, is_file):
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, {
                MainYoutubeKeys.YOUTUBE_URL.value: self.actual_youtube_playlist_url1,
                MainYoutubeKeys.DOWNLOAD_TYP.value: self.mp3
            }
        )
        python_emit = self.socket_io_test_client.get_received()
        is_file.assert_called_once()
        self.assertEqual(len(python_emit), 1)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        mock_download_data.assert_called_once()
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.data_str, emit_data.data)
        self.assertIn(MainYoutubeKeys.HASH.value,
                      emit_data.data[self.data_str])

    @patch.object(youtube, "download_correct_data", return_value=None)
    def test_socket_download_fail(self, mock_download_data):
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, {
                MainYoutubeKeys.YOUTUBE_URL.value: self.actual_youtube_url1,
                MainYoutubeKeys.DOWNLOAD_TYP.value: self.mp3
            }
        )
        python_emit = self.socket_io_test_client.get_received()
        self.assertEqual(len(python_emit), 1)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(MainYoutubeKeys.ERROR.value, emit_data.data)
        mock_download_data.assert_called_once()

    @patch.object(YoutubeDL,
                  "request_single_media_info", return_value=result_of_youtube_single)
    def test_send_emit_single_media_info_from_youtube(self,
                                                      mock_request_single_media):
        with self.app.app_context():
            result = youtube.send_emit_single_media_info_from_youtube(
                self.actual_youtube_url1)
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        mock_request_single_media.assert_called_once_with(
            self.actual_youtube_url1)
        self.assertEqual(emit_data.data[self.data_str],
                         self.expected_result_single_medi_info)
        self.assertEqual(self.single_media_info_emit.emit_msg,
                         emit_data.emit_name)
        self.assertTrue(result)

    @patch.object(YoutubeHelper, "request_single_media_info",
                  return_value=result_of_youtube_single_with_error1)
    def test_send_emit_single_media_info_with_error(self,
                                                    mock_request_single_media):
        with self.app.app_context():
            result = youtube.send_emit_single_media_info_from_youtube(
                self.actual_youtube_url1)
        python_emit = self.socket_io_test_client.get_received()
        mock_request_single_media.assert_called_once_with(
            self.actual_youtube_url1)
        no_emit_data = len(python_emit)
        self.assertFalse(result)
        self.assertEqual(no_emit_data, 0)

    @patch.object(YoutubeDL, "request_playlist_media_info",
                  return_value=result_of_youtube_playlist)
    def test_send_emit_playlist_media(self, mock_request_single_media):
        with self.app.app_context():
            result = youtube.send_emit_playlist_media(
                self.actual_youtube_playlist_url1)
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        mock_request_single_media.assert_called_once_with(
            self.actual_youtube_playlist_url1)
        self.assertEqual(emit_data.data[self.data_str],
                         self.expected_result_playlist_media_info)
        self.assertEqual(self.playlist_media_info_emit.emit_msg,
                         emit_data.emit_name)
        self.assertTrue(result)

    @patch.object(YoutubeDL,
                  "request_playlist_media_info", return_value=result_of_youtube_playlist_with_error)
    def test_send_emit_playlist_media_with_error(self,
                                                 mock_request_single_media):
        with self.app.app_context():
            result = youtube.send_emit_playlist_media(
                self.actual_youtube_playlist_url1)
        python_emit = self.socket_io_test_client.get_received()
        no_emit_data = len(python_emit)
        self.assertFalse(result)
        self.assertEqual(no_emit_data, 0)

    @patch.object(utils, "zip_all_files_in_list",
                  return_value=f"/home/test_path/{test_playlist_name}")
    @patch.object(youtube, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubeHelper, "download_single_video", return_value="full_path_test")
    @patch.object(utils, "get_files_from_dir", return_value=path_files)
    def test_download_tracks_from_playlist_video(self, mockGetFilesFromDir,
                                                 mockDownloadVideo,
                                                 mockSendEmitPlaylist,
                                                 mockZipFiles):
        with self.app.app_context():
            result = youtube.download_tracks_from_playlist(self.actual_youtube_playlist_url1,
                                                           self.format_720p)
        print("TEST")
        mockGetFilesFromDir.assert_called_once_with(self.test_path)
        mockSendEmitPlaylist.assert_called_once()
        calls = mockDownloadVideo.mock_calls
        self.assertEqual(call(single_media_url=self.testId1, video_type='720'),
                         calls[0])
        self.assertEqual(call(single_media_url=self.testId2, video_type='720'),
                         calls[1])
        self.assertEqual(2, mockDownloadVideo.call_count)
        self.assertEqual(result, f"/home/test_path/{self.test_playlist_name}")
        mockZipFiles.assert_called_once()

    @patch.object(utils, "zip_all_files_in_list",
                  return_value=f"/home/test_path/{test_playlist_name}")
    @patch.object(youtube, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubeHelper, "download_audio_from_playlist", return_value="full_path_test")
    @patch.object(utils, "get_files_from_dir", return_value=path_files)
    def test_download_tracks_from_playlist_audio(self, mockGetFilesFromDir,
                                                 mock_download_audio,
                                                 mockSendEmitPlaylist,
                                                 mockZipFiles):
        with self.app.app_context():
            result = youtube.download_tracks_from_playlist(
                self.actual_youtube_playlist_url1, self.format_mp3)
        mockSendEmitPlaylist.assert_called_once()
        mockGetFilesFromDir.assert_called_once_with(self.test_path)
        calls = mock_download_audio.mock_calls
        self.assertEqual(call(single_media_url=self.testId1,
                              playlist_name=self.test_playlist_name,
                              index="0"),
                         calls[0])
        self.assertEqual(call(single_media_url=self.testId2,
                              playlist_name=self.test_playlist_name,
                              index="1"),
                         calls[1])
        self.assertEqual(2, mock_download_audio.call_count)
        self.assertEqual(result, f"/home/test_path/{self.test_playlist_name}")
        mockZipFiles.assert_called_once()

    @patch.object(utils, "zip_all_files_in_list", return_value=f"/home/test_path/{test_playlist_name}")
    @patch.object(youtube, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubeHelper, "download_single_video", return_value="full_path_test")
    @patch.object(utils, "get_files_from_dir", return_value=["file1", "file2"])
    def test_download_tracks_from_playlist_1080p(self, mock_get_files, mock_download_video, mock_send_emit, mock_zip):
        with self.app.app_context():
            result = youtube.download_tracks_from_playlist(
                self.actual_youtube_playlist_url1, self.format_1080p)
        mock_get_files.assert_called_once_with(self.test_path)
        mock_send_emit.assert_called_once()
        self.assertEqual(mock_download_video.call_count, 2)
        self.assertEqual(result, f"/home/test_path/{self.test_playlist_name}")
        mock_zip.assert_called_once()

    @patch.object(utils, "zip_all_files_in_list", return_value=f"/home/test_path/{test_playlist_name}")
    @patch.object(youtube, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubeHelper, "download_single_video", return_value="full_path_test")
    @patch.object(utils, "get_files_from_dir", return_value=["file1", "file2"])
    def test_download_tracks_from_playlist_2160p(self, mock_get_files, mock_download_video, mock_send_emit, mock_zip):
        with self.app.app_context():
            result = youtube.download_tracks_from_playlist(
                self.actual_youtube_playlist_url1, self.format_2160p)
        mock_get_files.assert_called_once_with(self.test_path)
        mock_send_emit.assert_called_once()
        self.assertEqual(mock_download_video.call_count, 2)
        self.assertEqual(result, f"/home/test_path/{self.test_playlist_name}")
        mock_zip.assert_called_once()

    @patch.object(youtube, "send_emit_playlist_media",
                  return_value=None)
    def testdownload_tracks_from_playlist_video_with_error(self,
                                                           mock_request_playlist_media_info):
        with self.app.app_context():
            result = youtube.download_tracks_from_playlist(
                self.actual_youtube_playlist_url1, self.hd_720p)
        self.assertFalse(result)
        mock_request_playlist_media_info.assert_called_once_with(
            self.actual_youtube_playlist_url1)

    @patch.object(youtube, "send_emit_playlist_media",
                  return_value=None)
    def testdownload_tracks_from_playlist_audio_with_error(self,
                                                           mock_request_playlist_media_info):
        with self.app.app_context():
            result = youtube.download_tracks_from_playlist(
                self.actual_youtube_playlist_url1, None)
        self.assertFalse(result)
        mock_request_playlist_media_info.assert_called_once_with(
            self.actual_youtube_playlist_url1)

    @patch.object(youtube, "download_tracks_from_playlist",
                  return_value="video_playlist_path")
    def test_download_correct_data_playlist_video(self, mock_download_playlist):
        with self.app.app_context():
            result = youtube.download_correct_data(
                self.actual_youtube_url1, self.format_480p, True)
        self.assertEqual(result, "video_playlist_path")
        mock_download_playlist.assert_called_once_with(youtube_url=self.actual_youtube_url1,
                                                       format_instance=self.format_480p)

    @patch.object(youtube, "download_tracks_from_playlist",
                  return_value="/home/music/audio_playlist_path")
    def test_download_correct_data_playlist_audio(self, mock_download_playlist):
        with self.app.app_context():
            result = youtube.download_correct_data(
                self.actual_youtube_url1, self.format_mp3, True)
        self.assertEqual(result, "/home/music/audio_playlist_path")
        mock_download_playlist.assert_called_once_with(youtube_url=self.actual_youtube_url1,
                                                       format_instance=self.format_mp3)

    @patch.object(youtube, "send_emit_single_media_info_from_youtube",
                  return_value=True)
    @patch.object(YoutubeHelper, "download_single_video",
                  return_value="/home/music/video_single_path")
    def test_download_correct_data_single_video(self,
                                                mock_download_single_media, mock_send_emit_single_media):
        with self.app.app_context():
            result = youtube.download_correct_data(
                self.actual_youtube_url1, self.format_360p, False)
        mock_send_emit_single_media.assert_called_once_with(
            self.actual_youtube_url1)
        self.assertEqual(result, "/home/music/video_single_path")
        mock_download_single_media.assert_called_once_with(single_media_url=self.actual_youtube_url1,
                                                           video_type=self.format_360p.get_format_type())

    @patch.object(youtube, "send_emit_single_media_info_from_youtube",
                  return_value=True)
    @patch.object(YoutubeHelper, "download_single_audio",
                  return_value="/home/music/audio_single_path")
    def test_download_correct_data_single_audio(self,
                                                mock_download_single_media, mock_send_emit_single_media):
        with self.app.app_context():
            result = youtube.download_correct_data(
                self.actual_youtube_url1, self.format_mp3, False)
        mock_send_emit_single_media.assert_called_once_with(
            self.actual_youtube_url1)
        self.assertEqual(result, "/home/music/audio_single_path")
        mock_download_single_media.assert_called_once_with(
            single_media_url=self.actual_youtube_url1)

    def test_yourube_html(self):
        response = self.flask.get("/youtube.html")
        self.assertIn('<title>YouTube</title>', str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_index_html(self):
        response1 = self.flask.get("/")
        response2 = self.flask.get("/index.html")
        response3 = self.flask.get('/example')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)

    def test_wrong_yourube_html(self):
        response = self.flask.get("/youtubetest.html")
        self.assertEqual(response.status_code, 404)

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(youtubeModifyPlaylist, "generate_hash",
                  return_value="test_hash")
    @patch.object(youtubeModifyPlaylist, "download_tracks_from_playlist",
                  return_value="video_playlist_path")
    def test_download_config_playlist(self, mock_download_playlist,
                                      mock_generate_hash,
                                      mock_is_file):
        self.app.config_parser_manager.get_playlist_url = MagicMock(
            return_value=self.actual_youtube_playlist_url1)
        self.socket_io_test_client.emit(
            "downloadFromConfigFile", {
                "playlistToDownload": self.test_playlist_name
            }
        )
        mock_download_playlist.assert_called_once_with(
            youtube_url=self.actual_youtube_playlist_url1, video_type=None)
        mock_is_file.assert_called_once()
        mock_generate_hash.assert_called_once()
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(emit_data.emit_name,
                         self.download_media_finish_emit.emit_msg)
        self.assertEqual(
            emit_data.data[self.data_str], self.download_media_finish_emit.convert_data_to_message("test_hash"))

    @patch.object(youtubeModifyPlaylist, "download_tracks_from_playlist",
                  return_value=None)
    def test_download_config_playlist_with_error(self, mock_download_playlist):
        self.app.config_parser_manager.get_playlist_url = MagicMock(
            return_value=self.actual_youtube_playlist_url1)
        self.socket_io_test_client.emit(
            "downloadFromConfigFile", {
                "playlistToDownload": self.test_playlist_name
            }
        )
        self.app.config_parser_manager.get_playlist_url.assert_called_once_with(
            self.test_playlist_name)
        mock_download_playlist.assert_called_once_with(
            youtube_url=self.actual_youtube_playlist_url1, video_type=None)
        python_emit = self.socket_io_test_client.get_received()
        self.assertEqual(len(python_emit), 0)

    def test_add_playlist_config(self):
        self.app.config_parser_manager.add_playlist = MagicMock()
        self.app.config_parser_manager.get_playlists = MagicMock(
            return_value={
                "test_playlist": "url1",
                self.test_playlist_name: "url2"
            })
        self.socket_io_test_client.emit(
            "addPlaylist", {
                "playlistName": self.test_playlist_name,
                "playlistURL": self.actual_youtube_playlist_url1
            }
        )
        self.app.config_parser_manager.add_playlist.assert_called_once_with(
            self.test_playlist_name, self.actual_youtube_playlist_url1)
        self.app.config_parser_manager.get_playlists.assert_called_once()
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(emit_data.emit_name, "uploadPlaylists")
        self.assertEqual(
            emit_data.data, {self.data_str: {'playlistList': ["test_playlist", self.test_playlist_name]}})

    def test_delete_playlist_config(self):
        self.app.config_parser_manager.deletePlaylist = MagicMock()
        self.app.config_parser_manager.get_playlists = MagicMock(
            return_value={
                "test_playlist": "url1",
                self.test_playlist_name: "url2"
            })
        self.socket_io_test_client.emit(
            "deletePlaylist", {
                "playlistToDelete": self.test_playlist_name,
            }
        )
        self.app.config_parser_manager.deletePlaylist.assert_called_once_with(
            self.test_playlist_name)
        self.app.config_parser_manager.get_playlists.assert_called_once()
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(emit_data.emit_name, "uploadPlaylists")
        self.assertEqual(
            emit_data.data, {self.data_str: {'playlistList': ["test_playlist", self.test_playlist_name]}})

    def test_playlist_config_url(self):
        self.app.config_parser_manager.get_playlist_url = MagicMock(
            return_value=self.test_playlist_name)
        self.socket_io_test_client.emit(
            "playlistName", {
                "playlistName": self.test_playlist_name,
            }
        )
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        self.app.config_parser_manager.get_playlist_url.assert_called_once()
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.playlist_url_str, emit_data.emit_name)
        self.assertEqual(
            emit_data.data, {self.data_str: {self.playlist_url_str:  self.test_playlist_name}})

    def test_modify_playlist_html(self):
        response = self.flask.get("/modify_playlist.html")
        self.assertEqual(response.status_code, 200)


class TestEmits(TestCase):
    playlist_name = "playlistName"
    track_list = "trackList"
    title = "title"
    url = "url"
    artist = "artist"

    playlist_mediaTest = FlaskPlaylistMedia.init_from_playlist_media(testYoutubeWeb.test_playlist_name,
                                                                     [testYoutubeWeb.single_media1,
                                                                      testYoutubeWeb.single_media2])

    singleMedia = FlaskSingleMedia(testYoutubeWeb.test_title1,
                                   testYoutubeWeb.test_artist1,
                                   testYoutubeWeb.test_original_url1)

    def setUp(self):
        self.playlist_media_info_emits = emits.PlaylistMediaInfoEmit()
        self.single_media_info_emits = emits.SingleMediaInfoEmit()

    def test_convert_data_to_massage_playlist(self):
        result = self.playlist_media_info_emits.convert_data_to_message(
            self.playlist_mediaTest)
        self.assertEqual(
            result, testYoutubeWeb.expected_result_playlist_media_info)

    def test_convert_data_to_massage_single(self):
        result = self.single_media_info_emits.convert_data_to_message(
            testYoutubeWeb.single_media1)
        self.assertEqual(
            result, testYoutubeWeb.expected_result_single_medi_info)


if __name__ == "__main__":
    main()
