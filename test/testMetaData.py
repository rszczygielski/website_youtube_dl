import os
import youtubeDL
import mutagen.easyid3
import mutagen.mp3
from youtubeDL import MetaDataType
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call

class MetaDataTest(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.testMetaData = youtubeDL.MetaData(self.testDir)
        self.metaDataPlaylist = {
            "title": "testPlaylist",
            "entries": [{
                MetaDataType.TITLE.value: "testTitle",
                MetaDataType.ALBUM.value: "testAlbum",
                MetaDataType.ARTIST.value: "testArtist",
                MetaDataType.PLAYLIST_INDEX.value: 1
            }]}
        self.metaData ={
                MetaDataType.TITLE.value: "testTitle",
                MetaDataType.ALBUM.value: "testAlbum",
                MetaDataType.ARTIST.value: "testArtist",
                MetaDataType.PLAYLIST_INDEX.value: 1
            }

    @patch.object(youtubeDL.MetaData, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaData, "saveMetaDataForPlaylist")
    def testSetMetaDataPlaylist(self, mockSavePlaylist, mockShow):
        self.testMetaData.setMetaDataPlaylist(self.metaDataPlaylist)
        mockSavePlaylist.assert_called_once_with({
                MetaDataType.TITLE.value: "testTitle",
                MetaDataType.ALBUM.value: "testAlbum",
                MetaDataType.ARTIST.value: "testArtist",
                MetaDataType.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle.mp3", "testPlaylist")
        mockShow.assert_called_once_with(f"{self.testDir}/testTitle.mp3")

    @patch.object(youtubeDL.MetaData, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaData, "saveMetaDataForPlaylist")
    def testSetMetaDataPlaylistTwoPlaylists(self, mockSavePlaylist, mockShow):
        metaDataPlaylistTwoArgs = self.metaDataPlaylist
        metaDataPlaylistTwoArgs["entries"].append({
                MetaDataType.TITLE.value: "testTitle2",
                MetaDataType.ALBUM.value: "testAlbum2",
                MetaDataType.ARTIST.value: "testArtist2",
                MetaDataType.PLAYLIST_INDEX.value: 1
            })
        self.testMetaData.setMetaDataPlaylist(metaDataPlaylistTwoArgs)
        mockSavePlaylist.assert_has_calls([call(metaDataPlaylistTwoArgs["entries"][0], f"{self.testDir}/testTitle.mp3", "testPlaylist"), 
                                           call(metaDataPlaylistTwoArgs["entries"][1], f"{self.testDir}/testTitle2.mp3", "testPlaylist")])
        mockSavePlaylist.assert_called_with({
                MetaDataType.TITLE.value: "testTitle2",
                MetaDataType.ALBUM.value: "testAlbum2",
                MetaDataType.ARTIST.value: "testArtist2",
                MetaDataType.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle2.mp3", "testPlaylist")
        mockShow.assert_called_with(f"{self.testDir}/testTitle2.mp3")

    @patch.object(youtubeDL.MetaData, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaData, "saveMetaDataForSingleFile")
    def testSetMetaDataSingleFile(self, mockSaveFile, mockShow):
        self.testMetaData.setMetaDataSingleFile(self.metaData)
        mockSaveFile.assert_called_with({
                MetaDataType.TITLE.value: "testTitle",
                MetaDataType.ALBUM.value: "testAlbum",
                MetaDataType.ARTIST.value: "testArtist",
                MetaDataType.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle.mp3")
        mockShow.assert_called_with(f"{self.testDir}/testTitle.mp3")

    def testGetMetaDataDict(self):
        metaData = {
                MetaDataType.TITLE.value: "testTitle",
                "testDictKey": "testDictValue",
                MetaDataType.ALBUM.value: "testAlbum",
                "testDictKey": "testDictValue2",
                MetaDataType.ARTIST.value: "testArtist",
                MetaDataType.PLAYLIST_INDEX.value: 1,
                "testDictKey": "testDictValue3",
                "testDictKey": "testDictValue4"
            }
        metaDataDict = self.testMetaData.getMetaDataDict(metaData)
        self.assertEqual(metaDataDict, {
            MetaDataType.TITLE.value: "testTitle",
            MetaDataType.ALBUM.value: "testAlbum",
            MetaDataType.ARTIST.value: "testArtist",
            MetaDataType.PLAYLIST_INDEX.value: 1
            })

    @patch.object(youtubeDL.MetaData, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3")
    def testSaveMetaDataForPlaylist(self, mockEasyID3, mockSaveEasyID3):
        mockSaveEasyID3.confiugure_mock(return_value=self.metaData)
        self.testMetaData.saveMetaDataForPlaylist(self.metaData, f"{self.testDir}/testTitle.mp3", "testPlaylist")
        mockEasyID3.assert_called_once_with(f"{self.testDir}/testTitle.mp3")
        # mockSaveEasyID3.assert_called_once_with(mockEasyID3)
        # obczaić to

    @patch.object(youtubeDL.MetaData, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3")
    def testSaveMetaDataForSingleFile(self, mockEasyID3, mockSaveEasyID3):
        mockSaveEasyID3.confiugure_mock(return_value=self.metaData)
        self.testMetaData.saveMetaDataForSingleFile(self.metaData, f"{self.testDir}/testTitle.mp3")
        mockEasyID3.assert_called_once_with(f"{self.testDir}/testTitle.mp3")
        # mockSaveEasyID3.assert_called_once()
        # obczaić

    # @patch.object(mutagen.mp3, "MP3")
    # @patch.object(mutagen.mp3.MP3, "pprint")
    # def testShowMetaDataInfo(self, mockPrint, mockMP3):
    #     self.testMetaData.showMetaDataInfo(f"{self.testDir}/testTitle.mp3")
        # mockMP3.assert_called_once()
    # mock_saveConfig.assert_has_calls w manualu spradź
    # mock_.call_count

if __name__ == "__main__":
    main()

