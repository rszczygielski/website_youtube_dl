from yt_dlp import utils
import flask
from common.youtubeConfigManager import ConfigParserManager
from common.youtubeDL import YoutubeDL
from unittest import TestCase, main
from unittest.mock import patch
from mainWebPage import socketio, app

class testYoutubeWeb(TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.socketIoTestClient = socketio.test_client(app)

    def testSocketDownloadServerNoDownloadType(self):
        self.socketIoTestClient.emit("FormData", {"youtubeURL": "ttest/url.com"})
        pythonEmit = self.socketIoTestClient.get_received()
        print(pythonEmit)
        self.assertEqual(len(pythonEmit), 1)
        receivedMsg = pythonEmit[0]
        self.assertIn('name', receivedMsg)
        self.assertEqual("downloadError", receivedMsg["name"])

    @patch.object(YoutubeDL, "downloadVideo", return_value={"ext": "mp4", "title": "testTitle"})
    def testVideoDownoladToServer(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL.com",
                                    "qualType": "720"})
        self.assertEqual(response.status_code, 200)
        mockDownload.assert_called_once_with("testYoutubeURL.com", "720")
        self.assertIn("Downloaded video file", str(response.data))
        self.assertIn('value="testTitle_720p.mp4"', str(response.data))

    @patch.object(YoutubeDL, "downloadAudio", return_value={"ext": "mp3", "title": "testTitle"})
    def testAudioDownoladToServer(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL.com",
                                    "qualType": "mp3"})
        self.assertEqual(response.status_code, 200)
        mockDownload.assert_called_once_with("testYoutubeURL.com")
        self.assertIn("Downloaded audio file", str(response.data))
        self.assertIn('value="testTitle.mp3"', str(response.data))

    def testDownoladToServerNoType(self):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter type", str(response.data))

    def testDownoladToServerEmptyURL(self):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "",
                                   "qualType": "720"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter YouTube URL", str(response.data))

    @patch.object(YoutubeDL, "downloadVideo", return_value={"ext": "mp4", "title": "testTitle"})
    def testDownoladToServerPlaylistURLwithVideo(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?v=testVideo?list=playlist.com",
                                   "qualType": "720"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("You entered URL with playlist hash - only single video has been downloaded", str(response.data))
        mockDownload.assert_called_once_with("testYoutubeURL?v=testVideo?list=playlist.com", "720")
        self.assertIn("Downloaded video file", str(response.data))
        self.assertIn('value="testTitle_720p.mp4"', str(response.data))

    @patch.object(YoutubeDL, "downloadVideo", return_value="error")
    def testDownoladToServerPlaylistURLNoVideo(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?list=playlist.com",
                                   "qualType": "720"})
        self.assertEqual(response.status_code, 200)
        mockDownload.assert_called_once_with("testYoutubeURL?list=playlist.com", "720")
        self.assertIn("File not found - wrong link", str(response.data))
        self.assertIn('<title>YouTube</title>', str(response.data))

    @patch.object(YoutubeDL, "downloadAudio", return_value={"ext": "mp3", "title": "testTitle"})
    def testDownoladToServerPlaylistURLwithAudio(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?v=testVideo?list=playlist.com",
                                   "qualType": "mp3"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("You entered URL with playlist hash - only single video has been downloaded", str(response.data))
        mockDownload.assert_called_once_with("testYoutubeURL?v=testVideo?list=playlist.com")
        self.assertIn("Downloaded audio file", str(response.data))
        self.assertIn('value="testTitle.mp3"', str(response.data))

    @patch.object(YoutubeDL, "downloadAudio", return_value="error")
    def testDownoladToServerPlaylistURLNoAudio(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?list=playlist.com",
                                   "qualType": "mp3"})
        self.assertEqual(response.status_code, 200)
        mockDownload.assert_called_once_with("testYoutubeURL?list=playlist.com")
        self.assertIn("File not found - wrong link", str(response.data))
        self.assertIn('<title>YouTube</title>', str(response.data))

    def testYourubeHTML(self):
        response = self.flask.get("/youtube.html")
        self.assertIn('<title>YouTube</title>', str(response.data))
        self.assertEqual(response.status_code, 200)

    def testWrongYourubeHTML(self):
        response = self.flask.get("/youtubetest.html")
        self.assertEqual(response.status_code, 404)

    @patch.object(ConfigParserManager, "getPlaylists", return_value={"testPlaylistName": "testplaylistURL.com"})
    def testModifyPlaylistHtml(self, mockGetPlaylsits):
        response = self.flask.get("/modify_playlist.html")
        self.assertEqual(response.status_code, 200)
        mockGetPlaylsits.assert_called_once()
        self.assertIn('<option value=testPlaylistName>', str(response.data))
        self.assertIn('<title>Modify Playlist</title>', str(response.data))

    @patch.object(YoutubeDL, "downoladConfigPlaylistVideo")
    def testDownoladConfigPlaylistVideo(self, mockDownload):
        response = self.flask.get("/downloadConfigPlaylist")
        self.assertEqual(response.status_code, 200)
        mockDownload.assert_called_once_with(type=720)
        self.assertIn("All config playlist has been downloaded", str(response.data))
        self.assertIn('<title>YouTube</title>', str(response.data))

    @patch.object(flask, "send_file")
    @patch.object(utils, "sanitize_filename", return_value="testFileName")
    def testDownoladFile(self, mockSanitizeFilename, mockSendFile):
        response = self.flask.post("/downloadFile", data={"directoryPath": "test/path", "fileName": "testFileName"})
        self.assertEqual(response.status_code, 200)
        mockSanitizeFilename.assert_called_once_with("testFileName")
        mockSendFile.assert_called_once_with("test/path/testFileName", as_attachment=True)

    @patch.object(ConfigParserManager, "getPlaylists")
    def testAddPlaylistNoURL(self, mockGetPlaylists):
        response = self.flask.post("/modify_playlist", data={"playlistURL": "testYoutubeURL.com",
                                                             "playlistName": "testPlaylistName",
                                                             "AddPlaylistButton": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter correct URL of YouTube playlist", str(response.data))
        self.assertIn("<title>Modify Playlist</title>", str(response.data))
        mockGetPlaylists.assert_called_once()


    @patch.object(ConfigParserManager, "addPlaylist")
    @patch.object(ConfigParserManager, "getPlaylists")
    def testAddPlaylistCorrectURL(self, mockGetPlaylists, mockAddPlaylist):
        response = self.flask.post("/modify_playlist", data={"playlistURL": "testYoutubeURL?list=playlisHash.com",
                                                             "playlistName": "testPlaylistName",
                                                             "AddPlaylistButton": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mockGetPlaylists.call_count, 2)
        self.assertIn("Playlist testPlaylistName added to config file", str(response.data))
        self.assertIn("<title>Modify Playlist</title>", str(response.data))
        mockAddPlaylist.assert_called_once()

    @patch.object(ConfigParserManager, "getPlaylists")
    def testDeletePlaylistNoName(self, mockGetPlaylists):
        response = self.flask.post("/modify_playlist", data={"DeletePlaylistButton": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Select a playlist to delete", str(response.data))
        self.assertIn("<title>Modify Playlist</title>", str(response.data))
        mockGetPlaylists.assert_called_once()

    @patch.object(ConfigParserManager, "deletePlaylist")
    @patch.object(ConfigParserManager, "getPlaylists")
    def testDeletePlaylistWithName(self, mockGetPlaylists, mockDeletePlaylist):
        response = self.flask.post("/modify_playlist", data={"playlistSelect": "playlistToDelete",
                                                             "DeletePlaylistButton": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Playlist playlistToDelete deleted from config file", str(response.data))
        self.assertIn("<title>Modify Playlist</title>", str(response.data))
        self.assertEqual(mockGetPlaylists.call_count, 2)
        mockDeletePlaylist.assert_called_once()

    def testModifyPlaylist(self):
        with self.assertRaises(Exception) as fail:
            response = self.flask.post("/modify_playlist", data={"playlistSelect": "playlistToDelete"})
            self.assertEqual(response.status_code, 200)
            self.assertIn("<title>Modify Playlist</title>", str(response.data))
        self.assertIn('Undefined behaviour', str(fail.exception))


if __name__ == "__main__":
    main()