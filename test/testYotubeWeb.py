import flask
from os import path
from common.youtubeLogKeys import YoutubeLogs, YoutubeVariables
from yt_dlp import utils
from common.youtubeConfigManager import ConfigParserManager
from common.youtubeDL import YoutubeDL, SingleMedia, PlaylistMedia, ResultOfYoutube
from common.emits import DownloadMediaFinishEmit, SingleMediaInfoEmit, PlaylistMediaInfoEmit
from unittest import TestCase, main
from unittest.mock import patch, call
from mainWebPage import socketio, app
from flaskAPI import youtube


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
                                  singleMediaList=[singleMedia1, singleMedia2])

    resultOfYoutubeSingle = ResultOfYoutube(singleMedia1)
    resultOfYoutubeSingleWithError1 = ResultOfYoutube()
    resultOfYoutubeSingleWithError1.setError(
        YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value)

    resultOfYoutubePlaylist = ResultOfYoutube(playlistMedia)
    resultOfYoutubeSingleWithError2 = ResultOfYoutube()
    resultOfYoutubeSingleWithError2.setError(
        YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value)

    def setUp(self):
        app.config["TESTING"] = True
        self.socketIoTestClient = socketio.test_client(app)

    @patch.object(youtube, "downloadCorrectData")
    def testSocketDownloadServerSuccess(self, mockDownloadData):
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
    @patch.object(YoutubeDL, "getSingleMediaInfo", return_value=resultOfYoutubeSingle)
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
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        self.assertEqual(data, self.singleMediaInfoEmit.convertDataToMessage(
            self.singleMedia1))
        print(emitName)
        self.assertEqual(self.singleMediaInfoEmit.emit_msg,
                         emitName)

    @patch.object(YoutubeDL, "getSingleMediaInfo",
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
        expected_result = path.join("/home/test_path/",
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
        expected_result = path.join("/home/test_path/",
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
    @patch.object(YoutubeDL, "getPlaylistMediaInfo",
                  return_value=resultOfYoutubePlaylist)
    def testDonwnloadPlaylist(self, mockGetPlaylistMedia,
                              mockGetSavePath,
                              mockDownloadAllTracks,
                              mockZipFiles):
        result = youtube.downloadPlaylist(self.actualYoutubePlaylistURL1, "720")
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = pythonEmit[0]
        data = receivedMsg[YoutubeVariables.ARGS.value][0]
        emitName = receivedMsg[YoutubeVariables.NAME.value]
        mockGetPlaylistMedia.assert_called_once_with(
            self.actualYoutubePlaylistURL1)
        mockDownloadAllTracks.assert_called_once_with(self.playlistMedia.singleMediaList,
                                                      "720")
        mockGetSavePath.assert_called_once()
        mockZipFiles.assert_called_once_with("/home/test_path/",
                                             self.playlistMedia.playlistName,
                                             ["full_path_test1",
                                              "full_path_test2"])
        self.assertEqual(result,
                         path.join("/home/test_path/", self.playlistMedia.playlistName))
        self.assertEqual(data, self.playlistMediaInfoEmit.convertDataToMessage(
            self.playlistMedia))
        print(emitName)
        self.assertEqual(self.playlistMediaInfoEmit.emit_msg,
                         emitName)
        print(data)
        print(emitName)


#     @patch.object(YoutubeDL, "downloadVideo", return_value={"ext": "mp4", "title": "testTitle"})
#     def testVideoDownoladToServer(self, mockDownload):
#         response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL.com",
#                                                               "qualType": "720"})
#         self.assertEqual(response.status_code, 200)
#         mockDownload.assert_called_once_with("testYoutubeURL.com", "720")
#         self.assertIn("Downloaded video file", str(response.data))
#         self.assertIn('value="testTitle_720p.mp4"', str(response.data))

#     @patch.object(YoutubeDL, "downloadAudio", return_value={"ext": "mp3", "title": "testTitle"})
#     def testAudioDownoladToServer(self, mockDownload):
#         response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL.com",
#                                                               "qualType": "mp3"})
#         self.assertEqual(response.status_code, 200)
#         mockDownload.assert_called_once_with("testYoutubeURL.com")
#         self.assertIn("Downloaded audio file", str(response.data))
#         self.assertIn('value="testTitle.mp3"', str(response.data))

#     def testDownoladToServerNoType(self):
#         response = self.flask.post(
#             "/downloadToServer", data={"youtubeURL": "testYoutubeURL.com"})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("Please enter type", str(response.data))

#     def testDownoladToServerEmptyURL(self):
#         response = self.flask.post("/downloadToServer", data={"youtubeURL": "",
#                                    "qualType": "720"})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("Please enter YouTube URL", str(response.data))

#     @patch.object(YoutubeDL, "downloadVideo", return_value={"ext": "mp4", "title": "testTitle"})
#     def testDownoladToServerPlaylistURLwithVideo(self, mockDownload):
#         response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?v=testVideo?list=playlist.com",
#                                    "qualType": "720"})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(
#             "You entered URL with playlist hash - only single video has been downloaded", str(response.data))
#         mockDownload.assert_called_once_with(
#             "testYoutubeURL?v=testVideo?list=playlist.com", "720")
#         self.assertIn("Downloaded video file", str(response.data))
#         self.assertIn('value="testTitle_720p.mp4"', str(response.data))

#     @patch.object(YoutubeDL, "downloadVideo", return_value="error")
#     def testDownoladToServerPlaylistURLNoVideo(self, mockDownload):
#         response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?list=playlist.com",
#                                    "qualType": "720"})
#         self.assertEqual(response.status_code, 200)
#         mockDownload.assert_called_once_with(
#             "testYoutubeURL?list=playlist.com", "720")
#         self.assertIn("File not found - wrong link", str(response.data))
#         self.assertIn('<title>YouTube</title>', str(response.data))

#     @patch.object(YoutubeDL, "downloadAudio", return_value={"ext": "mp3", "title": "testTitle"})
#     def testDownoladToServerPlaylistURLwithAudio(self, mockDownload):
#         response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?v=testVideo?list=playlist.com",
#                                    "qualType": "mp3"})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(
#             "You entered URL with playlist hash - only single video has been downloaded", str(response.data))
#         mockDownload.assert_called_once_with(
#             "testYoutubeURL?v=testVideo?list=playlist.com")
#         self.assertIn("Downloaded audio file", str(response.data))
#         self.assertIn('value="testTitle.mp3"', str(response.data))

#     @patch.object(YoutubeDL, "downloadAudio", return_value="error")
#     def testDownoladToServerPlaylistURLNoAudio(self, mockDownload):
#         response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?list=playlist.com",
#                                    "qualType": "mp3"})
#         self.assertEqual(response.status_code, 200)
#         mockDownload.assert_called_once_with(
#             "testYoutubeURL?list=playlist.com")
#         self.assertIn("File not found - wrong link", str(response.data))
#         self.assertIn('<title>YouTube</title>', str(response.data))

#     def testYourubeHTML(self):
#         response = self.flask.get("/youtube.html")
#         self.assertIn('<title>YouTube</title>', str(response.data))
#         self.assertEqual(response.status_code, 200)

#     def testWrongYourubeHTML(self):
#         response = self.flask.get("/youtubetest.html")
#         self.assertEqual(response.status_code, 404)

#     @patch.object(ConfigParserManager, "getPlaylists", return_value={"testPlaylistName": "testplaylistURL.com"})
#     def testModifyPlaylistHtml(self, mockGetPlaylsits):
#         response = self.flask.get("/modify_playlist.html")
#         self.assertEqual(response.status_code, 200)
#         mockGetPlaylsits.assert_called_once()
#         self.assertIn('<option value=testPlaylistName>', str(response.data))
#         self.assertIn('<title>Modify Playlist</title>', str(response.data))

#     @patch.object(YoutubeDL, "downoladAllConfigPlaylistsVideo")
#     def testdownoladAllConfigPlaylistsVideo(self, mockDownload):
#         response = self.flask.get("/downloadConfigPlaylist")
#         self.assertEqual(response.status_code, 200)
#         mockDownload.assert_called_once_with(type=720)
#         self.assertIn("All config playlist has been downloaded",
#                       str(response.data))
#         self.assertIn('<title>YouTube</title>', str(response.data))

#     @patch.object(flask, "send_file")
#     @patch.object(utils, "sanitize_filename", return_value="testFileName")
#     def testDownoladFile(self, mockSanitizeFilename, mockSendFile):
#         response = self.flask.post(
#             "/downloadFile", data={"directoryPath": "test/path", "fileName": "testFileName"})
#         self.assertEqual(response.status_code, 200)
#         mockSanitizeFilename.assert_called_once_with("testFileName")
#         mockSendFile.assert_called_once_with(
#             "test/path/testFileName", as_attachment=True)

#     @patch.object(ConfigParserManager, "getPlaylists")
#     def testAddPlaylistNoURL(self, mockGetPlaylists):
#         response = self.flask.post("/modify_playlist", data={"playlistURL": "testYoutubeURL.com",
#                                                              "playlistName": "testPlaylistName",
#                                                              "AddPlaylistButton": ""})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(
#             "Please enter correct URL of YouTube playlist", str(response.data))
#         self.assertIn("<title>Modify Playlist</title>", str(response.data))
#         mockGetPlaylists.assert_called_once()

#     @patch.object(ConfigParserManager, "addPlaylist")
#     @patch.object(ConfigParserManager, "getPlaylists")
#     def testAddPlaylistCorrectURL(self, mockGetPlaylists, mockAddPlaylist):
#         response = self.flask.post("/modify_playlist", data={"playlistURL": "testYoutubeURL?list=playlisHash.com",
#                                                              "playlistName": "testPlaylistName",
#                                                              "AddPlaylistButton": ""})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(mockGetPlaylists.call_count, 2)
#         self.assertIn(
#             "Playlist testPlaylistName added to config file", str(response.data))
#         self.assertIn("<title>Modify Playlist</title>", str(response.data))
#         mockAddPlaylist.assert_called_once()

#     @patch.object(ConfigParserManager, "getPlaylists")
#     def testDeletePlaylistNoName(self, mockGetPlaylists):
#         response = self.flask.post(
#             "/modify_playlist", data={"DeletePlaylistButton": ""})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("Select a playlist to delete", str(response.data))
#         self.assertIn("<title>Modify Playlist</title>", str(response.data))
#         mockGetPlaylists.assert_called_once()

#     @patch.object(ConfigParserManager, "deletePlaylist")
#     @patch.object(ConfigParserManager, "getPlaylists")
#     def testDeletePlaylistWithName(self, mockGetPlaylists, mockDeletePlaylist):
#         response = self.flask.post("/modify_playlist", data={"playlistSelect": "playlistToDelete",
#                                                              "DeletePlaylistButton": ""})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(
#             "Playlist playlistToDelete deleted from config file", str(response.data))
#         self.assertIn("<title>Modify Playlist</title>", str(response.data))
#         self.assertEqual(mockGetPlaylists.call_count, 2)
#         mockDeletePlaylist.assert_called_once()

#     def testModifyPlaylist(self):
#         with self.assertRaises(Exception) as fail:
#             response = self.flask.post(
#                 "/modify_playlist", data={"playlistSelect": "playlistToDelete"})
#             self.assertEqual(response.status_code, 200)
#             self.assertIn("<title>Modify Playlist</title>", str(response.data))
#         self.assertIn('Undefined behaviour', str(fail.exception))


if __name__ == "__main__":
    main()
