import os
from unittest.mock import patch, call
from unittest import TestCase, main
# from website_youtube_dl.common.youtubeDataKeys import PlaylistInfo
from website_youtube_dl.common.easyID3Manager import EasyID3Manager


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

    testDir = fileFullPath=os.path.dirname(os.path.abspath(__file__))

    easyID3Manager = EasyID3Manager(fileFullPath=testDir)
    easyID3Manager.setParams(title=testTitle, album=testAlbum, artist=testArtist)

    easyID3Manager1 = EasyID3Manager(fileFullPath=testDir)
    easyID3Manager1.setParams(title=testTitle, album=testAlbum,
                                artist=testArtist,
                                trackNumber=testPlaylistIndex1,
                                playlistName=testPlaylistName)

    easyID3Manager2 = EasyID3Manager(fileFullPath=testDir)

    easyID3Manager2.setParams(title=testTitle2, album=testAlbum2,
                                artist=testArtist2, 
                                trackNumber=testPlaylistIndex2,
                                playlistName=testPlaylistName)


    trackList = [easyID3Manager1]
    trackListTwoSongs = [easyID3Manager1, easyID3Manager2]

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))

    @patch.object(EasyID3Manager, "saveMetaData")
    def testSetMetaDataPlaylist(self, mockShow, mockSave):
        EasyID3Manager(self.testPlaylistName,
                                              self.trackList, self.testDir)
        mockShow.assert_called_once_with(
            f"{self.testDir}/{self.testTitle}.mp3")
        mockSave.assert_called_once_with()

    @patch.object(EasyID3Manager, "saveMetaData")
    def testSetMetaDataPlaylistTwoSongs(self, mockShow, mockSave):
        self.testMetaData.setMetaDataPlaylist(self.testPlaylistName,
                                              self.trackListTwoSongs, self.testDir)
        mockShow.assert_has_calls([call(f"{self.testDir}/{self.testTitle}.mp3"),
                                   call(f"{self.testDir}/{self.testTitle2}.mp3")])

        self.assertEqual(2, len(mockSave.mock_calls))
        self.assertEqual(call(), mockSave.mock_calls[0])
        self.assertEqual(call(), mockSave.mock_calls[1])

    @patch.object(EasyID3Manager, "saveMetaData")
    def testSetMetaDataSingleFileWithSingleMedia(self, mockSaveFile, mockShow):
        self.testMetaData.setMetaDataSingleFile(
            self.easyID3Manager, self.testDir)
        mockSaveFile.sel
        mockShow.assert_called_with(f"{self.testDir}/testTitle.mp3")
        mockSaveFile.assert_called_once_with()

    @patch.object(EasyID3Manager, "saveMetaData")
    def testSetMetaDataSingleFileWithMediaFromPlaylist(self, mockSaveFile, mockShow):
        self.testMetaData.setMetaDataSingleFile(
            self.easyID3Manager1, self.testDir)
        mockShow.assert_called_with(f"{self.testDir}/testTitle.mp3")
        mockSaveFile.assert_called_once_with()


if __name__ == "__main__":
    main()
