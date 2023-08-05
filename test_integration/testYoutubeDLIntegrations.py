import sys
import os
sys.path.append("/home/rszczygielski/pythonVSC/personal_classes/youtube-dl")
import youtube.youtubeDL
from unittest import TestCase, main

class YoutubeDlTest(TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtube.youtubeDL.YoutubeDL(f'{self.testDir}/test_youtube_config.ini')

    def test_downloadFile(self):
        youtubeOptions = {
        # 'download_archive': 'downloaded_songs.txt',
        'addmetadata': True,
        'format': f'bestvideo[height=360][ext=mp4]+bestaudio/bestvideo+bestaudio',
        'outtmpl': self.testDir + '/%(title)s' + f'_360p' + '.%(ext)s'
        }
        metaData = self.youtubeTest.downloadFile("https://www.youtube.com/watch?v=ABsslEoL0-c", youtubeOptions)
        title = metaData["title"]
        ext = metaData["ext"]
        downlodedFilePath = os.path.join(self.testDir, title + '_360p' + f".{ext}")
        print(downlodedFilePath)
        self.assertTrue(os.path.isfile(downlodedFilePath))


class YoutubeAudioTest(TestCase):

    def setUp(self) -> None:
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        self.youtubeTest = youtube.youtubeDL.YoutubeDL(f'{self.testDir}/test_youtube_config.ini')
        self.youtubeTest.ydl_audio_opts['outtmpl'] = self.testDir + '/%(title)s.%(ext)s'


    def testDownloadAudio(self):
        print(self.testDir)
        metaData = self.youtubeTest.downloadAudio("https://www.youtube.com/watch?v=ABsslEoL0-c")
        title = metaData["title"]
        downloadedFilePath =os.path.join(self.testDir, f"{title}.mp3")
        self.assertTrue(os.path.isfile(downloadedFilePath))
        self.assertEqual("Society", title)
        self.assertEqual("Into The Wild", metaData["album"])
        self.assertEqual("Eddie Vedder", metaData["artist"])
        self.assertIsNone(metaData["playlist_index"])

if __name__ == "__main__":
    main()

# https://stackoverflow.com/questions/55295844/how-to-unittest-python-configparser