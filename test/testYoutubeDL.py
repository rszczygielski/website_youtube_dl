import os
import youtubeDL
import mutagen.easyid3
import mutagen.mp3
from youtubeDL import MetaDataType
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

class TestYoutubeDL(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(f'{self.testDir}/test_youtube_config.ini')
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

    @patch.object(youtubeDL.YoutubeDL, "setMetaDataPlaylist")
    @patch.object(youtubeDL.YoutubeDL, "downloadFile", return_value={"title": "testPlaylist", "entries":[{"title": "Society","album": "Into The Wild","artist": "Eddie Vedder","ext": "webm","playlist_index": None}]})
    def testDownloadPlaylistAudio(self, mockDownload, mockSetMetaData):
        metaData = self.youtubeTest.downloadAudioPlaylist("https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0")
        mockDownload.assert_called_once_with("PLAz00b-z3I5Um0R1_XqkbiqqkB0526jx0", self.youtubeTest.ydl_audio_opts)
        mockSetMetaData.assert_called_once_with(metaData)
        self.assertEqual(self.testMetaDataPlaylist, metaData)

    @patch.object(youtubeDL.YoutubeDL, "setMetaDataSingleFile")
    @patch.object(youtubeDL.YoutubeDL, "downloadFile", return_value={"title": "Society","album": "Into The Wild","artist": "Eddie Vedder","ext": "webm","playlist_index": None})
    def testDownloadPlaylistAudio(self, mockDownload, mockSetMetaData):
        metaData = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        mockDownload.assert_called_once_with("ABsslEoL0-c", self.youtubeTest.ydl_audio_opts)
        mockSetMetaData.assert_called_once_with(metaData)
        self.assertEqual(self.testMetaData, metaData)

if __name__ == "__main__":
    main()