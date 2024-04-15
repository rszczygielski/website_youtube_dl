import os
import yt_dlp
import common.youtubeDL as youtubeDL
import mutagen.easyid3
import mutagen.mp3
from unittest import TestCase, main
from unittest.mock import patch, call
from common.youtubeConfigManager import ConfigParserManager
from common.metaDataManager import MetaDataManager


class TestYoutubeDL(TestCase):
    mainURL1 = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    mainPlaylistUrlWithVideoHash1 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    mainPlaylistUrlNoVideoHash1 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    mainPlaylistUrlNoVideoHash2 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    mainPlaylistUrlWithIndex1 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO&index=1"
    mainPlaylistHash = "PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    mainMediaDownloadError = "Download media info error ValueError"
    mainPlaylistWithoutVideoError = 'This a playlist only - without video hash to download'

    testPlaylistName = "testPlaylist"
    testTitle1 = "Society"
    testAlbum1 = "Into The Wild"
    testArtist1 = "Eddie Vedder"
    testExt1 = "webm"
    testPlaylistIndex1 = 1
    testOriginalUrl1 = 'https://www.youtube.com/watch?v=ABsslEoL0-c'
    testId1 = 'ABsslEoL0-c'
    testTitle2 = 'Hard Sun'
    testArtist2 = "Eddie Vedder"
    testExt2 = "webm"
    testPlaylistIndex2 = 2
    testOriginalUrl2 = 'https://www.youtube.com/watch?v=_EZUfnMv3Lg'
    testId2 = '_EZUfnMv3Lg'

    songMetaData1 = {
        "title": testTitle1,
        "album": testAlbum1,
        "artist": testArtist1,
        "ext": testExt1,
        "playlist_index": testPlaylistIndex1,
        'original_url': testOriginalUrl1,
        "id": testId1
    }

    songMetaData2 = {
        'title': testTitle2,
        "artist": testArtist2,
        "ext": testExt2,
        "playlist_index": testPlaylistIndex2,
        'original_url': testOriginalUrl2,
        'id': testId2
    }
    testEntriesList = [songMetaData1, songMetaData2, None]
    testPlaylsitUrlsList = [
        mainPlaylistUrlNoVideoHash1, mainPlaylistUrlNoVideoHash2]

    plalistMetaData = {
        "title": testPlaylistName,
        "entries": testEntriesList
    }

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(ConfigParserManager(
            f'{self.testDir}/test_youtube_config.ini'), MetaDataManager())
        self.youtubeTest._savePath = self.testDir
        self.youtubeTest._ydl_opts['outtmpl'] = self.testDir + \
            '/%(title)s.%(ext)s'

    def checkResultMetaData1(
            self, singleMedia, playlist_index=None):
        if not singleMedia.title == self.testTitle1:
            return False
        if not singleMedia.album == self.testAlbum1:
            return False
        if not singleMedia.artist == self.testArtist1:
            return False
        if not singleMedia.extension == self.testExt1:
            return False
        if not singleMedia.playlistIndex == playlist_index:
            return False
        if not singleMedia.url == self.mainURL1:
            return False
        if not singleMedia.ytHash == self.testId1:
            return False
        else:
            return True

    def checkResultMetaData2(self, singleMedia):
        if not singleMedia.title == self.testTitle2:
            return False
        if not singleMedia.album == "":
            return False
        if not singleMedia.artist == self.testArtist2:
            return False
        if not singleMedia.extension == self.testExt2:
            return False
        if not singleMedia.playlistIndex == 2:
            return False
        if not singleMedia.url == self.testOriginalUrl2:
            return False
        if not singleMedia.ytHash == self.testId2:
            return False
        else:
            return True

    def checkResultMetaData1Playlist(self, playlistMedia):
        if not playlistMedia.playlistName == self.testPlaylistName:
            return False
        if not len(playlistMedia.singleMediaList) > 0:
            return False
        if not self.checkResultMetaData1(
                playlistMedia.singleMediaList[0], 1):
            return False
        if not self.checkResultMetaData2(playlistMedia.singleMediaList[1]):
            return False
        else:
            return True

    def checkFastDownloadResult(self, metaData):
        resultTest = {'title': 'testPlaylist', 'entries': [
            self.songMetaData1, self.songMetaData2, None]}
        if metaData != resultTest:
            return False
        else:
            return True

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def testDownloadFile(self, mockExtractinfo):
        resultOfYoutube = self.youtubeTest._downloadFile(self.mainURL1)
        self.assertEqual(False, resultOfYoutube.isError())
        mockExtractinfo.assert_called_once_with(self.mainURL1)
        metaData = resultOfYoutube.getData()
        self.assertEqual(metaData, self.songMetaData1)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testDownloadFileWithError(self, mockExtractinfo):
        resultOfYoutube = self.youtubeTest._downloadFile(self.mainURL1)
        self.assertEqual(True, resultOfYoutube.isError())
        mockExtractinfo.assert_called_once_with(self.mainURL1)
        errorMsg = resultOfYoutube.getErrorInfo()
        self.assertEqual(errorMsg, self.mainMediaDownloadError)

    def testSetVideoOptions(self):
        formatBeforeChange = self.youtubeTest._ydl_opts["format"]
        listOfFormats = ['360', '480', '720', '1080', '2160', 'mp3']
        for format_type in listOfFormats:
            self.youtubeTest._setVideoOptions(format_type)
            self.assertNotEqual(formatBeforeChange,
                                self.youtubeTest._ydl_opts["format"])
            self.assertEqual(
                f'best[height={format_type}][ext=mp4]+bestaudio/bestvideo+bestaudio',
                self.youtubeTest._ydl_opts["format"])

    def testGetVideoHash(self):
        correctVideoHash = self.testId1
        testVideoHash1 = self.youtubeTest._getSingleMediaResultHash(self.mainURL1)
        testVideoHash2 = self.youtubeTest._getSingleMediaResultHash(
            self.mainPlaylistUrlWithVideoHash1)
        testVideoHash3 = self.youtubeTest._getSingleMediaResultHash(
            self.mainPlaylistUrlWithIndex1)
        wrong_link_with_video = self.mainPlaylistUrlNoVideoHash1
        self.assertEqual(testVideoHash1, correctVideoHash)
        self.assertEqual(testVideoHash2, correctVideoHash)
        self.assertEqual(testVideoHash3, correctVideoHash)
        with self.assertRaises(ValueError) as context:
            self.youtubeTest._getSingleMediaResultHash(wrong_link_with_video)
        self.assertTrue(
            self.mainPlaylistWithoutVideoError in str(context.exception))

    def testGetPlaylistHash(self):
        correectPlaylistHash = self.mainPlaylistHash
        testVideoHash1 = self.youtubeTest._getPlaylistHash(
            self.mainPlaylistUrlNoVideoHash1)
        testVideoHash2 = self.youtubeTest._getPlaylistHash(
            self.mainPlaylistUrlWithVideoHash1)
        testVideoHash3 = self.youtubeTest._getPlaylistHash(
            self.mainPlaylistUrlWithIndex1)
        wrong_link_with_video = self.mainURL1
        self.assertEqual(testVideoHash1, correectPlaylistHash)
        self.assertEqual(testVideoHash2, correectPlaylistHash)
        self.assertEqual(testVideoHash3, correectPlaylistHash)
        with self.assertRaises(ValueError) as context:
            self.youtubeTest._getPlaylistHash(wrong_link_with_video)
        self.assertTrue('This is not a playlist' in str(context.exception))

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value=songMetaData1)
    def testDownloadVideo(self, mockDownloadFile):
        youtubeResult = self.youtubeTest.downloadVideo(self.mainURL1, "480")
        singleMedia = youtubeResult.getData()
        mockDownloadFile.assert_called_once_with(self.testId1)
        resultCheck = self.checkResultMetaData1(singleMedia)
        self.assertEqual(True, resultCheck)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testDownloadVideoWithError(self, mockDownloadFile,):
        youtubeResult = self.youtubeTest.downloadVideo(self.mainURL1, "480")
        mockDownloadFile.assert_any_call(self.testId1)
        self.assertEqual(mockDownloadFile.mock_calls[0], call(self.testId1))
        self.assertEqual(youtubeResult.isError(), True)
        self.assertEqual(youtubeResult.getErrorInfo(),
                         self.mainMediaDownloadError)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": testPlaylistName,
                                "entries": testEntriesList})
    def testFastDownloadVideoPlaylist(self, mockExtractinfo):
        resultOfYoutube = self.youtubeTest.fastDownloadVideoPlaylist(
            self.mainPlaylistUrlNoVideoHash1, "480")
        metaData = resultOfYoutube.getData()
        mockExtractinfo.assert_called_once_with(self.mainPlaylistHash)
        checkResult = self.checkFastDownloadResult(metaData)
        self.assertEqual(True, checkResult)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testDownloadVideoPlaylistWithError(self, mockDownloadError):
        resultOfYoutube = self.youtubeTest.fastDownloadVideoPlaylist(
            self.mainPlaylistUrlNoVideoHash1, "480")
        self.assertEqual(resultOfYoutube.isError(), True)
        errorMsg = resultOfYoutube.getErrorInfo()
        mockDownloadError.assert_called_once_with(self.mainPlaylistHash)
        self.assertEqual(errorMsg, self.mainMediaDownloadError)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": testPlaylistName,
                                "entries": testEntriesList})
    @patch.object(youtubeDL.MetaDataManager, "setMetaDataPlaylist")
    def testFastDownloadPlaylistAudio(self, mockSetMetaData, mockExtractinfo):
        resultOfYoutube = self.youtubeTest.fastDownloadAudioPlaylist(
            self.mainPlaylistUrlNoVideoHash1)
        metaData = resultOfYoutube.getData()
        mockExtractinfo.assert_called_once_with(self.mainPlaylistHash)
        mockSetMetaData.assert_called_once_with(
            self.testPlaylistName, self.testEntriesList, self.testDir)
        checkResult = self.checkFastDownloadResult(metaData)
        self.assertEqual(True, checkResult)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": testPlaylistName})
    def testFastDownloadPlaylistAudioNoEntries(self, mockExtractinfo):
        functionResult = self.youtubeTest.fastDownloadAudioPlaylist(
            self.mainPlaylistUrlNoVideoHash1)
        mockExtractinfo.assert_called_once_with(self.mainPlaylistHash)
        self.assertEqual(False, functionResult)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testFastDownloadPlaylistAudioWithError(self, mockDownloadError):
        resultOfYoutube = self.youtubeTest.fastDownloadAudioPlaylist(
            self.mainPlaylistUrlNoVideoHash1)
        self.assertEqual(resultOfYoutube.isError(), True)
        errorMsg = resultOfYoutube.getErrorInfo()
        mockDownloadError.assert_called_once_with(self.mainPlaylistHash)
        self.assertEqual(errorMsg, self.mainMediaDownloadError)

    @patch.object(youtubeDL.MetaDataManager, "setMetaDataSingleFile")
    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def testDownloadAudio(self, mockDownloadFile, mockSave):
        singleMediaInfoResult = self.youtubeTest.downloadAudio(self.mainURL1)
        metaData = singleMediaInfoResult.getData()
        mockDownloadFile.assert_called_once_with(self.testId1)
        mockSave.assert_called_once()
        resultCheck = self.checkResultMetaData1(metaData)
        self.assertEqual(True, resultCheck)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testDownloadAudioWithError(self, mockDownloadFile):
        youtubeResult = self.youtubeTest.downloadAudio(self.mainURL1)
        self.assertEqual(youtubeResult.isError(), True)
        mockDownloadFile.assert_called_once_with(self.testId1)
        self.assertEqual(youtubeResult.getErrorInfo(),
                         self.mainMediaDownloadError)

    @patch.object(youtubeDL.YoutubeDL, "fastDownloadAudioPlaylist")
    @patch.object(youtubeDL.ConfigParserManager,
                  "getUrlOfPlaylists",
                  return_value=testPlaylsitUrlsList)
    def testDownloadAudioFromConfigTwoPlaylists(
            self, mockGetPlaylists, mockDownloadAudio):
        metaData = self.youtubeTest.downoladAllConfigPlaylistsAudio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadAudio.call_count, 2)
        self.assertEqual(metaData, True)

    @patch.object(youtubeDL.YoutubeDL, "fastDownloadAudioPlaylist")
    @patch.object(youtubeDL.ConfigParserManager,
                  "getUrlOfPlaylists", return_value=[])
    def testDownloadAudioFromConfigZeroPlaylists(
            self, mockGetPlaylists, mockDownloadAudio):
        metaData = self.youtubeTest.downoladAllConfigPlaylistsAudio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadAudio.call_count, 0)
        self.assertEqual(metaData, True)

    @patch.object(youtubeDL.YoutubeDL, "_setVideoOptions")
    @patch.object(youtubeDL.YoutubeDL, "fastDownloadVideoPlaylist")
    @patch.object(youtubeDL.ConfigParserManager,
                  "getUrlOfPlaylists",
                  return_value=[mainPlaylistUrlNoVideoHash1])
    def testDownloadVideoFromConfigOnePlaylists(
            self, mockGetPlaylists, mockDownloadVideo, mockSetVideo):
        type = "720"
        metaData = self.youtubeTest.downoladAllConfigPlaylistsVideo(type)
        mockGetPlaylists.assert_called_once()
        mockDownloadVideo.assert_called_once_with(
            self.mainPlaylistUrlNoVideoHash1, type)
        mockSetVideo.assert_called_once_with(type)
        self.assertEqual(metaData, True)

    @patch.object(youtubeDL.YoutubeDL, "_setVideoOptions")
    @patch.object(youtubeDL.YoutubeDL, "fastDownloadVideoPlaylist")
    @patch.object(youtubeDL.ConfigParserManager,
                  "getUrlOfPlaylists",
                  return_value=testPlaylsitUrlsList)
    def testDownloadVideoFromConfigTwoPlaylists(
            self, mockGetPlaylists, mockDownloadVideo, mockSetVideo):
        type = "720"
        metaData = self.youtubeTest.downoladAllConfigPlaylistsVideo(type)
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadVideo.call_count, 2)
        mockDownloadVideo.assert_has_calls([call(self.mainPlaylistUrlNoVideoHash1, type),
                                            call(self.mainPlaylistUrlNoVideoHash2, type)])
        mockSetVideo.assert_called_once_with(type)
        self.assertEqual(mockDownloadVideo.call_count, 2)
        self.assertEqual(metaData, True)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def testrequestSingleMediaInfo(self, mockExtractInfo):
        resultOfYoutube = self.youtubeTest.requestSingleMediaInfo(
            self.mainURL1)
        mockExtractInfo.assert_called_once()
        self.assertEqual(False, resultOfYoutube.isError())
        resultMetaData = resultOfYoutube.getData()
        resultCheck = self.checkResultMetaData1(resultMetaData)
        self.assertEqual(True, resultCheck)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testgetSingleMediaInfoWithError(self, mockExtractInfo):
        resultOfYoutube = self.youtubeTest.getSingleMediaInfo(self.mainURL1)
        mockExtractInfo.assert_called_once()
        self.assertEqual(True, resultOfYoutube.isError())
        errorMsg = resultOfYoutube.getErrorInfo()
        self.assertTrue(errorMsg, self.mainMediaDownloadError)
        self.assertFalse(resultOfYoutube.getData())

    @patch.object(yt_dlp.YoutubeDL,
                  "extract_info",
                  return_value={"title": testPlaylistName,
                                "entries": testEntriesList})
    def testgetPlaylistMediaInfo(self, mockDownloadFile):
        resultOfYoutube = self.youtubeTest.getPlaylistMediaInfo(
            self.mainPlaylistUrlNoVideoHash1)
        mockDownloadFile.assert_called_once()
        self.assertEqual(False, resultOfYoutube.isError())
        palylistMedia = resultOfYoutube.getData()
        resultCheck = self.checkResultMetaData1Playlist(
            palylistMedia)
        self.assertEqual(True, resultCheck)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testgetPlaylistMediaInfoWithError(self, mockExtractInfo):
        resultOfYoutube = self.youtubeTest.getPlaylistMediaInfo(
            self.mainPlaylistUrlNoVideoHash1)
        mockExtractInfo.assert_called_once()
        self.assertEqual(True, resultOfYoutube.isError())
        errorMsg = resultOfYoutube.getErrorInfo()
        self.assertTrue(errorMsg, self.mainMediaDownloadError)
        self.assertFalse(resultOfYoutube.getData())

    def testGetPlaylistMediaResult(self):
        playlistMedia = self.youtubeTest._getPlaylistMediaResult(
            self.plalistMetaData)
        resultCheck = self.checkResultMetaData1Playlist(
            playlistMedia)
        self.assertTrue(resultCheck)

    def testGetSingleMediaResult(self):
        singleMedia = self.youtubeTest._getSingleMediaResult(
            self.songMetaData1)
        resultCheck = self.checkResultMetaData1(
            singleMedia)
        self.assertTrue(resultCheck)


if __name__ == "__main__":
    main()
