from website_youtube_dl import create_app, socketio
import os
from website_youtube_dl.common.youtubeLogKeys import YoutubeLogs, YoutubeVariables
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
from unittest import TestCase, main
from unittest.mock import patch, call
from website_youtube_dl.config import TestingConfig
from website_youtube_dl.flaskAPI import youtube
from website_youtube_dl.flaskAPI.flaskMedia import (FlaskSingleMedia,
                                                    FlaskPlaylistMedia)
from website_youtube_dl.flaskAPI.session import SessionDownloadData
from website_youtube_dl.common.youtubeDL import (YoutubeDL,
                                                 SingleMedia,
                                                 PlaylistMedia,
                                                 ResultOfYoutube)
from website_youtube_dl.flaskAPI.emits import (DownloadMediaFinishEmit,
                                               SingleMediaInfoEmit,
                                               PlaylistMediaInfoEmit)
from website_youtube_dl.common.easyID3Manager import EasyID3Manager
from website_youtube_dl.common.youtubeDataKeys import PlaylistInfo, MediaInfo
from website_youtube_dl.flaskAPI import emits
from website_youtube_dl.flaskAPI import youtubeModifyPlaylist
from test.socketClientMock import SessionClientMock


class EmitData:
    def __init__(self, emitName, data):
        self.data = data
        self.emitName = emitName

    @staticmethod
    def getEmitMassage(fullEmit, msgNumber):
        return fullEmit[msgNumber]

    @classmethod
    def initFromMassage(cls, receivedMsg):
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        return cls(emitName, data)


class testYoutubeWeb(TestCase):
    downloadMediaFinishEmit = DownloadMediaFinishEmit()
    singleMediaInfoEmit = SingleMediaInfoEmit()
    playlistMediaInfoEmit = PlaylistMediaInfoEmit()

    actualYoutubeURL1 = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    actualYoutubeURL2 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    actualYoutubePlaylistURL1 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"

    testPlaylistName = "playlistName"
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

    playlistUrlStr = "playlistUrl"
    dataStr = "data"
    testPath = "/home/test_path/"
    trackList = "trackList"
    testGeneratedHash = "Kpdwgh"
    error = "error"
    hd720p = "720"
    mp3 = "mp3"

    fileNotFoundError = f"File {testPath}  doesn't exist - something went wrong"

    sucessEmitData1 = {'title': 'Society',
                       'artist': 'Eddie Vedder',
                       'webpage_url': 'https://www.youtube.com/watch?v=ABsslEoL0-c'}

    singleMedia1 = SingleMedia(title=testTitle1,
                               album=testAlbum1,
                               artist=testArtist1,
                               ytHash=testId1,
                               url=testOriginalUrl1,
                               extension=testExt1)

    singleMedia2 = SingleMedia(title=testTitle2,
                               album=testAlbum1,
                               artist=testArtist2,
                               ytHash=testId2,
                               url=testOriginalUrl2,
                               extension=testExt2)

    expectedResultSingleMediInfo = {MediaInfo.TITLE.value:  testTitle1,
                                    MediaInfo.ARTIST.value: testArtist1,
                                    MediaInfo.URL.value: testOriginalUrl1}

    expectedResultPlaylistMediaInfo = {testPlaylistName: testPlaylistName,
                                       trackList: [{PlaylistInfo.TITLE.value: testTitle1,
                                                    PlaylistInfo.URL.value: testId1},
                                                   {PlaylistInfo.TITLE.value: testTitle2,
                                                    PlaylistInfo.URL.value: testId2}]}

    playlistMedia = PlaylistMedia(playlistName=testPlaylistName,
                                  mediaFromPlaylistList=[singleMedia1, singleMedia2])

    resultOfYoutubeSingle = ResultOfYoutube(singleMedia1)
    resultOfYoutubeSingleWithError1 = ResultOfYoutube()
    resultOfYoutubeSingleWithError1.setError(
        YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value)

    resultOfYoutubePlaylist = ResultOfYoutube(playlistMedia)
    resultOfYoutubePlaylistWithError = ResultOfYoutube()
    resultOfYoutubePlaylistWithError.setError(
        YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value)

    def setUp(self):
        app = create_app(TestingConfig)
        app.config["TESTING"] = True
        session_dict = {}
        self.socketIoTestClient = socketio.test_client(app)
        self.flask = app.test_client()
        self.app = app
        self.app.session = SessionClientMock(session_dict)

    def createFlaskSingleMedia(self, data):
        title = data["title"]
        artist = data["artist"]
        url = data["original_url"]
        return FlaskSingleMedia(title, artist, url)

    def createFlaskPlaylistMedia(self, data):
        flaskSingleMediaList = []
        for track in data["trackList"]:
            flaskSingleMediaList.append(self.createFlaskSingleMedia(track))
        return FlaskPlaylistMedia.initFromPlaylistMedia(data["playlistName"], flaskSingleMediaList)

    @patch.object(youtube, "send_file")
    @patch.object(os.path, "isfile", return_value=True)
    def testDownloadFile(self, isFileMock, sendFileMock):
        sessionData = SessionDownloadData(self.testPath)
        testKey = "testKey"
        self.app.session.addElemtoSession(testKey, sessionData)
        print(self.app.session)
        response = self.flask.get('/downloadFile/testKey')
        self.assertEqual(len(isFileMock.mock_calls), 2)
        sendFileMock.assert_called_once_with(self.testPath, as_attachment=True)
        self.assertEqual(response.status_code, 200)

    def testSessionWrongPath(self):
        with self.assertRaises(FileNotFoundError) as context:
            sessionData = SessionDownloadData(self.testPath)
            self.assertTrue(
                self.fileNotFoundError in str(context.exception))

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(youtube, "downloadCorrectData")
    def testSocketDownloadServerSuccess(self, mockDownloadData, isFile):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL1,
                YoutubeVariables.DOWNLOAD_TYP.value: self.mp3
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        self.assertEqual(len(pythonEmit), 1)
        mockDownloadData.assert_called_once()
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(self.dataStr, emitData.data)
        self.assertIn(YoutubeVariables.HASH.value,
                      emitData.data[self.dataStr])

    def testSocketDownloadServerNoDownloadType(self):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL1
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertIn(YoutubeVariables.NAME.value, receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(YoutubeVariables.ERROR.value, emitData.data)
        self.assertEqual(emitData.data[YoutubeVariables.ERROR.value],
                         YoutubeLogs.NO_FORMAT.value)

    def testSocketDownloadServerNoYoutubeURL(self):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: YoutubeVariables.EMPTY_STRING.value,
                YoutubeVariables.DOWNLOAD_TYP.value: self.mp3
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertIn(YoutubeVariables.NAME.value, receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(YoutubeVariables.ERROR.value, emitData.data)
        self.assertEqual(emitData.data[YoutubeVariables.ERROR.value],
                         YoutubeLogs.NO_URL.value)

    @patch.object(youtube, "generateHash", return_value=testGeneratedHash)
    @patch.object(SessionDownloadData, "setSessionDownloadData")
    @patch.object(youtube, "downloadCorrectData")
    def testSocketDownloadPlaylistAndVideoHash(self, mockDownloadData,
                                               mockSetSessionDownloadData,
                                               mockGenerateHash):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL2,
                YoutubeVariables.DOWNLOAD_TYP.value: self.mp3
            }
        )
        mockGenerateHash.assert_called_once()
        mockSetSessionDownloadData.assert_called_once()
        pythonEmit = self.socketIoTestClient.get_received()
        self.assertEqual(len(pythonEmit), 1)
        mockDownloadData.assert_called_once_with(self.actualYoutubeURL2,
                                                 self.mp3,
                                                 False)
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertIn(YoutubeVariables.NAME.value, receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        expectedData = self.downloadMediaFinishEmit.convertDataToMessage(
            self.testGeneratedHash)
        expectedRestult = {self.dataStr: expectedData}
        self.assertEqual(emitData.data, expectedRestult)

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(youtube, "downloadCorrectData")
    def testSocketDownloadPlaylist(self, mockDownloadData, isFile):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubePlaylistURL1,
                YoutubeVariables.DOWNLOAD_TYP.value: self.mp3
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        mockDownloadData.assert_called_once()
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(self.dataStr, emitData.data)
        self.assertIn(YoutubeVariables.HASH.value,
                      emitData.data[self.dataStr])

    @patch.object(youtube, "downloadCorrectData", return_value=None)
    def testSocketDownloadFail(self, mockDownloadData):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL1,
                YoutubeVariables.DOWNLOAD_TYP.value: self.mp3
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        self.assertEqual(len(pythonEmit), 0)
        mockDownloadData.assert_called_once()
        self.assertFalse(pythonEmit)

    @patch.object(YoutubeDL, "downloadVideo", return_value=resultOfYoutubeSingle)
    @patch.object(ConfigParserManager, "getSavePath", return_value=testPath)
    def testDownloadSingleMediaVideo(self, mockGetSavePath, mockDownloadVideo):
        with self.app.app_context():
            result = youtube.downloadSingleVideo(self.actualYoutubeURL1,
                                                 self.hd720p)
        mockGetSavePath.assert_called_once()
        mockDownloadVideo.assert_called_once_with(
            self.actualYoutubeURL1, self.hd720p)
        expected_result = os.path.join(self.testPath,
                                       f"{self.testTitle1}_720p.{self.testExt1}")
        self.assertEqual(expected_result, result)

    @patch.object(YoutubeDL, "downloadVideo", return_value=resultOfYoutubeSingleWithError1)
    def testDonwloadSingleMediaVideoWithError(self, mockDownloadVideoError):
        with self.app.app_context():
            result = youtube.downloadSingleVideo(self.actualYoutubeURL1,
                                                 self.hd720p)
        mockDownloadVideoError.assert_called_once_with(
            self.actualYoutubeURL1, self.hd720p)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsgDownloadError = pythonEmit[0]
        self.assertFalse(result)
        emitData = EmitData.initFromMassage(receivedMsgDownloadError)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertEqual(
            emitData.data, {self.error: YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value})

    @patch.object(EasyID3Manager, "saveMetaData")
    @patch.object(ConfigParserManager, "getSavePath", return_value=testPath)
    @patch.object(youtube, "sendEmitSingleMediaInfoFromYoutube", return_value=True)
    @patch.object(YoutubeDL, "downloadAudio", return_value=resultOfYoutubeSingle)
    def testDownloadSingleMediaAudio(self, mockDownloadAudio,
                                     mocksendEmitSingleMediaInfoFromYoutube,
                                     mockGetSavePath,
                                     mockSaveMetaData):
        with self.app.app_context():
            result = youtube.downloadSingleAudio(self.actualYoutubeURL1)
        mockGetSavePath.assert_called_once()
        mockDownloadAudio.assert_called_once_with(self.actualYoutubeURL1)
        mocksendEmitSingleMediaInfoFromYoutube.assert_called_once_with(
            self.actualYoutubeURL1)
        mockSaveMetaData.assert_called_once()
        expected_result = os.path.join(self.testPath,
                                       f"{self.testTitle1}.{self.mp3}")
        self.assertEqual(expected_result, result)

    @patch.object(youtube, "sendEmitSingleMediaInfoFromYoutube", return_value=False)
    def testDownloadSingleMediaAudioEmitMediaInfoError(self,
                                                       mockSendEmitSingleMediaInfoFromYoutube):
        with self.app.app_context():
            result = youtube.downloadSingleAudio(self.actualYoutubeURL1)
        self.assertIsNone(result)
        mockSendEmitSingleMediaInfoFromYoutube.assert_called_once_with(
            self.actualYoutubeURL1)

    @patch.object(YoutubeDL, "requestSingleMediaInfo", return_value=resultOfYoutubeSingle)
    @patch.object(YoutubeDL, "downloadAudio", return_value=resultOfYoutubeSingleWithError1)
    def testDownloadSingleMediaAudioWithError(self, mockDownloadAudio,
                                              mockRequestError):
        with self.app.app_context():
            result = youtube.downloadSingleAudio(self.actualYoutubeURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsgRequestSuccess = EmitData.getEmitMassage(pythonEmit, 0)
        receivedMsgDownloadError = EmitData.getEmitMassage(pythonEmit, 1)
        mockDownloadAudio.assert_called_once_with(self.actualYoutubeURL1)
        mockRequestError.assert_called_once_with(self.actualYoutubeURL1)
        self.assertFalse(result)
        emitDataSuccess = EmitData.initFromMassage(receivedMsgRequestSuccess)
        self.assertIn(self.dataStr, emitDataSuccess.data)
        self.assertEqual(self.sucessEmitData1,
                         emitDataSuccess.data[self.dataStr])
        self.assertEqual(self.singleMediaInfoEmit.emitMsg,
                         emitDataSuccess.emitName)

        emitDataError = EmitData.initFromMassage(receivedMsgDownloadError)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitDataError.emitName)
        self.assertEqual(
            emitDataError.data, {self.error: YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value})

    @patch.object(YoutubeDL, "requestSingleMediaInfo", return_value=resultOfYoutubeSingle)
    def testSendEmitSingleMediaInfoFromYoutube(self, mockRequestSingleMedia):
        with self.app.app_context():
            result = youtube.sendEmitSingleMediaInfoFromYoutube(
                self.actualYoutubeURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        mockRequestSingleMedia.assert_called_once_with(self.actualYoutubeURL1)
        self.assertEqual(emitData.data[self.dataStr],
                         self.expectedResultSingleMediInfo)
        self.assertEqual(self.singleMediaInfoEmit.emitMsg, emitData.emitName)
        self.assertTrue(result)

    @patch.object(YoutubeDL, "requestSingleMediaInfo", return_value=resultOfYoutubeSingleWithError1)
    def testSendEmitSingleMediaInfoWithError(self, mockRequestSingleMedia):
        with self.app.app_context():
            result = youtube.sendEmitSingleMediaInfoFromYoutube(
                self.actualYoutubeURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        mockRequestSingleMedia.assert_called_once_with(self.actualYoutubeURL1)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertEqual(
            emitData.data, {self.error: YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value})
        self.assertFalse(result)

    @patch.object(YoutubeDL, "requestPlaylistMediaInfo",
                  return_value=resultOfYoutubePlaylist)
    def testSendEmitPlaylistMedia(self, mockRequestSingleMedia):
        with self.app.app_context():
            result = youtube.sendEmitPlaylistMedia(
                self.actualYoutubePlaylistURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        mockRequestSingleMedia.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        self.assertEqual(emitData.data[self.dataStr],
                         self.expectedResultPlaylistMediaInfo)
        self.assertEqual(self.playlistMediaInfoEmit.emitMsg, emitData.emitName)
        self.assertTrue(result)

    @patch.object(YoutubeDL, "requestPlaylistMediaInfo", return_value=resultOfYoutubePlaylistWithError)
    def testSendEmitPlaylistMediaWithError(self, mockRequestSingleMedia):
        with self.app.app_context():
            result = youtube.sendEmitPlaylistMedia(
                self.actualYoutubePlaylistURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        mockRequestSingleMedia.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertEqual(
            emitData.data, {self.error: YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value})
        self.assertFalse(result)

    @patch.object(youtube, "zipAllFilesInList",
                  return_value=f"/home/test_path/{testPlaylistName}")
    @patch.object(youtube, "sendEmitPlaylistMedia", return_value=playlistMedia)
    @patch.object(youtube, "downloadSingleVideo", return_value="full_path_test")
    def testDownloadTracksFromPlaylistVideo(self, mockDownloadVideo,
                                            mockSendEmitPlaylist,
                                            mockZipFiles):
        with self.app.app_context():
            result = youtube.downloadTracksFromPlaylistVideo(self.actualYoutubePlaylistURL1,
                                                             self.hd720p)
        mockSendEmitPlaylist.assert_called_once()
        calls = mockDownloadVideo.mock_calls
        self.assertEqual(call(singleMediaURL=self.testId1, type='720'),
                         calls[0])
        self.assertEqual(call(singleMediaURL=self.testId2, type='720'),
                         calls[1])
        self.assertEqual(2, mockDownloadVideo.call_count)
        self.assertEqual(result, f"/home/test_path/{self.testPlaylistName}")
        mockZipFiles.assert_called_once()

    @patch.object(EasyID3Manager, "saveMetaData")
    @patch.object(ConfigParserManager, "getSavePath", return_value=testPath)
    @patch.object(YoutubeDL, "downloadAudio", return_value=resultOfYoutubeSingle)
    def testDownloadAudioFromPlaylist(self, mockDownloadAudio,
                                      mockGetSavePath,
                                      mockSaveMetaData):
        with self.app.app_context():
            result = youtube.downloadAudioFromPlaylist(self.actualYoutubeURL1,
                                                       self.testPlaylistName,
                                                       1)
        mockDownloadAudio.assert_called_once_with(self.actualYoutubeURL1)
        mockSaveMetaData.assert_called_once()
        mockGetSavePath.assert_called_once()
        self.assertEqual(result, os.path.join(
            self.testPath, f"{self.testTitle1}.mp3"))

    @patch.object(YoutubeDL, "downloadAudio", return_value=resultOfYoutubeSingleWithError1)
    def testDownloadAudioFromPlaylistWithError(self, mockDownloadAudio):
        with self.app.app_context():
            result = youtube.downloadAudioFromPlaylist(self.actualYoutubeURL1,
                                                       self.testPlaylistName,
                                                       1)
        mockDownloadAudio.assert_called_once_with(self.actualYoutubeURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsgDownloadError = EmitData.getEmitMassage(pythonEmit, 0)
        self.assertFalse(result)
        emitData = EmitData.initFromMassage(receivedMsgDownloadError)

        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertEqual(
            emitData.data, {self.error: YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value})

    @patch.object(youtube, "zipAllFilesInList",
                  return_value=f"/home/test_path/{testPlaylistName}")
    @patch.object(youtube, "sendEmitPlaylistMedia", return_value=playlistMedia)
    @patch.object(youtube, "downloadAudioFromPlaylist", return_value="full_path_test")
    def testDownloadTracksFromPlaylistAudio(self, mockDownloadAudio,
                                            mockSendEmitPlaylist,
                                            mockZipFiles):
        with self.app.app_context():
            result = youtube.downloadTracksFromPlaylistAudio(
                self.actualYoutubePlaylistURL1)
        mockSendEmitPlaylist.assert_called_once()
        calls = mockDownloadAudio.mock_calls
        self.assertEqual(call(singleMediaURL=self.testId1,
                              playlistName=self.testPlaylistName,
                              index="0"),
                         calls[0])
        self.assertEqual(call(singleMediaURL=self.testId2,
                              playlistName=self.testPlaylistName,
                              index="1"),
                         calls[1])
        self.assertEqual(2, mockDownloadAudio.call_count)
        self.assertEqual(result, f"/home/test_path/{self.testPlaylistName}")
        mockZipFiles.assert_called_once()

    @patch.object(youtube, "sendEmitPlaylistMedia",
                  return_value=None)
    def testdownloadTracksFromPlaylistVideoWithError(self,
                                                     mockRequestPlaylistMediaInfo):
        with self.app.app_context():
            result = youtube.downloadTracksFromPlaylistVideo(
                self.actualYoutubePlaylistURL1, self.hd720p)
        self.assertFalse(result)
        mockRequestPlaylistMediaInfo.assert_called_once_with(
            self.actualYoutubePlaylistURL1)

    @patch.object(youtube, "sendEmitPlaylistMedia",
                  return_value=None)
    def testdownloadTracksFromPlaylistAudioWithError(self,
                                                     mockRequestPlaylistMediaInfo):
        with self.app.app_context():
            result = youtube.downloadTracksFromPlaylistAudio(
                self.actualYoutubePlaylistURL1)
        self.assertFalse(result)
        mockRequestPlaylistMediaInfo.assert_called_once_with(
            self.actualYoutubePlaylistURL1)

    @patch.object(youtube, "downloadTracksFromPlaylistVideo",
                  return_value="video_playlist_path")
    def testDownloadCorrectDataPlaylistVideo(self, mockDownloadPlaylist):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, self.hd720p, True)
        self.assertEqual(result, "video_playlist_path")
        mockDownloadPlaylist.assert_called_once_with(
            self.actualYoutubeURL1, self.hd720p)

    @patch.object(youtube, "downloadTracksFromPlaylistAudio",
                  return_value="/home/music/audio_playlist_path")
    def testDownloadCorrectDataPlaylistAudio(self, mockDownloadPlaylist):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, "mp3", True)
        self.assertEqual(result, "/home/music/audio_playlist_path")
        mockDownloadPlaylist.assert_called_once_with(self.actualYoutubeURL1)

    @patch.object(youtube, "downloadSingleVideoWithEmit",
                  return_value="/home/music/video_single_path")
    def testDownloadCorrectDataSingleVideo(self, mockDownloadSingleMedia):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, self.hd720p, False)
        self.assertEqual(result, "/home/music/video_single_path")
        mockDownloadSingleMedia.assert_called_once_with(
            self.actualYoutubeURL1, self.hd720p)

    @patch.object(youtube, "downloadSingleAudio",
                  return_value="/home/music/audio_single_path")
    def testDownloadCorrectDataSingleAudio(self, mockDownloadSingleMedia):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, "mp3", False)
        self.assertEqual(result, "/home/music/audio_single_path")
        mockDownloadSingleMedia.assert_called_once_with(self.actualYoutubeURL1)

    def testYourubeHTML(self):
        response = self.flask.get("/youtube.html")
        self.assertIn('<title>YouTube</title>', str(response.data))
        self.assertEqual(response.status_code, 200)

    def testIndexHTML(self):
        response1 = self.flask.get("/")
        response2 = self.flask.get("/index.html")
        response3 = self.flask.get('/example')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)

    def testWrongYourubeHTML(self):
        response = self.flask.get("/youtubetest.html")
        self.assertEqual(response.status_code, 404)

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(youtubeModifyPlaylist, "generateHash",
                  return_value="test_hash")
    @patch.object(youtubeModifyPlaylist, "downloadTracksFromPlaylistAudio",
                  return_value="video_playlist_path")
    @patch.object(ConfigParserManager, "getPlaylistUrl",
                  return_value=actualYoutubePlaylistURL1)
    def testDownloadConfigPlaylist(self, mockGetPlaylistUrl,
                                   mockDownloadPlaylist,
                                   mockGenerateHash,
                                   mockIsFile):
        self.socketIoTestClient.emit(
            "downloadFromConfigFile", {
                "playlistToDownload": self.testPlaylistName
            }
        )
        mockGetPlaylistUrl.assert_called_once_with(self.testPlaylistName)
        mockDownloadPlaylist.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        mockIsFile.assert_called_once()
        mockGenerateHash.assert_called_once()
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(emitData.emitName,
                         self.downloadMediaFinishEmit.emitMsg)
        self.assertEqual(
            emitData.data[self.dataStr], self.downloadMediaFinishEmit.convertDataToMessage("test_hash"))

    @patch.object(youtubeModifyPlaylist, "downloadTracksFromPlaylistAudio",
                  return_value=None)
    @patch.object(ConfigParserManager, "getPlaylistUrl",
                  return_value=actualYoutubePlaylistURL1)
    def testDownloadConfigPlaylistWithError(self, mockGetPlaylistUrl,
                                            mockDownloadPlaylist):
        self.socketIoTestClient.emit(
            "downloadFromConfigFile", {
                "playlistToDownload": self.testPlaylistName
            }
        )
        mockGetPlaylistUrl.assert_called_once_with(self.testPlaylistName)
        mockDownloadPlaylist.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        self.assertEqual(len(pythonEmit), 0)

    @patch.object(ConfigParserManager, "getPlaylists", return_value={"test_playlist": "url1",
                                                                     testPlaylistName: "url2"})
    @patch.object(ConfigParserManager, "addPlaylist")
    def testAddPlaylistConfig(self, mockAddPlaylist, mockGetplaylists):
        self.socketIoTestClient.emit(
            "addPlaylist", {
                "playlistName": self.testPlaylistName,
                "playlistURL": self.actualYoutubePlaylistURL1
            }
        )
        mockAddPlaylist.assert_called_once_with(
            self.testPlaylistName, self.actualYoutubePlaylistURL1)
        mockGetplaylists.assert_called_once()
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(emitData.emitName, "uploadPlaylists")
        self.assertEqual(
            emitData.data, {self.dataStr: {'plalistList': ["test_playlist", self.testPlaylistName]}})

    @patch.object(ConfigParserManager, "getPlaylists", return_value={"test_playlist": "url1",
                                                                     testPlaylistName: "url2"})
    @patch.object(ConfigParserManager, "deletePlaylist")
    def testDeletePlaylistConfig(self, playlistToDelete, mockGetplaylists):
        self.socketIoTestClient.emit(
            "deletePlaylist", {
                "playlistToDelete": self.testPlaylistName,
            }
        )
        playlistToDelete.assert_called_once_with(self.testPlaylistName)
        mockGetplaylists.assert_called_once()
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(emitData.emitName, "uploadPlaylists")
        self.assertEqual(
            emitData.data, {self.dataStr: {'plalistList': ["test_playlist", self.testPlaylistName]}})

    @patch.object(ConfigParserManager, "getPlaylistUrl", return_value=testPlaylistName)
    def testPlaylistConfigUrl(self, mockGetPlaylistUrl):
        self.socketIoTestClient.emit(
            "playlistName", {
                "playlistName": self.testPlaylistName,
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        mockGetPlaylistUrl.assert_called_once()
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(self.playlistUrlStr, emitData.emitName)
        self.assertEqual(
            emitData.data, {self.dataStr: {self.playlistUrlStr:  self.testPlaylistName}})

    def testModifyPlaylistHTML(self):
        response = self.flask.get("/modify_playlist.html")
        self.assertEqual(response.status_code, 200)

    # def testDownloadFileHTML(self):
    #     response = self.flask.get("/downloadFile/test", )
    #     self.assertEqual(response.status_code, 200)


class TestEmits(TestCase):
    playlistName = "playlistName"
    trackList = "trackList"
    title = "title"
    url = "url"
    artist = "artist"

    playlistMediaTest = FlaskPlaylistMedia.initFromPlaylistMedia(testYoutubeWeb.testPlaylistName,
                                                                 [testYoutubeWeb.singleMedia1,
                                                                  testYoutubeWeb.singleMedia2])

    singleMedia = FlaskSingleMedia(testYoutubeWeb.testTitle1,
                                   testYoutubeWeb.testArtist1,
                                   testYoutubeWeb.testOriginalUrl1)

    def setUp(self):
        self.playlistMediaInfoEmits = emits.PlaylistMediaInfoEmit()
        self.singleMediaInfoEmits = emits.SingleMediaInfoEmit()

    def testConvertDataToMassagePlaylist(self):
        result = self.playlistMediaInfoEmits.convertDataToMessage(
            self.playlistMediaTest)
        self.assertEqual(
            result, testYoutubeWeb.expectedResultPlaylistMediaInfo)

    def testConvertDataToMassageSingle(self):
        result = self.singleMediaInfoEmits.convertDataToMessage(
            testYoutubeWeb.singleMedia1)
        self.assertEqual(result, testYoutubeWeb.expectedResultSingleMediInfo)


if __name__ == "__main__":
    main()
