import sys
sys.path.append("..")
import os
import yt_dlp
import youtubeDL
import configparser
import mutagen.easyid3
import mutagen.mp3
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call
from configParserManager import ConfigParserManager
from metaDataManager import MetaDataManager
from youtubeDataKeys import MediaInfo

songMetaData1 = {
        "title": "Society",
        "album": "Into The Wild",
        "artist": "Eddie Vedder",
        "ext": "webm",
        "playlist_index": 1,
        'original_url': 'https://www.youtube.com/watch?v=ABsslEoL0-c' ,
        "id": 'ABsslEoL0-c'
        }

songMetaData2 =  {
        'title': 'Hard Sun',
        "artist": "Eddie Vedder",
        "ext": "webm",
        "playlist_index": 2,
        'original_url': 'https://www.youtube.com/watch?v=_EZUfnMv3Lg',
        'id': '_EZUfnMv3Lg'
        }

class TestYoutubeDL(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(ConfigParserManager(f'{self.testDir}/test_youtube_config.ini'), MetaDataManager())
        self.youtubeTest.savePath = self.testDir
        self.youtubeTest._ydl_opts['outtmpl'] = self.testDir + '/%(title)s.%(ext)s'

    def updateDict(self, dictToChange):
        songMetaDataUpdated1 = dictToChange
        songMetaDataUpdated1["hash"] = dictToChange["id"]
        songMetaDataUpdated1.pop("id")
        songMetaDataUpdated1.pop("ext")
        if "tracknumber" in songMetaDataUpdated1:
            songMetaDataUpdated1.pop("tracknumber")
        return songMetaDataUpdated1

    def test__downloadFile(self):
        youtubeOptions = {
        # 'download_archive': 'downloaded_songs.txt',
        'addmetadata': True,
        'format': f'best[height=360][ext=mp4]+bestaudio/bestvideo+bestaudio',
        'outtmpl': self.testDir + '/%(title)s' + f'_360p' + '.%(ext)s'
        }
        self.youtubeTest._downloadFile = MagicMock(return_value=songMetaData1)
        metaData =  self.youtubeTest._downloadFile("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        self.youtubeTest._downloadFile.assert_called_once_with("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        self.assertEqual(metaData, songMetaData1)

    def testSetVideoOptions(self):
        formatBeforeChange = self.youtubeTest.ydl_opts["format"]
        listOfFormats = ['360','480', '720', '1080', '2160', 'mp3']
        for format_type in listOfFormats:
            self.youtubeTest.setVideoOptions(format_type)
            self.assertNotEqual(formatBeforeChange, self.youtubeTest.ydl_opts["format"])
            self.assertEqual(f'best[height={format_type}][ext=mp4]+bestaudio/bestvideo+bestaudio', self.youtubeTest.ydl_opts["format"])

    def testGetVideoHash(self):
        correctVideoHash = "ABsslEoL0-c"
        testVideoHash1 = self.youtubeTest.getSingleMediaHash("https://www.youtube.com/watch?v=ABsslEoL0-c")
        testVideoHash2 = self.youtubeTest.getSingleMediaHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO")
        testVideoHash3 = self.youtubeTest.getSingleMediaHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO&index=1")
        wrong_link_with_video = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
        self.assertEqual(testVideoHash1, correctVideoHash)
        self.assertEqual(testVideoHash2, correctVideoHash)
        self.assertEqual(testVideoHash3, correctVideoHash)
        with self.assertRaises(ValueError) as context:
            self.youtubeTest.getSingleMediaHash(wrong_link_with_video)
        self.assertTrue('This a playlist only - without video hash to download' in str(context.exception))

    def testGetPlaylistHash(self):
        correectPlaylistHash = "PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
        testVideoHash1 = self.youtubeTest.getPlaylistHash("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO")
        testVideoHash2 = self.youtubeTest.getPlaylistHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO")
        testVideoHash3 = self.youtubeTest.getPlaylistHash("https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO&index=1")
        wrong_link_with_video = "https://www.youtube.com/watch?v=ABsslEoL0-c"
        self.assertEqual(testVideoHash1, correectPlaylistHash)
        self.assertEqual(testVideoHash2, correectPlaylistHash)
        self.assertEqual(testVideoHash3, correectPlaylistHash)
        with self.assertRaises(ValueError) as context:
            self.youtubeTest.getPlaylistHash(wrong_link_with_video)
        self.assertTrue('This is not a playlist' in str(context.exception))

    @patch.object(youtubeDL.YoutubeDL, "_downloadFile", return_value=songMetaData1)
    def testDownloadVideo(self, mockDownload):
        metaData = self.youtubeTest.downloadVideo("https://www.youtube.com/watch?v=ABsslEoL0-c", "480")
        mockDownload.assert_called_once_with("ABsslEoL0-c")
        self.assertEqual(songMetaData1, metaData)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=ValueError("Download media info error ValueError"))
    def testDownloadVideoWithError(self, mockDownloadFile,):
        errorMsg = self.youtubeTest.downloadVideo("https://www.youtube.com/watch?v=ABsslEoL0-c", "480")
        calls = [call('ABsslEoL0-c', download=False), call("ABsslEoL0-c")]
        mockDownloadFile.assert_any_call("ABsslEoL0-c")
        mockDownloadFile.assert_any_call('ABsslEoL0-c', download=False)
        mockDownloadFile.assert_has_calls(calls)
        self.assertEqual(mockDownloadFile.mock_calls[0], call('ABsslEoL0-c', download=False))
        self.assertEqual(mockDownloadFile.mock_calls[1], call("ABsslEoL0-c"))
        self.assertEqual(errorMsg,  "Download media info error ValueError")

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title": "testPlaylist", "entries":[songMetaData1,
                                                                                                      songMetaData2]})
    @patch.object(youtubeDL.YoutubeDL, "_downloadFile")
    def testDownloadVideoPlaylist(self, mockDownload, mockExtractinfo):
        metaData = self.youtubeTest.downloadVideoPlaylist("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO", "480")
        self.assertEqual(mockExtractinfo.mock_calls[0], call('PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO', download=False))
        calls = [call("ABsslEoL0-c"), call("_EZUfnMv3Lg")]
        self.assertEqual(mockDownload.mock_calls[0], call('ABsslEoL0-c'))
        self.assertEqual(mockDownload.mock_calls[1], call("_EZUfnMv3Lg"))
        mockDownload.assert_has_calls(calls)
        self.assertEqual(mockDownload.call_count, 2)
        self.assertEqual(None, metaData)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=ValueError("Download media info error ValueError"))
    def testDownloadVideoPlaylistWithError(self, mockDownloadError):
        errorMsg = self.youtubeTest.downloadVideoPlaylist("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO", "480")
        mockDownloadError.assert_called_once_with("PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO", download=False)
        self.assertEqual(errorMsg,  "Download media info error ValueError")

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title": "testPlaylist", "entries":[songMetaData1,
                                                                                                      songMetaData2]})
    @patch.object(youtubeDL.MetaDataManager, "setMetaDataSingleFile")
    @patch.object(youtubeDL.YoutubeDL, "_downloadFile", return_value=songMetaData1)
    def testDownloadPlaylistAudio(self, mockDownload, mockSetMetaData, mockExtractinfo):
        metaData = self.youtubeTest.downloadAudioPlaylist("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO")
        self.assertEqual(mockExtractinfo.mock_calls[0], call('PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO', download=False))
        calls = [call("ABsslEoL0-c"), call("_EZUfnMv3Lg")]
        mockDownload.assert_has_calls(calls)
        self.assertEqual(mockDownload.mock_calls[0], call('ABsslEoL0-c'))
        self.assertEqual(mockDownload.mock_calls[1], call("_EZUfnMv3Lg"))
        self.assertEqual(mockDownload.call_count, 2)
        self.assertEqual(mockSetMetaData.mock_calls[0], call(songMetaData1, self.youtubeTest.savePath))
        self.assertEqual(mockSetMetaData.mock_calls[1], call(songMetaData1, self.youtubeTest.savePath))
        self.assertEqual(mockSetMetaData.call_count, 2)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=ValueError("Download media info error ValueError"))
    def testDownloadPlaylistAudioWithError(self, mockDownloadError):
        errorMsg = self.youtubeTest.downloadAudioPlaylist("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO")
        mockDownloadError.assert_called_once_with("PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO", download=False)
        self.assertEqual(errorMsg,  "Download media info error ValueError")

    def getMetaDataFromYoutube(youtubeURL):
            return {
                "title": "Society",
                "album": "Into The Wild",
                "artist": "Eddie Vedder",
                "ext": "webm",
                "playlist_index": None
                }

    @patch.object(youtubeDL.MetaDataManager, "showMetaDataInfo")
    @patch.object(youtubeDL.MetaDataManager, "saveEasyID3")
    @patch.object(mutagen.easyid3, "EasyID3", return_value=songMetaData1)
    @patch.object(youtubeDL.YoutubeDL,"_downloadFile", side_effect=getMetaDataFromYoutube)
    def testDownloadAudio(self, mockDownloadFile, mockEasyID3, mockSave, mockShowMetaData):
        singleMediaInfoResult = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        metaData = singleMediaInfoResult.getData()
        mockDownloadFile.assert_called_once_with("ABsslEoL0-c")
        mockEasyID3.assert_called_once()
        mockSave.assert_called_once()
        mockShowMetaData.assert_called_once()
        self.assertEqual("Society", metaData["title"])
        self.assertEqual("Into The Wild", metaData["album"])
        self.assertEqual("Eddie Vedder", metaData["artist"])
        self.assertIsNone(metaData["playlist_index"])

    @patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=ValueError("Download media info error ValueError"))
    def testDownloadAudioWithError(self, mockDownloadFile,):
        errorMsg = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        calls = [call('ABsslEoL0-c', download=False), call("ABsslEoL0-c")]
        mockDownloadFile.assert_any_call("ABsslEoL0-c")
        mockDownloadFile.assert_any_call('ABsslEoL0-c', download=False)
        mockDownloadFile.assert_has_calls(calls)
        self.assertEqual(mockDownloadFile.mock_calls[0], call('ABsslEoL0-c', download=False))
        self.assertEqual(mockDownloadFile.mock_calls[1], call("ABsslEoL0-c"))
        self.assertEqual(errorMsg,  "Download media info error ValueError")

    @patch.object(youtubeDL.YoutubeDL, "downloadAudioPlaylist")
    @patch.object(youtubeDL.ConfigParserManager, "getUrlOfPlaylists", return_value=["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO",\
                                                                               "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"])
    def testDownloadAudioFromConfigTwoPlaylists(self, mockGetPlaylists, mockDownloadAudio):
        metaData = self.youtubeTest.downoladConfigPlaylistAudio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadAudio.call_count, 2)

    @patch.object(youtubeDL.YoutubeDL, "downloadAudioPlaylist")
    @patch.object(youtubeDL.ConfigParserManager, "getUrlOfPlaylists", return_value=[])
    def testDownloadAudioFromConfigZeroPlaylists(self, mockGetPlaylists, mockDownloadAudio):
        metaData = self.youtubeTest.downoladConfigPlaylistAudio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadAudio.call_count, 0)

    @patch.object(youtubeDL.YoutubeDL, "setVideoOptions")
    @patch.object(youtubeDL.YoutubeDL, "downloadVideoPlaylist")
    @patch.object(youtubeDL.ConfigParserManager, "getUrlOfPlaylists", return_value=["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"])
    def testDownloadVideoFromConfigOnePlaylists(self, mockGetPlaylists, mockDownloadVideo, mockSetVideo):
        type = "720"
        metaData = self.youtubeTest.downoladConfigPlaylistVideo(type)
        mockGetPlaylists.assert_called_once()
        mockDownloadVideo.assert_called_once_with("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO", type)
        mockSetVideo.assert_called_once_with(type)

    @patch.object(youtubeDL.YoutubeDL, "setVideoOptions")
    @patch.object(youtubeDL.YoutubeDL, "downloadVideoPlaylist")
    @patch.object(youtubeDL.ConfigParserManager, "getUrlOfPlaylists", return_value=["https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO", \
                                                                                    "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"])
    def testDownloadVideoFromConfigTwoPlaylists(self, mockGetPlaylists, mockDownloadVideo, mockSetVideo):
        type = "720"
        metaData = self.youtubeTest.downoladConfigPlaylistVideo(type)
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadVideo.call_count, 2)
        mockDownloadVideo.assert_has_calls([call('https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO', '720'), \
                                            call('https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU', '720')])
        mockSetVideo.assert_called_once_with(type)
        self.assertEqual(mockDownloadVideo.call_count, 2)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title": "Society","album": "Into The Wild","artist": "Eddie Vedder","ext": "webm","playlist_index": None, 'original_url': 'ABsslEoL0-c', "id": 'ABsslEoL0-c'})
    def testgetSingleMediaInfo(self, mockExtractInfo):
        testMediaInfo = self.youtubeTest.getSingleMediaInfo("https://www.youtube.com/watch?v=ABsslEoL0-c")
        mockExtractInfo.assert_called_once()
        self.assertEqual(testMediaInfo, {'title': 'Society', 'album': 'Into The Wild', 'artist': 'Eddie Vedder', 'hash': 'ABsslEoL0-c', 'original_url': 'ABsslEoL0-c'})

    @patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=ValueError("Download media info error ValueError"))
    def testgetSingleMediaInfoWithError(self, mockExtractInfo):
        testMediaInfo = self.youtubeTest.getSingleMediaInfo("https://www.youtube.com/watch?v=ABsslEoL0-c")
        mockExtractInfo.assert_called_once()
        self.assertTrue(testMediaInfo,  "Download media info error ValueError")

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title": "testPlaylist", "entries":[songMetaData1,
                                                                                                      songMetaData2]})
    def testgetPlaylistMediaInfo(self, mockDownloadFile):
        testMediaInfo = self.youtubeTest.getPlaylistMediaInfo("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO")
        mockDownloadFile.assert_called_once()
        songMetaDataUpdated1 = self.updateDict(songMetaData1)
        songMetaDataUpdated2 = self.updateDict(songMetaData2)
        self.assertEqual(testMediaInfo[0], songMetaDataUpdated1)
        self.assertEqual(testMediaInfo[1], songMetaDataUpdated2)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=ValueError("Download media info error ValueError"))
    def testgetPlaylistMediaInfoWithError(self, mockDownloadFile):
        testMediaInfo = self.youtubeTest.getPlaylistMediaInfo("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO")
        mockDownloadFile.assert_called_once()
        self.assertTrue(testMediaInfo,  "Download media info error ValueError")

if __name__ == "__main__":
    main()