from  website_youtube_dl import create_app
import os
from website_youtube_dl.common.youtubeLogKeys import YoutubeLogs, YoutubeVariables
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
from unittest import TestCase, main
from unittest.mock import patch, call
from website_youtube_dl.config import TestingConfig
from website_youtube_dl.flaskAPI import youtube
from website_youtube_dl.flaskAPI.youtube import (FlaskSingleMedia,
                                                 FlaskPlaylistMedia,
                                                 socketio)
from website_youtube_dl.common.youtubeDL import (YoutubeDL,
                                                SingleMedia,
                                                PlaylistMedia,
                                                MediaFromPlaylist,
                                                ResultOfYoutube)
from website_youtube_dl.common.emits import (DownloadMediaFinishEmit,
                                             SingleMediaInfoEmit,
                                             PlaylistMediaInfoEmit)

class testYoutubeWeb(TestCase):
    downloadMediaFinishEmit = DownloadMediaFinishEmit()
    singleMediaInfoEmit = SingleMediaInfoEmit()
    playlistMediaInfoEmit = PlaylistMediaInfoEmit()

    actualYoutubeURL1 = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    actualYoutubeURL2 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    actualYoutubePlaylistURL1 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"

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
        self.socketIoTestClient = socketio.test_client(app)
        self.flask = app.test_client()

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

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(youtube, "downloadCorrectData")
    def testSocketDownloadServerSuccess(self, mockDownloadData, isFile):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
            YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL1,
            YoutubeVariables.DOWNLOAD_TYP.value: YoutubeVariables.MP3.value
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        print(pythonEmit)
        receivedMsg = pythonEmit[0]
        self.assertEqual(len(pythonEmit), 1)
        mockDownloadData.assert_called_once()
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertIn(YoutubeVariables.DATA.value, data)
        self.assertIn(YoutubeVariables.HASH.value,
                      data[YoutubeVariables.DATA.value])

    def testSocketDownloadServerNoDownloadType(self):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL1
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        print(pythonEmit)
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertIn(YoutubeVariables.NAME.value, receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertIn(YoutubeVariables.ERROR.value, data)
        self.assertEqual(data[YoutubeVariables.ERROR.value],
                         YoutubeLogs.NO_FORMAT.value)

    def testSocketDownloadServerNoYoutubeURL(self):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: YoutubeVariables.EMPTY_STRING.value,
                YoutubeVariables.DOWNLOAD_TYP.value: YoutubeVariables.MP3.value
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        print(pythonEmit)
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertIn(YoutubeVariables.NAME.value, receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertIn(YoutubeVariables.ERROR.value, data)
        self.assertEqual(data[YoutubeVariables.ERROR.value],
                         YoutubeLogs.NO_URL.value)

    def testSocketDownloadPlaylistAndVideoHash(self):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL2,
                YoutubeVariables.DOWNLOAD_TYP.value: YoutubeVariables.MP3.value
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        print(pythonEmit)
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertIn(YoutubeVariables.NAME.value, receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertIn(YoutubeVariables.ERROR.value, data)
        self.assertEqual(data[YoutubeVariables.ERROR.value],
                         YoutubeLogs.PLAYLIST_AND_VIDEO_HASH_IN_URL.value)

    @patch.object(youtube, "downloadCorrectData")
    def testSocketDownloadPlaylist(self, mockDownloadData):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubePlaylistURL1,
                YoutubeVariables.DOWNLOAD_TYP.value: YoutubeVariables.MP3.value
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = pythonEmit[0]
        mockDownloadData.assert_called_once()
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertIn(YoutubeVariables.DATA.value, data)
        self.assertIn(YoutubeVariables.HASH.value,
                      data[YoutubeVariables.DATA.value])

    @patch.object(youtube, "downloadCorrectData", return_value=None)
    def testSocketDownloadFail(self, mockDownloadData):
        self.socketIoTestClient.emit(
            YoutubeVariables.FORM_DATA.value, {
                YoutubeVariables.YOUTUBE_URL.value: self.actualYoutubeURL1,
                YoutubeVariables.DOWNLOAD_TYP.value: YoutubeVariables.MP3.value
            }
        )
        pythonEmit = self.socketIoTestClient.get_received()
        print(pythonEmit)
        self.assertEqual(len(pythonEmit), 0)
        mockDownloadData.assert_called_once()
        self.assertFalse(pythonEmit)

    @patch.object(youtube, "downloadSingleMedia", return_value="path_test")
    @patch.object(YoutubeDL, "requestSingleMediaInfo", return_value=resultOfYoutubeSingle)
    def testDownloadSingleInfoAndMedia(self, mockGetSigleMedia,
                                       mockDownloadSingleMedia):
        result = youtube.downloadSingleInfoAndMedia(self.testOriginalUrl1)
        self.assertEqual("path_test", result)
        mockGetSigleMedia.assert_called_once()
        mockDownloadSingleMedia.assert_called_once_with(self.singleMedia1.url,
                                                        self.singleMedia1.title,
                                                        False)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0][YoutubeVariables.DATA.value]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        flaskSingleMedia = self.createFlaskSingleMedia(data)
        self.assertEqual(data, self.singleMediaInfoEmit.convertDataToMessage(
            flaskSingleMedia))
        # zrobić funkcje która sprawdza wszytko po kolei, taka sama logia jak w yt
        self.assertEqual(self.singleMediaInfoEmit.emit_msg,
                         emitName)

    @patch.object(YoutubeDL, "requestSingleMediaInfo",
                  return_value=resultOfYoutubeSingleWithError1)
    def testDownloadSingleInfoAndMediaWithError(self, mockGetSigleMedia):
        result = youtube.downloadSingleInfoAndMedia(self.testOriginalUrl1)
        self.assertFalse(result)
        mockGetSigleMedia.assert_called_once()
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = pythonEmit[0]
        error = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertEqual(
            error, {"error": YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value})

    @patch.object(YoutubeDL, "downloadVideo", return_value=resultOfYoutubeSingle)
    @patch.object(ConfigParserManager, "getSavePath", return_value="/home/test_path/")
    def testDownloadSingleMediaVideo(self, mockGetSavePath, mockDownloadVideo):
        result = youtube.downloadSingleMedia(self.actualYoutubeURL1,
                                             self.testTitle1,
                                             "720")
        mockGetSavePath.assert_called_once()
        mockDownloadVideo.assert_called_once_with(
            self.actualYoutubeURL1, "720")
        expected_result = os.path.join("/home/test_path/",
                                    f"{self.testTitle1}_720p.{self.testExt1}")
        self.assertEqual(expected_result, result)

    @patch.object(YoutubeDL, "downloadAudio", return_value=resultOfYoutubeSingle)
    @patch.object(ConfigParserManager, "getSavePath", return_value="/home/test_path/")
    def testDownloadSingleMediaAudio(self, mockGetSavePath, mockDownloadAudio):
        result = youtube.downloadSingleMedia(self.actualYoutubeURL1,
                                             self.testTitle1,
                                             False)
        mockGetSavePath.assert_called_once()
        mockDownloadAudio.assert_called_once_with(self.actualYoutubeURL1)
        expected_result = os.path.join("/home/test_path/",
                                    f"{self.testTitle1}.{YoutubeVariables.MP3.value}")
        self.assertEqual(expected_result, result)

    @patch.object(YoutubeDL, "downloadAudio", return_value=resultOfYoutubeSingleWithError1)
    @patch.object(ConfigParserManager, "getSavePath", return_value="/home/test_path/")
    def testDownloadSingleMediaAudioWithError(self, mockGetSavePath, mockDownloadAudio):
        result = youtube.downloadSingleMedia(self.actualYoutubeURL1,
                                             self.testTitle1,
                                             False)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = pythonEmit[0]
        mockGetSavePath.assert_called_once()
        mockDownloadAudio.assert_called_once_with(self.actualYoutubeURL1)
        self.assertFalse(result)
        error = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertEqual(
            error, {"error": YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value})

    @patch.object(youtube, "downloadSingleMedia", return_value="full_path_test")
    def testDownloadAllPlaylistTracks(self, mockDownloadSingleMedia):
        result = youtube.downloadAllPlaylistTracks([self.singleMedia1,
                                                    self.singleMedia1,
                                                    self.singleMedia1], "720")
        for mockCall in mockDownloadSingleMedia.mock_calls:
            self.assertEqual(call(self.testOriginalUrl1, self.testTitle1, '720'),
                             mockCall)
        self.assertEqual(3, mockDownloadSingleMedia.call_count)
        self.assertEqual(result, ["full_path_test",
                                  "full_path_test",
                                  "full_path_test"])

    @patch.object(youtube, "zipAllFilesInList",
                  return_value=f"/home/test_path/{testPlaylistName}")
    @patch.object(youtube, "downloadAllPlaylistTracks", return_value=["full_path_test1",
                                                                      "full_path_test2"])
    @patch.object(ConfigParserManager, "getSavePath", return_value="/home/test_path/")
    @patch.object(YoutubeDL, "requestPlaylistMediaInfo",
                  return_value=resultOfYoutubePlaylist)
    def testDonwnloadPlaylist(self, mockRequestPlaylistMediaInfo,
                              mockGetSavePath,
                              mockDownloadAllTracks,
                              mockZipFiles):
        result = youtube.downloadPlaylist(
            self.actualYoutubePlaylistURL1, "720")
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0][YoutubeVariables.DATA.value]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        mockRequestPlaylistMediaInfo.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        mockDownloadAllTracks.assert_called_once_with(self.playlistMedia.MediaFromPlaylistList,
                                                      "720")
        mockGetSavePath.assert_called_once()
        mockZipFiles.assert_called_once_with("/home/test_path/",
                                             self.playlistMedia.playlistName,
                                             ["full_path_test1",
                                              "full_path_test2"])
        self.assertEqual(result,
                         os.path.join("/home/test_path/", self.playlistMedia.playlistName))
        flaskPlaylistMedia = self.createFlaskPlaylistMedia(data)
        self.assertEqual(data, self.playlistMediaInfoEmit.convertDataToMessage(
            flaskPlaylistMedia))
        self.assertEqual(self.playlistMediaInfoEmit.emit_msg,
                         emitName)

    @patch.object(YoutubeDL, "requestPlaylistMediaInfo",
                  return_value=resultOfYoutubePlaylistWithError)
    def testDonwnloadPlaylistWithError(self, mockRequestPlaylistMediaInfo):
        result = youtube.downloadPlaylist(
            self.actualYoutubePlaylistURL1, "720")
        self.assertFalse(result)
        mockRequestPlaylistMediaInfo.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = pythonEmit[0]
        error = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(self.downloadMediaFinishEmit.emit_msg,
                         emitName)
        self.assertEqual(
            error, {"error": YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value})

    @patch.object(youtube, "downloadPlaylist", return_value="video_playlist_path")
    def testDownloadCorrectDataPlaylistVideo(self, mockDownloadPlaylist):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, "720", True)
        self.assertEqual(result, "video_playlist_path")
        mockDownloadPlaylist.assert_called_once_with(
            self.actualYoutubeURL1, "720")

    @patch.object(youtube, "downloadPlaylist", return_value="/home/music/audio_playlist_path")
    def testDownloadCorrectDataPlaylistAudio(self, mockDownloadPlaylist):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, "mp3", True)
        self.assertEqual(result, "/home/music/audio_playlist_path")
        mockDownloadPlaylist.assert_called_once_with(self.actualYoutubeURL1)

    @patch.object(youtube, "downloadSingleInfoAndMedia", return_value="/home/music/video_single_path")
    def testDownloadCorrectDataSingleVideo(self, mockDownloadSingleMedia):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, "720", False)
        self.assertEqual(result, "/home/music/video_single_path")
        mockDownloadSingleMedia.assert_called_once_with(
            self.actualYoutubeURL1, "720")

    @patch.object(youtube, "downloadSingleInfoAndMedia", return_value="/home/music/audio_single_path")
    def testDownloadCorrectDataSingleAudio(self, mockDownloadSingleMedia):
        result = youtube.downloadCorrectData(
            self.actualYoutubeURL1, "mp3", False)
        self.assertEqual(result, "/home/music/audio_single_path")
        mockDownloadSingleMedia.assert_called_once_with(self.actualYoutubeURL1)

    def testYourubeHTML(self):
        response = self.flask.get("/youtube.html")
        self.assertIn('<title>YouTube</title>', str(response.data))
        self.assertEqual(response.status_code, 200)

    def testWrongYourubeHTML(self):
        response = self.flask.get("/youtubetest.html")
        self.assertEqual(response.status_code, 404)

    @patch.object(youtube, "generateHash", return_value="test_hash")
    @patch.object(youtube, "downloadPlaylist", return_value="video_playlist_path")
    @patch.object(ConfigParserManager, "getPlaylistUrl", return_value=actualYoutubePlaylistURL1)
    def testDownloadConfigPlaylist(self, mockGetPlaylistUrl, mockDownloadPlaylist, mockGenerateHash):
        self.socketIoTestClient.emit(
            "downloadFromConfigFile", {
                "playlistToDownload": self.testPlaylistName
            }
        )
        mockGetPlaylistUrl.assert_called_once_with(self.testPlaylistName)
        mockDownloadPlaylist.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0][YoutubeVariables.DATA.value]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(emitName, self.downloadMediaFinishEmit.emit_msg)
        self.assertEqual(
            data, self.downloadMediaFinishEmit.convertDataToMessage("test_hash"))

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
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(emitName, "uploadPlalists")
        self.assertEqual(
            data, {'data': {'plalistList': ["test_playlist", self.testPlaylistName]}})

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
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(emitName, "uploadPlalists")
        self.assertEqual(
            data, {'data': {'plalistList': ["test_playlist", self.testPlaylistName]}})

    def testModifyPlaylistHTML(self):
        response = self.flask.get("/modify_playlist.html")
        self.assertEqual(response.status_code, 200)

    # def testDownloadFileHTML(self):
    #     response = self.flask.get("/downloadFile/test", )
    #     self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    main()
