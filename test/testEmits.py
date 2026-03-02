from unittest import main, TestCase
from unittest.mock import MagicMock

from test.emitData import EmitData
from website_youtube_dl import create_app, socketio
from website_youtube_dl.config import TestingConfig
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys, MediaInfo
from website_youtube_dl.flaskAPI.services.flaskMedia import (
    FlaskSingleMedia,
    FlaskMediaFromPlaylist,
    FlaskPlaylistMedia
)
from website_youtube_dl.flaskAPI.sockets.emits import (
    DownloadMediaFinishEmit,
    SingleMediaInfoEmit,
    PlaylistMediaInfoEmit,
    UploadPlaylistToConfigEmit,
    GetPlaylistUrlEmit,
    PlaylistTrackFinish
)


class TestEmits(TestCase):
    # Constants for Testing
    TEST_HASH = "test_hash"
    DATA_KEY = "data"
    TITLE_KEY = "title"
    URL_KEY = "url"
    PLAYLIST_NAME = "Test Playlist"
    PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    
    # Track 1 Metadata
    TRACK_1_TITLE = "Society"
    TRACK_1_ARTIST = "Eddie Vedder"
    TRACK_1_URL = 'https://www.youtube.com/watch?v=ABsslEoL0-c'

    # Track 2 Metadata
    TRACK_2_TITLE = 'Hard Sun'
    TRACK_2_ARTIST = "Eddie Vedder"
    TRACK_2_URL = 'https://www.youtube.com/watch?v=_EZUfnMv3Lg'

    # Media Objects for Testing
    sample_single_media = FlaskSingleMedia(
        TRACK_1_TITLE,
        TRACK_1_ARTIST,
        TRACK_1_URL
    )

    media_from_playlist_1 = FlaskMediaFromPlaylist(TRACK_1_TITLE, TRACK_1_URL)
    media_from_playlist_2 = FlaskMediaFromPlaylist(TRACK_2_TITLE, TRACK_2_URL)
    
    track_objects_list = [media_from_playlist_1, media_from_playlist_2]
    
    expected_track_dict_list = [
        {TITLE_KEY: TRACK_1_TITLE, URL_KEY: TRACK_1_URL},
        {TITLE_KEY: TRACK_2_TITLE, URL_KEY: TRACK_2_URL}
    ]

    sample_playlist_media = FlaskPlaylistMedia(PLAYLIST_NAME, track_objects_list)

    def setUp(self):
        # Initialize Emit Classes
        self.download_finish_emit = DownloadMediaFinishEmit()
        self.single_info_emit = SingleMediaInfoEmit()
        self.playlist_info_emit = PlaylistMediaInfoEmit()
        self.upload_config_emit = UploadPlaylistToConfigEmit()
        self.playlist_url_emit = GetPlaylistUrlEmit()
        self.track_finish_emit = PlaylistTrackFinish()
        
        # Flask & SocketIO Setup
        self.config_manager_mock = MagicMock()
        app = create_app(TestingConfig, self.config_manager_mock)
        app.config["TESTING"] = True
        
        self.youtube_ns = "/youtube"
        self.socket_io_client = socketio.test_client(app, namespace=self.youtube_ns)
        self.app = app
        
        # User Session Simulation
        self.user_browser_id = "test-browser-id"
        self.socket_io_client.emit(
            "userSession",
            {"userBrowserId": self.user_browser_id},
            namespace=self.youtube_ns
        )
        
        # Resolve session ID and clear startup buffers
        self.session_id = self.app.socket_manager.get_session_id_by_user_browser_id(self.user_browser_id)
        self.socket_io_client.get_received(namespace=self.youtube_ns)

    # --- Helper Methods ---

    def get_message_from_list(self, events_list, index):
        return events_list[index]

    # --- Download Media Finish Tests ---

    def test_download_media_finish_emit_convert_data_to_msg(self):
        result = self.download_finish_emit.convert_data_to_message(self.TEST_HASH)
        self.assertEqual({MainYoutubeKeys.HASH.value: self.TEST_HASH}, result)

    def test_download_media_finish_emit_send_emit(self):
        with self.app.app_context():
            self.download_finish_emit.send_emit(self.TEST_HASH, self.session_id, self.youtube_ns)
            
            received_events = self.socket_io_client.get_received(namespace=self.youtube_ns)
            message_payload = EmitData.get_emit_massage(received_events, 0)
            emit_data = EmitData.init_from_massage(message_payload)

            self.assertEqual(self.download_finish_emit.emit_msg, emit_data.emit_name)
            self.assertIn(self.DATA_KEY, emit_data.data)
            self.assertIn(MainYoutubeKeys.HASH.value, emit_data.data[self.DATA_KEY])

    # --- Single Media Info Tests ---

    def test_single_media_info_emit_convert_data_to_msg(self):
        result = self.single_info_emit.convert_data_to_message(self.sample_single_media)
        expected = {
            MediaInfo.TITLE.value: self.sample_single_media.title,
            MediaInfo.ARTIST.value: self.sample_single_media.artist,
            MediaInfo.URL.value: self.sample_single_media.url
        }
        self.assertEqual(expected, result)

    def test_single_media_info_emit_send_emit(self):
        with self.app.app_context():
            self.single_info_emit.send_emit(self.sample_single_media, self.session_id, self.youtube_ns)
            
            received_events = self.socket_io_client.get_received(namespace=self.youtube_ns)
            message_payload = EmitData.get_emit_massage(received_events, 0)
            emit_data = EmitData.init_from_massage(message_payload)

            self.assertEqual(self.single_info_emit.emit_msg, emit_data.emit_name)
            self.assertIn(self.DATA_KEY, emit_data.data)
            
            expected_data = {
                MediaInfo.TITLE.value: self.sample_single_media.title,
                MediaInfo.ARTIST.value: self.sample_single_media.artist,
                MediaInfo.URL.value: self.sample_single_media.url
            }
            self.assertEqual(expected_data, emit_data.data[self.DATA_KEY])

    # --- Playlist Media Info Tests ---

    def test_playlist_media_info_emit_convert_data_to_msg(self):
        result = self.playlist_info_emit.convert_data_to_message(self.sample_playlist_media)
        expected = {
            self.playlist_info_emit.playlist_name_data_key: self.PLAYLIST_NAME,
            self.playlist_info_emit.track_list_data_key: self.expected_track_dict_list
        }
        self.assertEqual(expected, result)

    def test_playlist_media_info_emit_convert_send_emit(self):
        with self.app.app_context():
            self.playlist_info_emit.send_emit(self.sample_playlist_media, self.session_id, self.youtube_ns)
            
            received_events = self.socket_io_client.get_received(namespace=self.youtube_ns)
            message_payload = EmitData.get_emit_massage(received_events, 0)
            emit_data = EmitData.init_from_massage(message_payload)

            self.assertEqual(self.playlist_info_emit.emit_msg, emit_data.emit_name)
            self.assertIn(self.DATA_KEY, emit_data.data)
            
            payload_data = emit_data.data[self.DATA_KEY]
            self.assertEqual(self.PLAYLIST_NAME, payload_data[self.playlist_info_emit.playlist_name_data_key])
            self.assertEqual(self.expected_track_dict_list, payload_data["trackList"])

    # --- Playlist URL Tests ---

    def test_get_playlist_url_emit_convert_data_to_msg(self):
        result = self.playlist_url_emit.convert_data_to_message(self.PLAYLIST_URL)
        self.assertEqual({"playlistUrl": self.PLAYLIST_URL}, result)

    def test_get_playlist_url_emit_send_emit(self):
        with self.app.app_context():
            self.playlist_url_emit.send_emit(self.PLAYLIST_URL, self.session_id, self.youtube_ns)
            
            received_events = self.socket_io_client.get_received(namespace=self.youtube_ns)
            message_payload = EmitData.get_emit_massage(received_events, 0)
            emit_data = EmitData.init_from_massage(message_payload)

            self.assertEqual(self.playlist_url_emit.emit_msg, emit_data.emit_name)
            self.assertEqual({"playlistUrl": self.PLAYLIST_URL}, emit_data.data[self.DATA_KEY])

    # --- Track Finish Tests ---

    def test_playlist_track_finish_convert_data_to_msg(self):
        test_index = 5
        result = self.track_finish_emit.convert_data_to_message(test_index)
        self.assertEqual({"index": test_index}, result)

    def test_playlist_track_finish_send_emit(self):
        with self.app.app_context():
            test_index = 5
            self.track_finish_emit.send_emit(test_index, self.session_id, self.youtube_ns)
            
            received_events = self.socket_io_client.get_received(namespace=self.youtube_ns)
            message_payload = EmitData.get_emit_massage(received_events, 0)
            emit_data = EmitData.init_from_massage(message_payload)

            self.assertEqual(self.track_finish_emit.emit_msg, emit_data.emit_name)
            self.assertEqual({"index": test_index}, emit_data.data[self.DATA_KEY])

    def test_playlist_track_finish_send_emit_error(self):
        with self.app.app_context():
            test_index = 5
            self.track_finish_emit.send_emit_error(test_index, self.session_id, self.youtube_ns)
            
            received_events = self.socket_io_client.get_received(namespace=self.youtube_ns)
            message_payload = EmitData.get_emit_massage(received_events, 0)
            emit_data = EmitData.init_from_massage(message_payload)

            self.assertEqual(self.track_finish_emit.emit_msg, emit_data.emit_name)
            self.assertIn(self.track_finish_emit.error_str, emit_data.data)
            self.assertEqual(test_index, emit_data.data[self.track_finish_emit.error_str])


if __name__ == "__main__":
    main()