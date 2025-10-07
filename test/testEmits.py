from test.emitData import EmitData
from website_youtube_dl.flaskAPI.sockets.emits import (DownloadMediaFinishEmit,
                                                       SingleMediaInfoEmit,
                                                       PlaylistMediaInfoEmit,
                                                       UploadPlaylistToConfigEmit,
                                                       GetPlaylistUrlEmit,
                                                       PlaylistTrackFinish)
from unittest import main, TestCase
from website_youtube_dl.flaskAPI.services.flaskMedia import (FlaskSingleMedia,
                                                             FlaskMediaFromPlaylist,
                                                             FlaskPlaylistMedia)
from website_youtube_dl.common.youtubeDataKeys import MediaInfo
from website_youtube_dl.config import TestingConfig
from website_youtube_dl import create_app, socketio
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from unittest.mock import MagicMock


class TestEmits(TestCase):
    test_hash = "test_hash"
    data_str = "data"
    title_str = "title"
    url_str = "url"
    test_playlist_name = "playlistName"
    playlist_str = "playlist_list"
    playlist_url_str = "playlistUrl"
    track_list = "trackList"
    test_title1 = "Society"
    test_album1 = "Into The Wild"
    test_artist1 = "Eddie Vedder"
    test_original_url1 = 'https://www.youtube.com/watch?v=ABsslEoL0-c'

    test_title2 = 'Hard Sun'
    test_artist2 = "Eddie Vedder"
    test_ext2 = "webm"
    test_playlist_index2 = 2
    test_original_url2 = 'https://www.youtube.com/watch?v=_EZUfnMv3Lg'
    youtube_playlist_url = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"

    flask_single_media = FlaskSingleMedia(test_title1,
                                          test_artist1,
                                          test_original_url1)

    flaskMediaFromPlaylist1 = FlaskMediaFromPlaylist(test_title1,
                                                     test_original_url1)

    flaskMediaFromPlaylist2 = FlaskMediaFromPlaylist(test_title2,
                                                     test_original_url2)
    trakList_with_objects = [flaskMediaFromPlaylist1, flaskMediaFromPlaylist2]
    track_list_with_dict = [{title_str: test_title1,
                             url_str: test_original_url1},
                            {title_str: test_title2,
                             url_str: test_original_url2}]
    flask_playlist_media = FlaskPlaylistMedia(
        test_playlist_name, trakList_with_objects)

    def setUp(self):
        self.download_media_finish_emit = DownloadMediaFinishEmit()
        self.single_media_info_emit = SingleMediaInfoEmit()
        self.playlist_media_info_emit = PlaylistMediaInfoEmit()
        self.upload_playlist_to_config_emit = UploadPlaylistToConfigEmit()
        self.get_playlist_url_emit = GetPlaylistUrlEmit()
        self.playlist_track_finish_emit = PlaylistTrackFinish()
        self.config_manager_mock = MagicMock()
        app = create_app(TestingConfig, self.config_manager_mock)
        app.config["TESTING"] = True
        self.socket_io_test_client = socketio.test_client(app)
        self.flask = app.test_client()
        self.app = app
        self.session_id = "12345"

    def test_download_media_finish_emit_convert_data_to_msg(self):
        result = self.download_media_finish_emit.convert_data_to_message(
            self.test_hash)
        self.assertEqual({MainYoutubeKeys.HASH.value: self.test_hash},
                         result)

    def get_emit_massage(self, fullEmit, msgNumber):
        return fullEmit[msgNumber]

    def test_download_media_finish_emit_send_emit(self):
        with self.app.app_context():
            session_id = self.socket_io_test_client.sid
            self.download_media_finish_emit.send_emit(
                self.test_hash, session_id)
            python_emit = self.socket_io_test_client.get_received()
            print(python_emit)
            received_msg = EmitData.get_emit_massage(python_emit, 0)
            emit_data = EmitData.init_from_massage(received_msg)
            self.assertEqual(self.download_media_finish_emit.emit_msg,
                             emit_data.emit_name)
            self.assertIn(self.data_str, emit_data.data)
            self.assertIn(MainYoutubeKeys.HASH.value,
                          emit_data.data[self.data_str])

    def test_single_media_info_emit_convert_data_to_msg(self):
        result = self.single_media_info_emit.convert_data_to_message(
            self.flask_single_media)
        self.assertEqual({
            MediaInfo.TITLE.value: self.flask_single_media.title,
            MediaInfo.ARTIST.value: self.flask_single_media.artist,
            MediaInfo.URL.value: self.flask_single_media.url
        }, result)

    def test_single_media_info_emit_send_emit(self):
        self.single_media_info_emit.send_emit(self.flask_single_media)
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.single_media_info_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.data_str, emit_data.data)
        data = emit_data.data[self.data_str]
        self.assertEqual({
            MediaInfo.TITLE.value: self.flask_single_media.title,
            MediaInfo.ARTIST.value: self.flask_single_media.artist,
            MediaInfo.URL.value: self.flask_single_media.url
        }, data)

    def test_playlist_media_info_emit_convert_data_to_msg(self):
        result = self.playlist_media_info_emit.convert_data_to_message(
            self.flask_playlist_media)
        self.assertEqual({self.playlist_media_info_emit.playlist_name: self.playlist_media_info_emit.playlist_name,
                          self.playlist_media_info_emit.track_list: self.track_list_with_dict}, result)

    def test_playlist_media_info_emit_convert_send_emit(self):
        self.playlist_media_info_emit.send_emit(self.flask_playlist_media)
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.playlist_media_info_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.data_str, emit_data.data)
        self.assertEqual(self.playlist_media_info_emit.playlist_name,
                         emit_data.data[self.data_str][self.playlist_media_info_emit.playlist_name])
        print(emit_data.data)
        self.assertEqual(self.track_list_with_dict,
                         emit_data.data[self.data_str][self.track_list])

    def test_get_playlist_url_emit_config_emit_convert_data_to_msg(self):
        result = self.get_playlist_url_emit.convert_data_to_message(
            self.youtube_playlist_url)
        self.assertEqual(
            {self.playlist_url_str: self.youtube_playlist_url}, result)

    def test_get_playlist_url_emit_config_emit_send_emit(self):
        self.get_playlist_url_emit.send_emit(self.youtube_playlist_url)
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.get_playlist_url_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.data_str, emit_data.data)
        self.assertEqual(
            {self.playlist_url_str: self.youtube_playlist_url}, emit_data.data[self.data_str])

    def test_playlist_track_finish_convert_data_to_msg(self):
        test_index = 5
        result = self.playlist_track_finish_emit.convert_data_to_message(
            test_index)
        self.assertEqual({"index": test_index}, result)

    def test_playlist_track_finish_send_emit(self):
        test_index = 5
        self.playlist_track_finish_emit.send_emit(test_index)
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.playlist_track_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.data_str, emit_data.data)
        self.assertEqual({"index": test_index}, emit_data.data[self.data_str])

    def test_playlist_track_finish_send_emit_error(self):
        test_index = 5
        self.playlist_track_finish_emit.send_emit_error(test_index)
        python_emit = self.socket_io_test_client.get_received()
        received_msg = EmitData.get_emit_massage(python_emit, 0)
        emit_data = EmitData.init_from_massage(received_msg)
        self.assertEqual(self.playlist_track_finish_emit.emit_msg,
                         emit_data.emit_name)
        self.assertIn(self.playlist_track_finish_emit.error_str,
                      emit_data.data)
        self.assertEqual(
            test_index, emit_data.data[self.playlist_track_finish_emit.error_str])


if __name__ == "__main__":
    main()
