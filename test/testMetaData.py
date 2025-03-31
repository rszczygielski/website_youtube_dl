# import os
# from unittest.mock import patch, call
# from unittest import TestCase, main
# # from website_youtube_dl.common.youtubeDataKeys import PlaylistInfo
# from website_youtube_dl.common.easy_id3_manager import EasyID3Manager


# class MetaDataTest(TestCase):

#     testTitle = "testTitle"
#     testAlbum = "testAlbum"
#     testArtist = "testArtist"
#     test_playlist_name = "test_playlist_name"
#     test_title2 = f"{testTitle}2"
#     testAlbum2 = f"{testAlbum}2"
#     test_artist2 = f"{testArtist}2"
#     test_playlistIndex1 = 1
#     test_playlist_index2 = 2

#     testDir = fileFullPath=os.path.dirname(os.path.abspath(__file__))

#     easy_id3_manager = EasyID3Manager()
#     easy_id3_manager.setParams(filePath=testDir, title=testTitle, album=testAlbum, artist=testArtist)

#     easy_id3_manager1 = EasyID3Manager()
#     easy_id3_manager1.setParams(filePath=testDir,
#                                 title=testTitle, album=testAlbum,
#                                 artist=testArtist,
#                                 trackNumber=test_playlistIndex1,
#                                 playlist_name=test_playlist_name)

#     easy_id3_manager2 = EasyID3Manager()

#     easy_id3_manager2.setParams(filePath=testDir,
#                                 title=test_title2, album=testAlbum2,
#                                 artist=test_artist2,
#                                 trackNumber=test_playlist_index2,
#                                 playlist_name=test_playlist_name)


#     track_list = [easy_id3_manager1]
#     track_listTwoSongs = [easy_id3_manager1, easy_id3_manager2]

#     def setUp(self):
#         self.testDir = os.path.dirname(os.path.abspath(__file__))


#     @patch.object(EasyID3Manager, "save_meta_data")
#     def test_set_meta_data_playlist_two_songs(self, mock_save):
#         self.testMetaData.setMetaDataPlaylist(self.test_playlist_name,
#                                               self.track_listTwoSongs, self.testDir)
#         self.assertEqual(2, len(mock_save.mock_calls))
#         self.assertEqual(call(), mock_save.mock_calls[0])
#         self.assertEqual(call(), mock_save.mock_calls[1])

#     @patch.object(EasyID3Manager, "save_meta_data")
#     def test_set_meta_data_single_file_with_single_media(self, mock_saveFile):
#         self.testMetaData.setMetaDataSingleFile(
#             self.easy_id3_manager, self.testDir)
#         mock_saveFile.assert_called_once_with()

#     @patch.object(EasyID3Manager, "save_meta_data")
#     def test_set_meta_data_single_file_with_media_from_playlist(self, mock_saveFile):
#         self.testMetaData.setMetaDataSingleFile(
#             self.easy_id3_manager1, self.testDir)
#         mock_saveFile.assert_called_once_with()


# if __name__ == "__main__":
#     main()
