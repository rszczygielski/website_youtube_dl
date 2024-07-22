import os
import yt_dlp
import mutagen.easyid3
import mutagen.mp3
from unittest import TestCase, main
from unittest.mock import patch, call
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
from website_youtube_dl.common.easyID3Manager import EasyID3Manager
import website_youtube_dl.common.youtubeDL as youtubeDL


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
        "album": testAlbum1,
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

    singleMediaTest = youtubeDL.SingleMedia(testTitle1, testAlbum1,
                                            testArtist1, testId1,
                                            testOriginalUrl1, testExt1)

    mediaFromPlaylistTest1 = youtubeDL.MediaFromPlaylist(testTitle1,testId1)

    mediaFromPlaylistTest2 = youtubeDL.MediaFromPlaylist(testTitle2, testId2)

    # pisz tak zmienne testowe MEDIA_FROM_PLAYLIST2

    playlistMediaTest = youtubeDL.PlaylistMedia(testPlaylistName, [mediaFromPlaylistTest1,
                                                                   mediaFromPlaylistTest2])

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(ConfigParserManager(
            f'{self.testDir}/test_youtube_config.ini'))
        self.youtubeTest._savePath = self.testDir
        self.youtubeTest._ydl_opts['outtmpl'] = self.testDir + \
            '/%(title)s.%(ext)s'

    def checkResultSingleMedia(self, singleMedia, singleMediaExpected):
        self.assertEqual(singleMedia.title, singleMediaExpected.title)
        self.assertEqual(singleMedia.album, singleMediaExpected.album)
        self.assertEqual(singleMedia.artist, singleMediaExpected.artist)
        self.assertEqual(singleMedia.extension, singleMediaExpected.extension)
        self.assertEqual(singleMedia.url, singleMediaExpected.url)
        self.assertEqual(singleMedia.ytHash, singleMediaExpected.ytHash)

    def checkResulPlaylistMeida(self, playlistMedia: youtubeDL.PlaylistMedia,
                                playlistMediaExpected: youtubeDL.PlaylistMedia):
        self.assertEqual(playlistMedia.playlistName,
                         playlistMediaExpected.playlistName)
        self.assertEqual(len(playlistMedia.MediaFromPlaylistList), len(
            playlistMediaExpected.MediaFromPlaylistList))
        for idex in range(len(playlistMedia.MediaFromPlaylistList)):
            self.checkResultSingleMedia(playlistMedia.MediaFromPlaylistList[idex],
                                        playlistMediaExpected.MediaFromPlaylistList[idex])

    # bez sensu testować ale błedy sprawdzać
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
        singleMedia = resultOfYoutube.getData()
        self.checkResultSingleMedia(singleMedia, self.singleMediaTest)

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
        testVideoHash1 = self.youtubeTest._getMediaResultHash(
            self.mainURL1)
        self.assertEqual(testVideoHash1, correctVideoHash)
        testVideoHash2 = self.youtubeTest._getMediaResultHash(
            self.mainPlaylistUrlWithVideoHash1)
        self.assertEqual(testVideoHash2, correctVideoHash)
        testVideoHash3 = self.youtubeTest._getMediaResultHash(
            self.mainPlaylistUrlWithIndex1)
        self.assertEqual(testVideoHash3, correctVideoHash)
        wrong_link_with_video = self.mainPlaylistUrlNoVideoHash1
        with self.assertRaises(ValueError) as context:
            self.youtubeTest._getMediaResultHash(wrong_link_with_video)
        self.assertTrue(
            self.mainPlaylistWithoutVideoError in str(context.exception))

    def testGetPlaylistHash(self):
        correectPlaylistHash = self.mainPlaylistHash
        testVideoHash1 = self.youtubeTest._getPlaylistHash(
            self.mainPlaylistUrlNoVideoHash1)
        self.assertEqual(testVideoHash1, correectPlaylistHash)
        testVideoHash2 = self.youtubeTest._getPlaylistHash(
            self.mainPlaylistUrlWithVideoHash1)
        self.assertEqual(testVideoHash2, correectPlaylistHash)
        testVideoHash3 = self.youtubeTest._getPlaylistHash(
            self.mainPlaylistUrlWithIndex1)
        self.assertEqual(testVideoHash3, correectPlaylistHash)
        wrong_link_with_video = self.mainURL1
        with self.assertRaises(ValueError) as context:
            self.youtubeTest._getPlaylistHash(wrong_link_with_video)
        self.assertTrue('This is not a playlist' in str(context.exception))

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value=songMetaData1)
    def testDownloadVideo(self, mockDownloadFile):
        youtubeResult = self.youtubeTest.downloadVideo(self.mainURL1, "480")
        singleMedia = youtubeResult.getData()
        mockDownloadFile.assert_called_once_with(self.testId1)
        self.checkResultSingleMedia(singleMedia, self.singleMediaTest)

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
        metaData = self.youtubeTest.fastDownloadVideoPlaylist(
            self.mainPlaylistUrlNoVideoHash1, "480")
        mockExtractinfo.assert_called_once_with(self.mainPlaylistHash)
        checkResult = self.checkFastDownloadResult(metaData)
        self.assertEqual(True, checkResult)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testDownloadVideoPlaylistWithError(self, mockDownloadError):
        errorMsg = self.youtubeTest.fastDownloadVideoPlaylist(
            self.mainPlaylistUrlNoVideoHash1, "480")
        mockDownloadError.assert_called_once_with(self.mainPlaylistHash)
        self.assertFalse(errorMsg)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": testPlaylistName,
                                "entries": testEntriesList})
    @patch.object(youtubeDL.EasyID3Manager, "setMetaDataPlaylist")
    def testFastDownloadPlaylistAudio(self, mockSetMetaData, mockExtractinfo):
        metaData = self.youtubeTest.fastDownloadAudioPlaylist(
            self.mainPlaylistUrlNoVideoHash1)
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
        errorMsg = self.youtubeTest.fastDownloadAudioPlaylist(
            self.mainPlaylistUrlNoVideoHash1)
        mockDownloadError.assert_called_once_with(self.mainPlaylistHash)
        self.assertFalse(errorMsg)

    @patch.object(youtubeDL.EasyID3Manager, "setMetaDataSingleFile")
    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def testDownloadAudio(self, mockDownloadFile, mockSave):
        singleMediaInfoResult = self.youtubeTest.downloadAudio(self.mainURL1)
        singleMedia = singleMediaInfoResult.getData()
        mockDownloadFile.assert_called_once_with(self.testId1)
        mockSave.assert_called_once()
        self.checkResultSingleMedia(singleMedia, self.singleMediaTest)

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
        singleMedia = resultOfYoutube.getData()
        self.checkResultSingleMedia(singleMedia, self.singleMediaTest)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testgetSingleMediaInfoWithError(self, mockExtractInfo):
        resultOfYoutube = self.youtubeTest.requestSingleMediaInfo(
            self.mainURL1)
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
        resultOfYoutube = self.youtubeTest.requestPlaylistMediaInfo(
            self.mainPlaylistUrlNoVideoHash1)
        mockDownloadFile.assert_called_once()
        self.assertEqual(False, resultOfYoutube.isError())
        playlistMedia = resultOfYoutube.getData()
        self.checkResulPlaylistMeida(playlistMedia,
                                     self.playlistMediaTest)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testgetPlaylistMediaInfoWithError(self, mockExtractInfo):
        resultOfYoutube = self.youtubeTest.requestPlaylistMediaInfo(
            self.mainPlaylistUrlNoVideoHash1)
        mockExtractInfo.assert_called_once()
        self.assertEqual(True, resultOfYoutube.isError())
        errorMsg = resultOfYoutube.getErrorInfo()
        self.assertTrue(errorMsg, self.mainMediaDownloadError)
        self.assertFalse(resultOfYoutube.getData())

    def testGetPlaylistMediaResult(self):
        playlistMedia = self.youtubeTest._getPlaylistMedia(
            self.plalistMetaData)
        self.checkResulPlaylistMeida(playlistMedia,
                                     self.playlistMediaTest)

    def testGetSingleMediaResult(self):
        singleMedia = self.youtubeTest._getMedia(
            self.songMetaData1)
        self.checkResultSingleMedia(singleMedia, self.singleMediaTest)


if __name__ == "__main__":
    main()
