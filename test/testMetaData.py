import os
from unittest.mock import MagicMock, patch, call
from unittest import TestCase, main
import mutagen.mp3
import mutagen.easyid3
from common.youtubeDataKeys import PlaylistInfo
from common.metaDataManager import MetaDataManager, EasyID3SingleMedia, EasyID3MediaFromPlaylist
import sys
sys.path.append("..")


class MetaDataTest(TestCase):

    testTitle = "testTitle"
    testAlbum = "testAlbum"
    testArtist = "testArtist"
    testPlaylistName = "testPlaylistName"
    testTitle2 = f"{testTitle}2"
    testAlbum2 = f"{testAlbum}2"
    testArtist2 = f"{testArtist}2"
    testPlaylistIndex1 = 1
    testPlaylistIndex2 = 2

    easyID3SingleMedia = EasyID3SingleMedia(testTitle, testAlbum, testArtist)
    easyID3MediaFromPlaylist1 = EasyID3MediaFromPlaylist(testTitle, testAlbum,
                                                         testArtist, testPlaylistIndex1)
    easyID3MediaFromPlaylist1.setPlaylistName(testPlaylistName)

    easyID3MediaFromPlaylist2 = EasyID3MediaFromPlaylist(testTitle2, testAlbum2,
                                                         testArtist2, testPlaylistIndex2)
    easyID3MediaFromPlaylist2.setPlaylistName(testPlaylistName)

    trackList = [easyID3MediaFromPlaylist1]
    trackListTwoSongs = [easyID3MediaFromPlaylist1, easyID3MediaFromPlaylist2]

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.testMetaData = MetaDataManager()

    @patch.object(EasyID3MediaFromPlaylist, "saveMetaData")
    @patch.object(MetaDataManager, "_showMetaDataInfo")
    def testSetMetaDataPlaylist(self, mockShow, mockSave):
        self.testMetaData.setMetaDataPlaylist(self.testPlaylistName,
                                              self.trackList, self.testDir)
        mockShow.assert_called_once_with(
            f"{self.testDir}/{self.testTitle}.mp3")
        mockSave.assert_called_once_with()

    @patch.object(EasyID3MediaFromPlaylist, "saveMetaData")
    @patch.object(MetaDataManager, "_showMetaDataInfo")
    def testSetMetaDataPlaylistTwoSongs(self, mockShow, mockSave):
        self.testMetaData.setMetaDataPlaylist(self.testPlaylistName,
                                              self.trackListTwoSongs, self.testDir)
        mockShow.assert_has_calls([call(f"{self.testDir}/{self.testTitle}.mp3"),
                                   call(f"{self.testDir}/{self.testTitle2}.mp3")])

        self.assertEqual(2, len(mockSave.mock_calls))
        self.assertEqual(call(), mockSave.mock_calls[0])
        self.assertEqual(call(), mockSave.mock_calls[1])

    @patch.object(MetaDataManager, "_showMetaDataInfo")
    @patch.object(EasyID3SingleMedia, "saveMetaData")
    def testSetMetaDataSingleFileWithSingleMedia(self, mockSaveFile, mockShow):
        self.testMetaData.setMetaDataSingleFile(
            self.easyID3SingleMedia, self.testDir)
        mockSaveFile.sel
        mockShow.assert_called_with(f"{self.testDir}/testTitle.mp3")
        mockSaveFile.assert_called_once_with()

    @patch.object(MetaDataManager, "_showMetaDataInfo")
    @patch.object(EasyID3MediaFromPlaylist, "saveMetaData")
    def testSetMetaDataSingleFileWithMediaFromPlaylist(self, mockSaveFile, mockShow):
        self.testMetaData.setMetaDataSingleFile(
            self.easyID3MediaFromPlaylist1, self.testDir)
        mockShow.assert_called_with(f"{self.testDir}/testTitle.mp3")
        mockSaveFile.assert_called_once_with()

if __name__ == "__main__":
    main()
