import unittest
from yt_dlp import utils
import mainWebPage
import flask
from configParserManager import ConfigParserManager
from youtubeDL import YoutubeDL
from mailManager import Mail
from unittest import TestCase
from unittest.mock import MagicMock, patch, call

class TestMainWeb(TestCase):

    def setUp(self):
        mainWebPage.app.config["TESTING"] = True
        self.flask = mainWebPage.app.test_client()

    def testIndexHTML(self):
        response = self.flask.get("/index.html")
        self.assertIn("<title>FlaskHomePage</title>", str(response.data))
        self.assertEqual(response.status_code, 200)

    def testWrongHTML(self):
        response = self.flask.get("/index")
        self.assertEqual(response.status_code, 404)

    def testWrongSenMail(self):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput",
                                           "messageText": "testMessageText"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Wrong mail adress", str(response.data))

    def testSendMailWithNoText(self):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput@gmail.com",
                                    "messageText": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Wrong empty massage", str(response.data))

    @patch.object(Mail, "sendMailFromHTML")
    def testSendMail(self, mockSendMail):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput@gmail.com",
                                    "messageText": "testMessageText"})
        self.assertEqual(response.status_code, 200)
        mockSendMail.assert_called_once_with("testSenderInput@gmail.com", "Automatic mail from flask", "testMessageText")
        self.assertIn("Mail was sucessfuly was send", str(response.data))

    @patch.object(Mail, "initialize")
    def testMailHTML(self, mockInitialize):
        response = self.flask.get("/mail.html")
        self.assertEqual(response.status_code, 200)
        mockInitialize.assert_called_once()

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

    @patch.object(YoutubeDL, "downloadVideo", return_value={})
    def testDownoladToServerPlaylistURLNoVideo(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?list=playlist.com",
                                   "qualType": "720"})
        self.assertEqual(response.status_code, 200)
        mockDownload.assert_called_once_with("testYoutubeURL?list=playlist.com", "720")
        self.assertIn("File not downloaded", str(response.data))
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

    @patch.object(YoutubeDL, "downloadAudio", return_value={})
    def testDownoladToServerPlaylistURLNoAudio(self, mockDownload):
        response = self.flask.post("/downloadToServer", data={"youtubeURL": "testYoutubeURL?list=playlist.com",
                                   "qualType": "mp3"})
        self.assertEqual(response.status_code, 200)
        mockDownload.assert_called_once_with("testYoutubeURL?list=playlist.com")
        self.assertIn("File not downloaded", str(response.data))
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

    @patch.object(ConfigParserManager, "addPlaylist")
    @patch.object(ConfigParserManager, "getPlaylists")
    def testAddPlaylist(self, mockGetPlaylist, mockGetPlaylsits):
        response = self.flask.post("/modify_playlist", data={"playlistURL": "testYoutubeURL.com",
                                                             "playlistName": "testPlaylistName",
                                                             "AddPlaylistButton": ""})
        # self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter correct URL of YouTube playlist", str(response.data))

# testy do modify_playlist


if __name__ == "__main__":
    unittest.main()

    # jeśli coś nie jest linkiem to zwróc erro youtubeDL

    # przekazywać obiekt Gmail do MailManagera po to aby można było zamockować send_massage tak
    # samo jak w przypadku Config menagera