from website_youtube_dl import create_app, socketio
import os
from website_youtube_dl.common.youtube_data_keys import MainYoutubeKeys
from website_youtube_dl.common.youtube_log_keys import YoutubeLogs
from unittest import TestCase, main, skip
from unittest.mock import patch, call
from website_youtube_dl.config import TestingConfig
from website_youtube_dl.flask_api.routes import youtube, youtube_playlists
from website_youtube_dl.flask_api.handlers import youtube_emit
from website_youtube_dl.flask_api.sockets import base_namespace
from website_youtube_dl.flask_api.handlers import youtube_download
from website_youtube_dl.flask_api.services.youtube_downloader import YoutubePlaylistDownloader
from website_youtube_dl.flask_api.services.flask_media import (FlaskSingleMedia,
                                                             FlaskPlaylistMedia)
from website_youtube_dl.common.youtube_api import (FormatMP3,
                                                  Format360p,
                                                  Format480p,
                                                  Format720p,
                                                  Format1080p,
                                                  Format2160p)
from website_youtube_dl.flask_api.sockets.session_data import DownloadFileInfo
from website_youtube_dl.flask_api.sockets.socket_manager import SocketManager
from website_youtube_dl.common.youtube_dl import YoutubeDL
from website_youtube_dl.common.youtube_api import (SingleMedia,
                                                  PlaylistMedia,
                                                  ResultOfYoutube)
from website_youtube_dl.flask_api.sockets.emits import (DownloadMediaFinishEmit,
                                                       SingleMediaInfoEmit,
                                                       PlaylistMediaInfoEmit)
from website_youtube_dl.common.youtube_data_keys import PlaylistInfo, MediaInfo
from website_youtube_dl.flask_api.sockets import emits
from test.emitData import EmitData
from unittest.mock import MagicMock
from website_youtube_dl.common.youtube_options import (YoutubeAudioOptions,
                                                      YoutubeVideoOptions)


class TestYoutubeWeb(TestCase):
    # Emit helpers used across tests
    download_media_finish_emit = DownloadMediaFinishEmit()
    single_media_info_emit = SingleMediaInfoEmit()
    playlist_media_info_emit = PlaylistMediaInfoEmit()

    # --- Test constants ---

    URL_SINGLE_VIDEO = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    URL_VIDEO_IN_PLAYLIST = (
        "https://www.youtube.com/watch?v=ABsslEoL0-c"
        "&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    )
    URL_PLAYLIST = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"

    TEST_FOLDER_PATH = os.path.abspath(__file__)

    SAMPLE_PLAYLIST_NAME = "playlistName"
    SAMPLE_TITLE_SOCIETY = "Society"
    SAMPLE_ALBUM_INTO_THE_WILD = "Into The Wild"
    SAMPLE_ARTIST_E_VEDDER = "Eddie Vedder"
    SAMPLE_EXTENSION_WEBM = "webm"
    SAMPLE_PLAYLIST_INDEX_1 = 1
    URL_SINGLE_VIDEO_ORIGINAL = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    SAMPLE_VIDEO_ID_1 = "ABsslEoL0-c"
    SAMPLE_FULL_PATH_1 = f"{TEST_FOLDER_PATH}/{SAMPLE_TITLE_SOCIETY}.webm"

    SAMPLE_TITLE_HARD_SUN = "Hard Sun"
    SAMPLE_ARTIST_HARD_SUN = "Eddie Vedder"
    SAMPLE_EXTENSION_WEBM_2 = "webm"
    SAMPLE_PLAYLIST_INDEX_2 = 2
    URL_SINGLE_VIDEO_ORIGINAL_2 = "https://www.youtube.com/watch?v=_EZUfnMv3Lg"
    SAMPLE_VIDEO_ID_2 = "_EZUfnMv3Lg"
    SAMPLE_FULL_PATH_2 = f"{TEST_FOLDER_PATH}/{SAMPLE_TITLE_HARD_SUN}.webm"

    KEY_PLAYLIST_URL = "playlistUrl"
    KEY_DATA = "data"
    DOWNLOAD_BASE_PATH = "/home/test_path/"
    KEY_TRACK_LIST = "trackList"
    SAMPLE_GENERATED_HASH = "Kpdwgh"
    KEY_ERROR = "error"
    QUALITY_720P = "720"
    FORMAT_KEY_MP3 = "mp3"

    FORMAT_MP3_INSTANCE = FormatMP3()
    FORMAT_720P_INSTANCE = Format720p()
    FORMAT_360P_INSTANCE = Format360p()
    FORMAT_480P_INSTANCE = Format480p()
    FORMAT_1080P_INSTANCE = Format1080p()
    FORMAT_2160P_INSTANCE = Format2160p()

    OUTPUT_TEMPLATE = TEST_FOLDER_PATH + f"{SAMPLE_TITLE_SOCIETY}.%(ext)s"
    AUDIO_OPTIONS = YoutubeAudioOptions(OUTPUT_TEMPLATE)
    VIDEO_OPTIONS = YoutubeVideoOptions(OUTPUT_TEMPLATE)

    PATH_FILES = [
        os.path.join(DOWNLOAD_BASE_PATH, SAMPLE_TITLE_SOCIETY),
        os.path.join(DOWNLOAD_BASE_PATH, SAMPLE_TITLE_HARD_SUN),
    ]

    FILE_NOT_FOUND_ERROR = (
        f"File {DOWNLOAD_BASE_PATH}  doesn't exist - something went wrong"
    )

    SUCCESS_EMIT_SAMPLE = {
        "title": "Society",
        "artist": "Eddie Vedder",
        "webpage_url": "https://www.youtube.com/watch?v=ABsslEoL0-c",
    }

    single_media1 = SingleMedia(
        file_path=SAMPLE_FULL_PATH_1,
        title=SAMPLE_TITLE_SOCIETY,
        album=SAMPLE_ALBUM_INTO_THE_WILD,
        artist=SAMPLE_ARTIST_E_VEDDER,
        yt_hash=SAMPLE_VIDEO_ID_1,
        url=URL_SINGLE_VIDEO_ORIGINAL,
        extension=SAMPLE_EXTENSION_WEBM,
    )

    single_media2 = SingleMedia(
        file_path=SAMPLE_FULL_PATH_2,
        title=SAMPLE_TITLE_HARD_SUN,
        album=SAMPLE_ALBUM_INTO_THE_WILD,
        artist=SAMPLE_ARTIST_HARD_SUN,
        yt_hash=SAMPLE_VIDEO_ID_2,
        url=URL_SINGLE_VIDEO_ORIGINAL_2,
        extension=SAMPLE_EXTENSION_WEBM_2,
    )

    expected_result_single_medi_info = {
        MediaInfo.TITLE.value: SAMPLE_TITLE_SOCIETY,
        MediaInfo.ARTIST.value: SAMPLE_ARTIST_E_VEDDER,
        MediaInfo.URL.value: URL_SINGLE_VIDEO_ORIGINAL,
    }

    expected_result_playlist_media_info = {
        SAMPLE_PLAYLIST_NAME: SAMPLE_PLAYLIST_NAME,
        KEY_TRACK_LIST: [
            {
                PlaylistInfo.TITLE.value: SAMPLE_TITLE_SOCIETY,
                PlaylistInfo.URL.value: SAMPLE_VIDEO_ID_1,
            },
            {
                PlaylistInfo.TITLE.value: SAMPLE_TITLE_HARD_SUN,
                PlaylistInfo.URL.value: SAMPLE_VIDEO_ID_2,
            },
        ],
    }

    playlist_media = PlaylistMedia(
        playlist_name=SAMPLE_PLAYLIST_NAME,
        media_from_playlist_list=[single_media1, single_media2],
    )

    result_of_youtube_single = ResultOfYoutube(single_media1)
    result_of_youtube_single_with_error1 = ResultOfYoutube()
    result_of_youtube_single_with_error1.set_error(
        YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value)

    result_of_youtube_playlist = ResultOfYoutube(playlist_media)
    result_of_youtube_playlist_with_error = ResultOfYoutube()
    result_of_youtube_playlist_with_error.set_error(
        YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value)

    def setUp(self):
        # --- PATCH zip_all_files_in_list ---
        self.zip_patcher = patch.object(
            youtube_download, "zip_all_files_in_list",
            return_value=f"/home/test_path/{self.SAMPLE_PLAYLIST_NAME}"
        )
        self.mock_zip = self.zip_patcher.start()
        self.addCleanup(self.zip_patcher.stop)

        # --- PATCH os.path.isfile ---
        self.isfile_patcher = patch.object(os.path, "isfile", return_value=True)
        self.mock_isfile = self.isfile_patcher.start()
        self.addCleanup(self.isfile_patcher.stop)

        app = create_app(TestingConfig)
        app.config_parser_manager = MagicMock()
        app.config_parser_manager.get_save_path = MagicMock(
            return_value=self.DOWNLOAD_BASE_PATH)
        app.config["TESTING"] = True
        # Connect explicitly to namespaces (the app registers '/youtube' and '/playlists')
        self.youtube_ns = "/youtube"
        self.playlists_ns = "/playlists"
        self.socket_io_test_client = socketio.test_client(app, namespace=self.youtube_ns)
        self.flask = app.test_client()
        self.app = app
        self.app.socket_manager = SocketManager()
        # Mirror frontend behavior: map Socket.IO session -> browser id before using any handlers
        self.user_browser_id = "test-browser-id"
        self.socket_io_test_client.emit(
            "userSession",
            {"userBrowserId": self.user_browser_id},
            namespace=self.youtube_ns
        )
        # Drain any acks/events produced during session init (usually none)
        self.socket_io_test_client.get_received(namespace=self.youtube_ns)

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
    def test_download_file(self, send_file_mock):
        session_data = DownloadFileInfo(self.DOWNLOAD_BASE_PATH, False)
        test_key = "test_key"
        self.app.socket_manager.add_message_to_session_hash(
            test_key, session_data)
        response = self.flask.get('/downloadFile/test_key')
        self.assertEqual(len(self.mock_isfile.mock_calls), 1)
        send_file_mock.assert_called_once_with(
            self.DOWNLOAD_BASE_PATH, as_attachment=True)
        self.assertEqual(response.status_code, 200)

    def test_session_wrong_path(self):
        self.mock_isfile.return_value = False
        with self.assertRaises(FileNotFoundError) as context:
            session_data = DownloadFileInfo(self.DOWNLOAD_BASE_PATH, False)
            self.assertTrue(
                self.fileNotFoundError in str(context.exception))

    @patch.object(youtube, "extract_request_format", return_value=FORMAT_MP3_INSTANCE)
    @patch.object(youtube, "download_single_track_data", return_value=DOWNLOAD_BASE_PATH)
    def test_socket_download_server_success(self,
                                            mock_download_single_track,
                                            mock_get_format
                                            ):
        form_data = {
            MainYoutubeKeys.YOUTUBE_URL.value: self.URL_SINGLE_VIDEO,
            MainYoutubeKeys.DOWNLOAD_TYP.value: self.FORMAT_KEY_MP3
        }
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, form_data, namespace=self.youtube_ns
        )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)

        received_msg = EmitData.get_emit_massage(python_emit, 0)
        mock_download_single_track.assert_called_once_with(self.URL_SINGLE_VIDEO,
                                                           self.FORMAT_MP3_INSTANCE,
                                                           self.user_browser_id,
                                                           self.youtube_ns)
        self.mock_isfile.assert_called_once_with(self.DOWNLOAD_BASE_PATH)
        mock_get_format.assert_called_once_with(
            form_data,
            self.user_browser_id,
            namespace=self.youtube_ns
        )
        self.assertEqual(len(python_emit), 1)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.KEY_DATA, emit_data.data)
        self.assertIn(MainYoutubeKeys.HASH.value,
                      emit_data.data[self.KEY_DATA])

    def test_socket_download_server_no_download_type(self):
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value,
            {MainYoutubeKeys.YOUTUBE_URL.value: self.URL_SINGLE_VIDEO},
            namespace=self.youtube_ns
        )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
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
            MainYoutubeKeys.FORM_DATA.value,
            {
                MainYoutubeKeys.YOUTUBE_URL.value: "",
                MainYoutubeKeys.DOWNLOAD_TYP.value: self.FORMAT_KEY_MP3
            },
            namespace=self.youtube_ns
        )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        self.assertEqual(len(python_emit), 1)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertIn(MainYoutubeKeys.NAME.value, received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(MainYoutubeKeys.ERROR.value, emit_data.data)
        self.assertEqual(emit_data.data[MainYoutubeKeys.ERROR.value],
                         YoutubeLogs.NO_URL.value)

    @patch.object(base_namespace, "generate_hash", return_value=SAMPLE_GENERATED_HASH)
    @patch.object(youtube, "extract_request_format", return_value=FORMAT_MP3_INSTANCE)
    @patch.object(youtube, "download_single_track_data", return_value=DOWNLOAD_BASE_PATH)
    def test_socket_download_audio(self,
                                   mock_download_single_track_data,
                                   mock_get_format,
                                   mock_generate_hash
                                   ):
        from_data = {
            MainYoutubeKeys.YOUTUBE_URL.value: self.URL_VIDEO_IN_PLAYLIST,
            MainYoutubeKeys.DOWNLOAD_TYP.value: self.FORMAT_KEY_MP3
        }
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, from_data, namespace=self.youtube_ns
        )
        mock_generate_hash.assert_called_once()
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        self.assertEqual(len(python_emit), 1)
        mock_download_single_track_data.assert_called_once_with(self.URL_VIDEO_IN_PLAYLIST,
                                                                self.FORMAT_MP3_INSTANCE,
                                                                self.user_browser_id,
                                                                self.youtube_ns)
        self.mock_isfile.assert_called_once_with(self.DOWNLOAD_BASE_PATH)
        mock_get_format.assert_called_once_with(
            from_data,
            self.user_browser_id,
            namespace=self.youtube_ns
        )
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertIn(MainYoutubeKeys.NAME.value, received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        expecte_data = self.download_media_finish_emit.convert_data_to_message(
            self.SAMPLE_GENERATED_HASH)
        expected_restult = {self.KEY_DATA: expecte_data}
        self.assertEqual(emit_data.data, expected_restult)

    @patch.object(youtube, "extract_request_format", return_value=FORMAT_MP3_INSTANCE)
    @patch.object(youtube, "download_playlist_data", return_value=DOWNLOAD_BASE_PATH)
    def test_socket_download_playlist(self,
                                      mock_download_playlist_data,
                                      mock_get_format
                                      ):
        form_data = {
            MainYoutubeKeys.YOUTUBE_URL.value: self.URL_PLAYLIST,
            MainYoutubeKeys.DOWNLOAD_TYP.value: self.FORMAT_KEY_MP3
        }
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, form_data, namespace=self.youtube_ns
        )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        self.mock_isfile.assert_called_once_with(self.DOWNLOAD_BASE_PATH)
        self.assertEqual(len(python_emit), 1)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        mock_download_playlist_data.assert_called_once_with(self.URL_PLAYLIST,
                                                            self.FORMAT_MP3_INSTANCE,
                                                            self.user_browser_id,
                                                            self.youtube_ns)
        mock_get_format.assert_called_once_with(
            form_data,
            self.user_browser_id,
            namespace=self.youtube_ns
        )
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.KEY_DATA, emit_data.data)
        self.assertIn(MainYoutubeKeys.HASH.value,
                      emit_data.data[self.KEY_DATA])

    @patch.object(youtube, "extract_request_format", return_value=FORMAT_MP3_INSTANCE)
    @patch.object(youtube, "download_single_track_data", return_value=None)
    def test_socket_download_fail(self,
                                  mock_download_single_track_data,
                                  mock_get_format):
        form_data = {
            MainYoutubeKeys.YOUTUBE_URL.value: self.URL_SINGLE_VIDEO,
            MainYoutubeKeys.DOWNLOAD_TYP.value: self.FORMAT_KEY_MP3
        }
        self.socket_io_test_client.emit(
            MainYoutubeKeys.FORM_DATA.value, form_data, namespace=self.youtube_ns
        )
        mock_get_format.assert_called_once_with(
            form_data,
            self.user_browser_id,
            namespace=self.youtube_ns
        )
        mock_download_single_track_data.assert_called_once_with(self.URL_SINGLE_VIDEO,
                                                                self.FORMAT_MP3_INSTANCE,
                                                                self.user_browser_id,
                                                                self.youtube_ns)
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        self.assertEqual(len(python_emit), 1)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.download_media_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(MainYoutubeKeys.ERROR.value, emit_data.data)

    @patch.object(YoutubeDL,
                  "request_single_media_info", return_value=result_of_youtube_single)
    def test_send_emit_single_media_info_from_youtube(self,
                                                      mock_request_single_media):
        with self.app.app_context():
            result = youtube_emit.send_emit_single_media_info_from_youtube(
                single_media_url=self.URL_SINGLE_VIDEO,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        mock_request_single_media.assert_called_once_with(
            self.URL_SINGLE_VIDEO)
        self.assertEqual(emit_data.data[self.KEY_DATA],
                         self.expected_result_single_medi_info)
        self.assertEqual(self.single_media_info_emit.emit_msg,
                         emit_data.emit_name)
        self.assertTrue(result)

    @patch.object(YoutubePlaylistDownloader, "request_single_media_info",
                  return_value=result_of_youtube_single_with_error1)
    def test_send_emit_single_media_info_with_error(self,
                                                    mock_request_single_media):
        with self.app.app_context():
            result = youtube_emit.send_emit_single_media_info_from_youtube(
                single_media_url=self.URL_SINGLE_VIDEO,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        mock_request_single_media.assert_called_once_with(
            self.URL_SINGLE_VIDEO)
        no_emit_data = len(python_emit)
        self.assertFalse(result)
        self.assertEqual(no_emit_data, 0)

    @patch.object(YoutubeDL, "request_playlist_media_info",
                  return_value=result_of_youtube_playlist)
    def test_send_emit_playlist_media(self, mock_request_single_media):
        with self.app.app_context():
            result = youtube_emit.send_emit_playlist_media(
                youtube_url=self.URL_PLAYLIST,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        mock_request_single_media.assert_called_once_with(
            self.URL_PLAYLIST)
        self.assertEqual(emit_data.data[self.KEY_DATA],
                         self.expected_result_playlist_media_info)
        self.assertEqual(self.playlist_media_info_emit.emit_msg,
                         emit_data.emit_name)
        self.assertTrue(result)

    @patch.object(YoutubeDL,
                  "request_playlist_media_info", return_value=result_of_youtube_playlist_with_error)
    def test_send_emit_playlist_media_with_error(self,
                                                 mock_request_single_media):
        with self.app.app_context():
            result = youtube_emit.send_emit_playlist_media(
                youtube_url=self.URL_PLAYLIST,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        python_emit = self.socket_io_test_client.get_received(namespace=self.youtube_ns)
        no_emit_data = len(python_emit)
        self.assertFalse(result)
        self.assertEqual(no_emit_data, 0)

    @patch.object(youtube_download, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubePlaylistDownloader, "download_single_video", return_value=SAMPLE_FULL_PATH_1)
    @patch.object(youtube_download, "get_files_from_dir", return_value=PATH_FILES)
    def test_download_tracks_from_playlist_video(self,
                                                 mockGetFilesFromDir,
                                                 mockDownloadVideo,
                                                 mockSendEmitPlaylist
                                                 ):
        with self.app.app_context():
            result = youtube_download.download_tracks_from_playlist(
                youtube_url=self.URL_PLAYLIST,
                req_format=self.FORMAT_360P_INSTANCE,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        mockSendEmitPlaylist.assert_called_once()
        calls = mockDownloadVideo.mock_calls
        self.assertEqual(call(single_media_url=self.SAMPLE_VIDEO_ID_1, req_format=self.FORMAT_360P_INSTANCE),
                         calls[0])
        self.assertEqual(call(single_media_url=self.SAMPLE_VIDEO_ID_2, req_format=self.FORMAT_360P_INSTANCE),
                         calls[1])
        self.assertEqual(2, mockDownloadVideo.call_count)
        self.assertEqual(result, f"/home/test_path/{self.SAMPLE_PLAYLIST_NAME}")
        self.mock_zip.assert_called_once()

    @patch.object(youtube_download, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubePlaylistDownloader, "download_audio_from_playlist", return_value=SAMPLE_FULL_PATH_1)
    @patch.object(youtube_download, "get_files_from_dir", return_value=PATH_FILES)
    def test_download_tracks_from_playlist_audio(self, mockGetFilesFromDir,
                                                 mock_download_audio,
                                                 mockSendEmitPlaylist
                                                 ):
        with self.app.app_context():
            result = youtube_download.download_tracks_from_playlist(
                youtube_url=self.URL_PLAYLIST,
                req_format=self.FORMAT_MP3_INSTANCE,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        mockSendEmitPlaylist.assert_called_once()
        mockGetFilesFromDir.assert_called_once_with(self.DOWNLOAD_BASE_PATH)
        calls = mock_download_audio.mock_calls
        self.assertEqual(call(single_media_url=self.SAMPLE_VIDEO_ID_1,
                              req_format=self.FORMAT_MP3_INSTANCE,
                              playlist_name=self.SAMPLE_PLAYLIST_NAME,
                              index="1"),
                         calls[0])
        self.assertEqual(call(single_media_url=self.SAMPLE_VIDEO_ID_2,
                              req_format=self.FORMAT_MP3_INSTANCE,
                              playlist_name=self.SAMPLE_PLAYLIST_NAME,
                              index="2"),
                         calls[1])
        self.assertEqual(2, mock_download_audio.call_count)
        self.assertEqual(result, f"/home/test_path/{self.SAMPLE_PLAYLIST_NAME}")
        self.mock_zip.assert_called_once()

    @patch.object(youtube_download, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubePlaylistDownloader, "download_single_video", return_value="full_path_test")
    @patch.object(youtube_download, "get_files_from_dir", return_value=["file1", "file2"])
    def test_download_tracks_from_playlist_1080p(self,
                                                 mock_get_files,
                                                 mock_download_video,
                                                 mock_send_emit):
        with self.app.app_context():
            result = youtube_download.download_tracks_from_playlist(
                youtube_url=self.URL_PLAYLIST,
                req_format=self.FORMAT_1080P_INSTANCE,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        mock_get_files.assert_called_once_with(self.DOWNLOAD_BASE_PATH)
        mock_send_emit.assert_called_once()
        self.assertEqual(mock_download_video.call_count, 2)
        self.assertEqual(result, f"/home/test_path/{self.SAMPLE_PLAYLIST_NAME}")
        self.mock_zip.assert_called_once()

    @patch.object(youtube_download, "send_emit_playlist_media", return_value=playlist_media)
    @patch.object(YoutubePlaylistDownloader, "download_single_video", return_value="full_path_test")
    @patch.object(youtube_download, "get_files_from_dir", return_value=["file1", "file2"])
    def test_download_tracks_from_playlist_2160p(self, mock_get_files, mock_download_video, mock_send_emit):
        with self.app.app_context():
            result = youtube_download.download_tracks_from_playlist(
                youtube_url=self.URL_PLAYLIST,
                req_format=self.FORMAT_2160P_INSTANCE,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        mock_get_files.assert_called_once_with(self.DOWNLOAD_BASE_PATH)
        mock_send_emit.assert_called_once()
        self.assertEqual(mock_download_video.call_count, 2)
        self.assertEqual(result, f"/home/test_path/{self.SAMPLE_PLAYLIST_NAME}")
        self.mock_zip.assert_called_once()

    @patch.object(youtube_download, "send_emit_playlist_media",
                  return_value=None)
    def testdownload_tracks_from_playlist_video_with_error(self,
                                                           mock_request_playlist_media_info):
        with self.app.app_context():
            result = youtube_download.download_tracks_from_playlist(
                youtube_url=self.URL_PLAYLIST,
                req_format=self.QUALITY_720P,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        self.assertFalse(result)
        mock_request_playlist_media_info.assert_called_once_with(
            self.URL_PLAYLIST,
            self.user_browser_id,
            namespace=self.youtube_ns
            )

    @patch.object(youtube_download, "send_emit_playlist_media",
                  return_value=None)
    def testdownload_tracks_from_playlist_audio_with_error(self,
                                                           mock_request_playlist_media_info):
        with self.app.app_context():
            result = youtube_download.download_tracks_from_playlist(
                youtube_url=self.URL_PLAYLIST,
                req_format=self.FORMAT_MP3_INSTANCE,
                user_browser_id=self.user_browser_id,
                namespace=self.youtube_ns
            )
        self.assertFalse(result)
        mock_request_playlist_media_info.assert_called_once_with(
            self.URL_PLAYLIST,
            self.user_browser_id,
            namespace=self.youtube_ns
            )

    def test_youtube_html(self):
        response = self.flask.get("/youtube.html")
        self.assertIn('<title>YouTube</title>', str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_index_html(self):
        response1 = self.flask.get("/")
        response2 = self.flask.get("/index.html")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    def test_wrong_yourube_html(self):
        response = self.flask.get("/youtubetest.html")
        self.assertEqual(response.status_code, 404)

    @skip("Skipping test, config not working")
    @patch.object(youtube_playlists, "generate_hash",
                  return_value="test_hash")
    @patch.object(youtube_playlists, "download_tracks_from_playlist",
                  return_value="video_playlist_path")
    def test_download_config_playlist(self, mock_download_playlist,
                                      mock_generate_hash):
        self.app.config_parser_manager.get_playlist_url = MagicMock(
            return_value=self.URL_PLAYLIST)
        self.socket_io_test_client.emit(
            "downloadFromConfigFile", {
                "playlistToDownload": self.SAMPLE_PLAYLIST_NAME
            }
        )
        mock_download_playlist.assert_called_once_with(
            youtube_url=self.URL_PLAYLIST, video_type=None)
        self.mock_isfile.assert_called_once()
        mock_generate_hash.assert_called_once()
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(emit_data.emit_name,
                         self.download_media_finish_emit.emit_msg)
        self.assertEqual(
            emit_data.data[self.KEY_DATA], self.download_media_finish_emit.convert_data_to_message("test_hash"))

    @skip("Skipping test, config not working")
    @patch.object(youtube_playlists, "download_tracks_from_playlist",
                  return_value=None)
    def test_download_config_playlist_with_error(self, mock_download_playlist):
        self.app.config_parser_manager.get_playlist_url = MagicMock(
            return_value=self.URL_PLAYLIST)
        self.socket_io_test_client.emit(
            "downloadFromConfigFile", {
                "playlistToDownload": self.SAMPLE_PLAYLIST_NAME
            }
        )
        self.app.config_parser_manager.get_playlist_url.assert_called_once_with(
            self.SAMPLE_PLAYLIST_NAME)
        mock_download_playlist.assert_called_once_with(
            youtube_url=self.URL_PLAYLIST, req_format=self.FORMAT_MP3_INSTANCE, user_browser_id=None)
        python_emit = self.socket_io_test_client.get_received()
        self.assertEqual(len(python_emit), 0)

    @skip("Skipping test, config not working")
    def test_add_playlist_config(self):
        self.app.config_parser_manager.add_playlist = MagicMock()
        self.app.config_parser_manager.get_playlists = MagicMock(
            return_value={
                "test_playlist": "url1",
                self.SAMPLE_PLAYLIST_NAME: "url2"
            })
        self.socket_io_test_client.emit(
            "addPlaylist", {
                "playlistName": self.SAMPLE_PLAYLIST_NAME,
                "playlistURL": self.URL_PLAYLIST
            }
        )
        self.app.config_parser_manager.add_playlist.assert_called_once_with(
            self.SAMPLE_PLAYLIST_NAME, self.URL_PLAYLIST)
        self.app.config_parser_manager.get_playlists.assert_called_once()
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(emit_data.emit_name, "uploadPlaylists")
        self.assertEqual(
            emit_data.data, {self.KEY_DATA: {'playlistList': ["test_playlist", self.SAMPLE_PLAYLIST_NAME]}})

    @skip("Skipping test, config not working")
    def test_delete_playlist_config(self):
        self.app.config_parser_manager.deletePlaylist = MagicMock()
        self.app.config_parser_manager.get_playlists = MagicMock(
            return_value={
                "test_playlist": "url1",
                self.SAMPLE_PLAYLIST_NAME: "url2"
            })
        self.socket_io_test_client.emit(
            "deletePlaylist", {
                "playlistToDelete": self.SAMPLE_PLAYLIST_NAME,
            }
        )
        self.app.config_parser_manager.deletePlaylist.assert_called_once_with(
            self.SAMPLE_PLAYLIST_NAME)
        self.app.config_parser_manager.get_playlists.assert_called_once()
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(emit_data.emit_name, "uploadPlaylists")
        self.assertEqual(
            emit_data.data, {self.KEY_DATA: {'playlistList': ["test_playlist", self.SAMPLE_PLAYLIST_NAME]}})

    @skip("Skipping test, config not working")
    def test_playlist_config_url(self):
        self.app.config_parser_manager.get_playlist_url = MagicMock(
            return_value=self.SAMPLE_PLAYLIST_NAME)
        self.socket_io_test_client.emit(
            "playlistName", {
                "playlistName": self.SAMPLE_PLAYLIST_NAME,
            }
        )
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        self.app.config_parser_manager.get_playlist_url.assert_called_once()
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.playlist_url_str, emit_data.emit_name)
        self.assertEqual(
            emit_data.data, {self.KEY_DATA: {self.playlist_url_str:  self.SAMPLE_PLAYLIST_NAME}})

    def test_modify_playlist_html(self):
        response = self.flask.get("/modify_playlist.html")
        self.assertEqual(response.status_code, 200)


class TestEmits(TestCase):
    playlist_name = "playlistName"
    track_list = "trackList"
    title = "title"
    url = "url"
    artist = "artist"

    playlist_mediaTest = FlaskPlaylistMedia.init_from_playlist_media(
        TestYoutubeWeb.SAMPLE_PLAYLIST_NAME,
        [TestYoutubeWeb.single_media1, TestYoutubeWeb.single_media2],
    )

    singleMedia = FlaskSingleMedia(
        TestYoutubeWeb.SAMPLE_TITLE_SOCIETY,
        TestYoutubeWeb.SAMPLE_ARTIST_E_VEDDER,
        TestYoutubeWeb.URL_SINGLE_VIDEO_ORIGINAL,
    )

    def setUp(self):
        self.playlist_media_info_emits = emits.PlaylistMediaInfoEmit()
        self.single_media_info_emits = emits.SingleMediaInfoEmit()

    def test_convert_data_to_massage_playlist(self):
        result = self.playlist_media_info_emits.convert_data_to_message(
            self.playlist_mediaTest)
        self.assertEqual(
            result, TestYoutubeWeb.expected_result_playlist_media_info)

    def test_convert_data_to_massage_single(self):
        result = self.single_media_info_emits.convert_data_to_message(
            TestYoutubeWeb.single_media1)
        self.assertEqual(
            result, TestYoutubeWeb.expected_result_single_medi_info)


if __name__ == "__main__":
    main()
