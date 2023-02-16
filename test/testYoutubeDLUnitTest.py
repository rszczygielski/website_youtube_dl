import os
import youtubeDL
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

class YoutubeDlTest(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(f'{self.testDir}/test_youtube_config.ini')
        
    def test_downloadFile(self):
        testMetaData = {
        "title": "Society",
        "album": "Into The Wild",
        "artist": "Eddie Vedder",
        "ext": "webm",
        "playlist_index": None
        }
        youtubeOptions = {
        # 'download_archive': 'downloaded_songs.txt',
        'addmetadata': True,
        'format': f'bestvideo[height=360][ext=mp4]+bestaudio/bestvideo+bestaudio',
        'outtmpl': self.testDir + '/%(title)s' + f'_360p' + '.%(ext)s'
        }
        self.youtubeTest.downloadFile = MagicMock(return_value=testMetaData)
        metaData =  self.youtubeTest.downloadFile("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        # metaData =  self.youtubeTest.downloadFile("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        # self.youtubeTest.downloadFile.assert_called_once_with("https://www", youtubeOptions)
        self.youtubeTest.downloadFile.assert_called_once_with("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        self.assertEqual(metaData, testMetaData)

class YoutubeAudioTest(TestCase):

    def setUp(self) -> None:
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtubeDL.YoutubeDL(f'{self.testDir}/test_youtube_config.ini')
        self.youtubeTest.ydl_audio_opts['outtmpl'] = self.testDir + '/%(title)s.%(ext)s'

    
    def testDownloadAudio(self):
        testMetaData = {
        "title": "Society",
        "album": "Into The Wild",
        "artist": "Eddie Vedder",
        "ext": "webm",
        "playlist_index": None
        }
        self.youtubeTest.downloadFile = MagicMock(return_value=testMetaData)
        metaData = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        self.youtubeTest.downloadFile.assert_called_once_with("ABsslEoL0-c", self.youtubeTest.ydl_audio_opts)
        self.assertEqual("Society", metaData["title"])
        self.assertEqual("Into The Wild", metaData["album"])
        self.assertEqual("Eddie Vedder", metaData["artist"])
        self.assertIsNone(metaData["playlist_index"])

    def getMetaDataFromYoutube2(youtubeURL, youtubeOptions):
        print(youtubeURL)
        print(youtubeOptions)
        return {
            "title": "Society",
            "album": "Into The Wild",
            "artist": "Eddie Vedder",
            "ext": "webm",
            "playlist_index": None
            }
    
    @patch.object(youtubeDL.YoutubeDL,"downloadFile", side_effect=getMetaDataFromYoutube2)
    def testDownloadAudioWithDecorator(self, mockDownloadFile):
        metaData = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        mockDownloadFile.assert_called_once_with("ABsslEoL0-c", self.youtubeTest.ydl_audio_opts)
        self.assertEqual("Society", metaData["title"])
        self.assertEqual("Into The Wild", metaData["album"])
        self.assertEqual("Eddie Vedder", metaData["artist"])
        self.assertIsNone(metaData["playlist_index"])

    @patch("youtubeDL.YoutubeDL.downloadFile", return_value=
            {
            "title": "Society",
            "album": "Into The Wild",
            "artist": "Eddie Vedder",
            "ext": "webm",
            "playlist_index": None
            })
    def testDownloadAudioWithDecorator(self, mockDownloadFile):
        metaData = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        mockDownloadFile.assert_called_once_with("ABsslEoL0-c", self.youtubeTest.ydl_audio_opts)
        self.assertEqual("Society", metaData["title"])
        self.assertEqual("Into The Wild", metaData["album"])
        self.assertEqual("Eddie Vedder", metaData["artist"])
        self.assertIsNone(metaData["playlist_index"])

if __name__ == "__main__":
    main()