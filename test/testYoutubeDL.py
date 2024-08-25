import os
import yt_dlp
import mutagen.easyid3
import mutagen.mp3
from unittest import TestCase, main
from unittest.mock import patch, call, MagicMock
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
from website_youtube_dl.common.youtubeDataKeys import PlaylistInfo, MediaInfo
from website_youtube_dl.common.youtubeLogKeys import YoutubeVariables
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
        MediaInfo.TITLE.value: testTitle1,
        MediaInfo.ALBUM.value: testAlbum1,
        MediaInfo.ARTIST.value: testArtist1,
        MediaInfo.EXTENSION.value: testExt1,
        PlaylistInfo.PLAYLIST_INDEX.value: testPlaylistIndex1,
        MediaInfo.URL.value: testOriginalUrl1,
        MediaInfo.YOUTUBE_HASH.value: testId1
    }

    songMetaData2 = {
        MediaInfo.TITLE.value: testTitle2,
        MediaInfo.ARTIST.value: testArtist2,
        MediaInfo.ALBUM.value: testAlbum1,
        MediaInfo.EXTENSION.value: testExt2,
        PlaylistInfo.PLAYLIST_INDEX.value: testPlaylistIndex2,
        MediaInfo.URL.value: testOriginalUrl2,
        MediaInfo.YOUTUBE_HASH.value: testId2
    }

    songFromPlaylist1 = {
        PlaylistInfo.TITLE.value: testTitle1,
        PlaylistInfo.URL.value: testId1,
    }

    songFromPlaylist2 = {
        PlaylistInfo.TITLE.value: testTitle2,
        PlaylistInfo.URL.value: testId2,
    }

    testEntriesList = [songFromPlaylist1, songFromPlaylist2, None]
    testPlaylsitUrlsList = [
        mainPlaylistUrlNoVideoHash1, mainPlaylistUrlNoVideoHash2]

    plalistMetaData = {
        PlaylistInfo.TITLE.value: testPlaylistName,
        PlaylistInfo.PLAYLIST_TRACKS.value: testEntriesList
    }

    singleMediaTest = youtubeDL.SingleMedia(testTitle1, testAlbum1,
                                            testArtist1, testId1,
                                            testOriginalUrl1, testExt1)

    mediaFromPlaylistTest1 = youtubeDL.MediaFromPlaylist(testTitle1, testId1)

    mediaFromPlaylistTest2 = youtubeDL.MediaFromPlaylist(testTitle2, testId2)

    # pisz tak zmienne testowe MEDIA_FROM_PLAYLIST2

    playlistMediaTest = youtubeDL.PlaylistMedia(testPlaylistName, [mediaFromPlaylistTest1,
                                                                   mediaFromPlaylistTest2])

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(ConfigParserManager(
            f'{self.testDir}/test_youtube_config.ini'))
        self.youtubeConfigPlaylists = youtubeDL.YoutubeDlConfig(ConfigParserManager(
            f'{self.testDir}/test_youtube_config.ini'),
            MagicMock())
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

    def checkMediaFromPlaylist(self, mediaFromPlaylist, mediaFromPlaylistExpected):
        self.assertEqual(mediaFromPlaylist.title,
                         mediaFromPlaylistExpected.title)
        self.assertEqual(mediaFromPlaylist.ytHash,
                         mediaFromPlaylistExpected.ytHash)

    def checkResulPlaylistMeida(self, playlistMedia: youtubeDL.PlaylistMedia,
                                playlistMediaExpected: youtubeDL.PlaylistMedia):
        self.assertEqual(playlistMedia.playlistName,
                         playlistMediaExpected.playlistName)
        self.assertEqual(len(playlistMedia.mediaFromPlaylistList), len(
            playlistMediaExpected.mediaFromPlaylistList))
        for idex in range(len(playlistMedia.mediaFromPlaylistList)):
            self.checkMediaFromPlaylist(playlistMedia.mediaFromPlaylistList[idex],
                                        playlistMediaExpected.mediaFromPlaylistList[idex])

    # bez sensu testować ale błedy sprawdzać
    def checkFastDownloadResult(self, metaData):
        resultTest = {'title': 'testPlaylist', 'entries': [
            self.songFromPlaylist1, self.songFromPlaylist2, None]}
        print("RESULT_TEST", resultTest)
        if metaData != resultTest:
            return False
        else:
            return True

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def testDownloadFile(self, mockExtractinfo):
        resultOfYoutube = self.youtubeTest._downloadFile(self.mainURL1)
        print(self.songMetaData1)
        print(dir(resultOfYoutube.getData()))
        print(resultOfYoutube.getData().url)

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
        print(metaData)
        checkResult = self.checkFastDownloadResult(metaData)
        self.assertEqual(True, checkResult)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(mainMediaDownloadError))
    def testDownloadVideoPlaylistWithError(self, mockDownloadError):
        errorMsg = self.youtubeTest.fastDownloadVideoPlaylist(
            self.mainPlaylistUrlNoVideoHash1, "480")
        mockDownloadError.assert_called_once_with(self.mainPlaylistHash)
        self.assertFalse(errorMsg)

# importować easyID3Manager to już imporotwać zmocowanaą wersję

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": testPlaylistName,
                                "entries": testEntriesList})
    def testFastDownloadPlaylistAudio(self, mockExtractinfo):
        print(os.path.join(self.testDir, self.testTitle1))
        metaData = self.youtubeTest.fastDownloadAudioPlaylist(
            self.mainPlaylistUrlNoVideoHash1)
        print(self.testDir)
        mockExtractinfo.assert_called_once_with(self.mainPlaylistHash)
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

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def testDownloadAudio(self, mockSave):
        singleMediaInfoResult = self.youtubeTest.downloadAudio(self.mainURL1)
        singleMedia = singleMediaInfoResult.getData()
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
    def testGetPlaylistMediaInfo(self, mockDownloadFile):
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
