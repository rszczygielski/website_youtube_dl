import os
from unittest.mock import patch, call, MagicMock
from unittest import TestCase, main
from website_youtube_dl.common.easyID3Manager import EasyID3Manager

# Global variables
TEST_TITLE = "testTitle"
TEST_ALBUM = "testAlbum"
TEST_ARTIST = "testArtist"
TEST_PLAYLIST_NAME = "test_playlist_name"
TEST_TITLE2 = f"{TEST_TITLE}2"
TEST_ALBUM2 = f"{TEST_ALBUM}2"
TEST_ARTIST2 = f"{TEST_ARTIST}2"
TEST_PLAYLIST_INDEX1 = 1
TEST_PLAYLIST_INDEX2 = 2


class MetaDataTest(TestCase):
    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.easy_id3_manager = EasyID3Manager()
        self.easy_id3_manager.set_params(
            filePath=self.testDir, title=TEST_TITLE, album=TEST_ALBUM, artist=TEST_ARTIST
        )

        self.easy_id3_manager1 = EasyID3Manager()
        self.easy_id3_manager1.set_params(
            filePath=self.testDir,
            title=TEST_TITLE,
            album=TEST_ALBUM,
            artist=TEST_ARTIST,
            track_number=TEST_PLAYLIST_INDEX1,
            playlist_name=TEST_PLAYLIST_NAME,
        )

        self.easy_id3_manager2 = EasyID3Manager()
        self.easy_id3_manager2.set_params(
            filePath=self.testDir,
            title=TEST_TITLE2,
            album=TEST_ALBUM2,
            artist=TEST_ARTIST2,
            track_number=TEST_PLAYLIST_INDEX2,
            playlist_name=TEST_PLAYLIST_NAME,
        )

        self.track_list = [self.easy_id3_manager1]
        self.track_listTwoSongs = [
            self.easy_id3_manager1, self.easy_id3_manager2]

    @patch.object(EasyID3Manager, "save_meta_data")
    def test_set_meta_data_playlist_two_songs(self, mock_save):
        for manager in self.track_listTwoSongs:
            manager.save_meta_data()
        self.assertEqual(2, len(mock_save.mock_calls))
        self.assertEqual(call(), mock_save.mock_calls[0])
        self.assertEqual(call(), mock_save.mock_calls[1])

    @patch.object(EasyID3Manager, "save_meta_data")
    def test_set_meta_data_single_file_with_single_media(self, mock_saveFile):
        self.easy_id3_manager.save_meta_data()
        mock_saveFile.assert_called_once_with()

    @patch.object(EasyID3Manager, "save_meta_data")
    def test_set_meta_data_single_file_with_media_from_playlist(self, mock_saveFile):
        self.easy_id3_manager1.save_meta_data()
        mock_saveFile.assert_called_once_with()


if __name__ == "__main__":
    main()
