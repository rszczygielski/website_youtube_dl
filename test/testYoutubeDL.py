import os
import youtubeDL
import configparser
import mutagen.easyid3
import mutagen.mp3
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call

class TestYoutubeDL(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(youtubeDL.ConfigParserMenager(f'{self.testDir}/test_youtube_config.ini'), youtubeDL.MetaDataMenager())
        self.youtubeTest.savePath = self.testDir
        self.youtubeTest.ydl_audio_opts['outtmpl'] = self.testDir + '/%(title)s.%(ext)s'
        self.testMetaData = {
        "title": "Society",
        "album": "Into The Wild",
        "artist": "Eddie Vedder",
        "ext": "webm",
        "playlist_index": None
        }
        self.testMetaDataPlaylist = {
            "title": "testPlaylist",
            "entries":[{"title": "Society",
                        "album": "Into The Wild",
                        "artist":"Eddie Vedder",
                        "ext": "webm",
                        "playlist_index": None}]
            }

    def test_downloadFile(self):
        youtubeOptions = {
        # 'download_archive': 'downloaded_songs.txt',
        'addmetadata': True,
        'format': f'bestvideo[height=360][ext=mp4]+bestaudio/bestvideo+bestaudio',
        'outtmpl': self.testDir + '/%(title)s' + f'_360p' + '.%(ext)s'
        }
        self.youtubeTest.downloadFile = MagicMock(return_value=self.testMetaData)
        metaData =  self.youtubeTest.downloadFile("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        self.youtubeTest.downloadFile.assert_called_once_with("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        self.assertEqual(metaData, self.testMetaData)

    def testSetVideoOptions(self):
        formatBeforeChange = self.youtubeTest.ydl_video_opts["format"]
        listOfFormats = ['360','480', '720', '1080', '2160', 'mp3']
        for format_type in listOfFormats:
            self.youtubeTest.setVideoOptions(format_type)
            self.assertNotEqual(formatBeforeChange, self.youtubeTest.ydl_video_opts["format"])
            self.assertEqual(f'bestvideo[height={format_type}][ext=mp4]+bestaudio/bestvideo+bestaudio', self.youtubeTest.ydl_video_opts["format"])

    def testGetVideoHash(self):
        correctVideoHash = "ABsslEoL0-c"
        testVideoHash1 = self.youtubeTest.getVideoHash("https://www.youtube.com/watch?v=ABsslEoL0-c")
        testVideoHash2 = self.youtubeTest.getVideoHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0")
        testVideoHash3 = self.youtubeTest.getVideoHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO&index=1")
        wrong_link_with_video = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0"
        self.assertEqual(testVideoHash1, correctVideoHash)
        self.assertEqual(testVideoHash2, correctVideoHash)
        self.assertEqual(testVideoHash3, correctVideoHash)
        with self.assertRaises(ValueError):
            self.youtubeTest.getVideoHash(wrong_link_with_video)

    def testGetPlaylistHash(self):
        correectPlaylistHash = "PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0"
        testVideoHash1 = self.youtubeTest.getPlaylistHash("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0")
        testVideoHash2 = self.youtubeTest.getPlaylistHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0")
        testVideoHash3 = self.youtubeTest.getPlaylistHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0&index=1")
        wrong_link_with_video = "https://www.youtube.com/watch?v=ABsslEoL0-c"
        self.assertEqual(testVideoHash1, correectPlaylistHash)
        self.assertEqual(testVideoHash2, correectPlaylistHash)
        self.assertEqual(testVideoHash3, correectPlaylistHash)
        with self.assertRaises(ValueError):
            self.youtubeTest.getPlaylistHash(wrong_link_with_video)

    @patch.object(youtubeDL.YoutubeDL, "downloadFile", return_value={"title": "Society","album": "Into The Wild","artist": "Eddie Vedder","ext": "webm","playlist_index": None})
    def testDownloadVideo(self, mockDownload):
        metaData = self.youtubeTest.downloadVideo("https://www.youtube.com/watch?v=ABsslEoL0-c", "480")
        mockDownload.assert_called_once_with("ABsslEoL0-c", self.youtubeTest.ydl_video_opts)
        self.assertEqual(self.testMetaData, metaData)

    @patch.object(youtubeDL.YoutubeDL, "downloadFile", return_value={"title": "testPlaylist", "entries":[{"title": "Society","album": "Into The Wild","artist": "Eddie Vedder","ext": "webm","playlist_index": None}]})
    def testDownloadVideoPlaylist(self, mockDownload):
        metaData = self.youtubeTest.downloadVideoPlaylist("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0", "480")
        mockDownload.assert_called_once_with("PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0", self.youtubeTest.ydl_video_opts)
        self.assertEqual(self.testMetaDataPlaylist, metaData)

    @patch.object(youtubeDL.MetaDataMenager, "setMetaDataPlaylist")
    @patch.object(youtubeDL.YoutubeDL, "downloadFile", return_value={"title": "testPlaylist", "entries":[{"title": "Society","album": "Into The Wild","artist": "Eddie Vedder","ext": "webm","playlist_index": None}]})
    def testDownloadPlaylistAudio(self, mockDownload, mockSetMetaData):
        metaData = self.youtubeTest.downloadAudioPlaylist("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0")
        mockDownload.assert_called_once_with("PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0", self.youtubeTest.ydl_audio_opts)
        mockSetMetaData.assert_called_once_with(metaData, self.youtubeTest.savePath)
        self.assertEqual(self.testMetaDataPlaylist, metaData)

    def getMetaDataFromYoutube(youtubeURL, youtubeOptions):
            return {
                "title": "Society",
                "album": "Into The Wild",
                "artist": "Eddie Vedder",
                "ext": "webm",
                "playlist_index": None
                }

    @patch.object(youtubeDL.MetaDataMenager, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaDataMenager, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3", return_value={'title': "Society", 'album': "Into The Wild", 'artist': "Eddie Vedder", "tracknumber": None})
    @patch.object(youtubeDL.YoutubeDL,"downloadFile", side_effect=getMetaDataFromYoutube)
    def testDownloadAudio(self, mockDownloadFile, mockEasyID3, mockSave, mockShowMetaData):
        metaData = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        mockDownloadFile.assert_called_once_with("ABsslEoL0-c", self.youtubeTest.ydl_audio_opts)
        mockEasyID3.assert_called_once()
        mockSave.assert_called_once()
        mockShowMetaData.assert_called_once()
        self.assertEqual("Society", metaData["title"])
        self.assertEqual("Into The Wild", metaData["album"])
        self.assertEqual("Eddie Vedder", metaData["artist"])
        self.assertIsNone(metaData["playlist_index"])

    @patch.object(youtubeDL.YoutubeDL, "downloadAudioPlaylist")
    @patch.object(youtubeDL.ConfigParserMenager, "getUrlOfPlaylists", return_value=["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0",\
                                                                               "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"])
    def testDownloadAudioFromConfigTwoPlaylists(self, mockGetPlaylists, mockDownloadAudio):
        metaData = self.youtubeTest.downoladConfigPlaylistAudio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadAudio.call_count, 2)

    @patch.object(youtubeDL.YoutubeDL, "downloadAudioPlaylist")
    @patch.object(youtubeDL.ConfigParserMenager, "getUrlOfPlaylists", return_value=[])
    def testDownloadAudioFromConfigZeroPlaylists(self, mockGetPlaylists, mockDownloadAudio):
        metaData = self.youtubeTest.downoladConfigPlaylistAudio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadAudio.call_count, 0)

    @patch.object(youtubeDL.YoutubeDL, "setVideoOptions")
    @patch.object(youtubeDL.YoutubeDL, "downloadVideoPlaylist")
    @patch.object(youtubeDL.ConfigParserMenager, "getUrlOfPlaylists", return_value=["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0"])
    def testDownloadVideoFromConfigOnePlaylists(self, mockGetPlaylists, mockDownloadVideo, mockSetVideo):
        type = "720"
        metaData = self.youtubeTest.downoladConfigPlaylistVideo(type)
        mockGetPlaylists.assert_called_once()
        mockDownloadVideo.assert_called_once_with("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0", type)
        mockSetVideo.assert_called_once_with(type)

    @patch.object(youtubeDL.YoutubeDL, "setVideoOptions")
    @patch.object(youtubeDL.YoutubeDL, "downloadVideoPlaylist")
    @patch.object(youtubeDL.ConfigParserMenager, "getUrlOfPlaylists", return_value=["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0", \
                                                                                    "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"])
    def testDownloadVideoFromConfigTwoPlaylists(self, mockGetPlaylists, mockDownloadVideo, mockSetVideo):
        type = "720"
        metaData = self.youtubeTest.downoladConfigPlaylistVideo(type)
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadVideo.call_count, 2)
        mockDownloadVideo.assert_has_calls([call('https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0', '720'), \
                                            call('https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU', '720')])
        mockSetVideo.assert_called_once_with(type)
        self.assertEqual(mockDownloadVideo.call_count, 2)

class MetaDataTest(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.testMetaData = youtubeDL.MetaDataMenager()
        self.metaDataPlaylist = {
            "title": "testPlaylist",
            "entries": [{
                youtubeDL.MetaDataType.TITLE.value: "testTitle",
                youtubeDL.MetaDataType.ALBUM.value: "testAlbum",
                youtubeDL.MetaDataType.ARTIST.value: "testArtist",
                youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1
            }]}
        self.metaData ={
                youtubeDL.MetaDataType.TITLE.value: "testTitle",
                youtubeDL.MetaDataType.ALBUM.value: "testAlbum",
                youtubeDL.MetaDataType.ARTIST.value: "testArtist",
                youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1
            }

    @patch.object(youtubeDL.MetaDataMenager, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaDataMenager, "saveMetaDataForPlaylist")
    def testSetMetaDataPlaylist(self, mockSavePlaylist, mockShow):
        self.testMetaData.setMetaDataPlaylist(self.metaDataPlaylist, self.testDir)
        mockSavePlaylist.assert_called_once_with({
                youtubeDL.MetaDataType.TITLE.value: "testTitle",
                youtubeDL.MetaDataType.ALBUM.value: "testAlbum",
                youtubeDL.MetaDataType.ARTIST.value: "testArtist",
                youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle.mp3", "testPlaylist")
        mockShow.assert_called_once_with(f"{self.testDir}/testTitle.mp3")

    @patch.object(youtubeDL.MetaDataMenager, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaDataMenager, "saveMetaDataForPlaylist")
    def testSetMetaDataPlaylistTwoPlaylists(self, mockSavePlaylist, mockShow):
        metaDataPlaylistTwoArgs = self.metaDataPlaylist
        metaDataPlaylistTwoArgs["entries"].append({
                youtubeDL.MetaDataType.TITLE.value: "testTitle2",
                youtubeDL.MetaDataType.ALBUM.value: "testAlbum2",
                youtubeDL.MetaDataType.ARTIST.value: "testArtist2",
                youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1
            })
        self.testMetaData.setMetaDataPlaylist(metaDataPlaylistTwoArgs, self.testDir)
        mockSavePlaylist.assert_has_calls([call(metaDataPlaylistTwoArgs["entries"][0], f"{self.testDir}/testTitle.mp3", "testPlaylist"),
                                           call(metaDataPlaylistTwoArgs["entries"][1], f"{self.testDir}/testTitle2.mp3", "testPlaylist")])
        mockSavePlaylist.assert_called_with({
                youtubeDL.MetaDataType.TITLE.value: "testTitle2",
                youtubeDL.MetaDataType.ALBUM.value: "testAlbum2",
                youtubeDL.MetaDataType.ARTIST.value: "testArtist2",
                youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle2.mp3", "testPlaylist")
        mockShow.assert_called_with(f"{self.testDir}/testTitle2.mp3")

    @patch.object(youtubeDL.MetaDataMenager, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaDataMenager, "saveMetaDataForSingleFile")
    def testSetMetaDataSingleFile(self, mockSaveFile, mockShow):
        self.testMetaData.setMetaDataSingleFile(self.metaData, self.testDir)
        mockSaveFile.assert_called_with({
                youtubeDL.MetaDataType.TITLE.value: "testTitle",
                youtubeDL.MetaDataType.ALBUM.value: "testAlbum",
                youtubeDL.MetaDataType.ARTIST.value: "testArtist",
                youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1
            }, f"{self.testDir}/testTitle.mp3")
        mockShow.assert_called_with(f"{self.testDir}/testTitle.mp3")

    def testGetMetaDataDict(self):
        metaData = {
                youtubeDL.MetaDataType.TITLE.value: "testTitle",
                "testDictKey": "testDictValue",
                youtubeDL.MetaDataType.ALBUM.value: "testAlbum",
                "testDictKey": "testDictValue2",
                youtubeDL.MetaDataType.ARTIST.value: "testArtist",
                youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1,
                "testDictKey": "testDictValue3",
                "testDictKey": "testDictValue4"
            }
        metaDataDict = self.testMetaData.getMetaDataDict(metaData)
        self.assertEqual(metaDataDict, {
            youtubeDL.MetaDataType.TITLE.value: "testTitle",
            youtubeDL.MetaDataType.ALBUM.value: "testAlbum",
            youtubeDL.MetaDataType.ARTIST.value: "testArtist",
            youtubeDL.MetaDataType.PLAYLIST_INDEX.value: 1
            })

    @patch.object(youtubeDL.MetaDataMenager, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3")
    def testSaveMetaDataForPlaylist(self, mockEasyID3, mockSaveEasyID3):
        mockSaveEasyID3.confiugure_mock(return_value=self.metaData)
        self.testMetaData.saveMetaDataForPlaylist(self.metaData, f"{self.testDir}/testTitle.mp3", "testPlaylist")
        mockEasyID3.assert_called_once_with(f"{self.testDir}/testTitle.mp3")

    @patch.object(youtubeDL.MetaDataMenager, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3")
    def testSaveMetaDataForSingleFile(self, mockEasyID3, mockSaveEasyID3):
        mockSaveEasyID3.confiugure_mock(return_value=self.metaData)
        self.testMetaData.saveMetaDataForSingleFile(self.metaData, f"{self.testDir}/testTitle.mp3")
        mockEasyID3.assert_called_once_with(f"{self.testDir}/testTitle.mp3")

class ConfigParserMock(configparser.ConfigParser):

    def read(self, file_path):
        self.read_string("[global]\npath = /home/rszczygielski/pythonVSC/youtube_files\n[playlists]\ntest_playlist = https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO\nnowy_swiat = https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU")

class TestConfigParserMenagerWithMockConfigClass(TestCase):
    def setUp(self):
        self.configParserMock = ConfigParserMock()
        self.config = youtubeDL.ConfigParserMenager("/test/config_file.ini", self.configParserMock)

    @patch.object(configparser.ConfigParser, "clear")
    def testGetSavePath(self, mockClear):
        save_path = self.config.getSavePath()
        self.assertEqual(save_path, "/home/rszczygielski/pythonVSC/youtube_files")
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    def testGetUrlOfPlaylists(self, mockClear):
        testPlaylistLists = self.config.getUrlOfPlaylists()
        self.assertEqual(["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO",\
                          "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"], testPlaylistLists)
        mockClear.assert_called_once()

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(youtubeDL.ConfigParserMenager, "saveConfig")
    def testAddPlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist("testPlaylist", "testURL")
        self.assertEqual(self.configParserMock["playlists"]["testPlaylist"], "testURL")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 3)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(youtubeDL.ConfigParserMenager, "saveConfig")
    def testAddPlaylistWithTheSameName(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.addPlaylist("testPlaylist", "testURL")
        self.assertEqual(self.configParserMock["playlists"]["testPlaylist"], "testURL")
        self.config.addPlaylist("testPlaylist", "newURL")
        self.assertEqual(self.configParserMock["playlists"]["testPlaylist"], "newURL")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 3)
        self.assertEqual(mockSave.call_count, 2)
        self.assertEqual(mockClear.call_count, 3)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(youtubeDL.ConfigParserMenager, "saveConfig")
    def testDeletePlaylist(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlylist("test_playlist")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 1)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

    @patch.object(configparser.ConfigParser, "clear")
    @patch.object(youtubeDL.ConfigParserMenager, "saveConfig")
    def testWrongPlaylistToDelete(self, mockSave, mockClear):
        self.config.getUrlOfPlaylists()
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        self.config.deletePlylist("wrongPlaylist")
        plalistsListCount = len(self.configParserMock["playlists"])
        self.assertEqual(plalistsListCount, 2)
        mockSave.assert_called_once()
        self.assertEqual(mockClear.call_count, 2)

if __name__ == "__main__":
    main()