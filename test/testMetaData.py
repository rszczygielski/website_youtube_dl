import sys
sys.path.append("..")
from common.metaDataManager import MetaDataManager
from common.youtubeDataKeys import PlaylistInfo
import mutagen.easyid3
import mutagen.mp3
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call
import os

class MetaDataTest(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.testMetaData = MetaDataManager()
        self.metaDataPlaylist = {
            "title": "testPlaylist",
            "entries": [{
                PlaylistInfo.TITLE.value: "testTitle",
                PlaylistInfo.ALBUM.value: "testAlbum",
                PlaylistInfo.ARTIST.value: "testArtist",
                PlaylistInfo.PLAYLIST_INDEX.value: 1
            }]}
        self.metaData ={
                PlaylistInfo.TITLE.value: "testTitle",
                PlaylistInfo.ALBUM.value: "testAlbum",
                PlaylistInfo.ARTIST.value: "testArtist",
                PlaylistInfo.PLAYLIST_INDEX.value: 1
            }

    @patch.object(MetaDataManager, "showMetaDataInfo")
    @patch.object(MetaDataManager, "saveMetaDataForPlaylist")
    def testSetMetaDataPlaylist(self, mockSavePlaylist, mockShow):
        self.testMetaData.setMetaDataPlaylist(self.metaDataPlaylist, self.testDir)
        mockSavePlaylist.assert_called_once_with({
                PlaylistInfo.TITLE.value: "testTitle",
                PlaylistInfo.ALBUM.value: "testAlbum",
                PlaylistInfo.ARTIST.value: "testArtist",
                PlaylistInfo.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle.mp3", "testPlaylist")
        mockShow.assert_called_once_with(f"{self.testDir}/testTitle.mp3")

    @patch.object(MetaDataManager, "showMetaDataInfo")
    @patch.object(MetaDataManager, "saveMetaDataForPlaylist")
    def testSetMetaDataPlaylistTwoPlaylists(self, mockSavePlaylist, mockShow):
        metaDataPlaylistTwoArgs = self.metaDataPlaylist
        metaDataPlaylistTwoArgs["entries"].append({
                PlaylistInfo.TITLE.value: "testTitle2",
                PlaylistInfo.ALBUM.value: "testAlbum2",
                PlaylistInfo.ARTIST.value: "testArtist2",
                PlaylistInfo.PLAYLIST_INDEX.value: 1
            })
        self.testMetaData.setMetaDataPlaylist(metaDataPlaylistTwoArgs, self.testDir)
        mockSavePlaylist.assert_has_calls([call(metaDataPlaylistTwoArgs["entries"][0], f"{self.testDir}/testTitle.mp3", "testPlaylist"),
                                           call(metaDataPlaylistTwoArgs["entries"][1], f"{self.testDir}/testTitle2.mp3", "testPlaylist")])
        mockSavePlaylist.assert_called_with({
                PlaylistInfo.TITLE.value: "testTitle2",
                PlaylistInfo.ALBUM.value: "testAlbum2",
                PlaylistInfo.ARTIST.value: "testArtist2",
                PlaylistInfo.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle2.mp3", "testPlaylist")
        mockShow.assert_called_with(f"{self.testDir}/testTitle2.mp3")

    @patch.object(MetaDataManager, "showMetaDataInfo")
    @patch.object(MetaDataManager, "saveMetaDataForSingleFile")
    def testSetMetaDataSingleFile(self, mockSaveFile, mockShow):
        self.testMetaData.setMetaDataSingleFile(self.metaData, self.testDir)
        mockSaveFile.assert_called_with({
                PlaylistInfo.TITLE.value: "testTitle",
                PlaylistInfo.ALBUM.value: "testAlbum",
                PlaylistInfo.ARTIST.value: "testArtist",
                PlaylistInfo.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle.mp3")
        mockShow.assert_called_with(f"{self.testDir}/testTitle.mp3")

    def testGetMetaDataDict(self):
        metaData = {
                PlaylistInfo.TITLE.value: "testTitle",
                "testDictKey": "testDictValue",
                PlaylistInfo.ALBUM.value: "testAlbum",
                "testDictKey": "testDictValue2",
                PlaylistInfo.ARTIST.value: "testArtist",
                PlaylistInfo.PLAYLIST_INDEX.value: 1,
                "testDictKey": "testDictValue3",
                "testDictKey": "testDictValue4"
            }
        metaDataDict = self.testMetaData.getMetaDataDict(metaData)
        self.assertEqual(metaDataDict, {
            PlaylistInfo.TITLE.value: "testTitle",
            PlaylistInfo.ALBUM.value: "testAlbum",
            PlaylistInfo.ARTIST.value: "testArtist",
            PlaylistInfo.PLAYLIST_INDEX.value: 1
            })

    @patch.object(MetaDataManager, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3")
    def testSaveMetaDataForPlaylist(self, mockEasyID3, mockSaveEasyID3):
        mockSaveEasyID3.confiugure_mock(return_value=self.metaData)
        self.testMetaData.saveMetaDataForPlaylist(self.metaData, f"{self.testDir}/testTitle.mp3", "testPlaylist")
        mockEasyID3.assert_called_once_with(f"{self.testDir}/testTitle.mp3")

    @patch.object(MetaDataManager, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3")
    def testSaveMetaDataForSingleFile(self, mockEasyID3, mockSaveEasyID3):
        mockSaveEasyID3.confiugure_mock(return_value=self.metaData)
        self.testMetaData.saveMetaDataForSingleFile(self.metaData, f"{self.testDir}/testTitle.mp3")
        mockEasyID3.assert_called_once_with(f"{self.testDir}/testTitle.mp3")

if __name__ == "__main__":
    main()