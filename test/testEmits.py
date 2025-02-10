from test.emitData import EmitData
from website_youtube_dl.flaskAPI.emits import (DownloadMediaFinishEmit,
                                               SingleMediaInfoEmit,
                                               PlaylistMediaInfoEmit,
                                               UploadPlaylistToConfigEmit,
                                               GetPlaylistUrlEmit)
from unittest import main, TestCase
from website_youtube_dl.flaskAPI.flaskMedia import (FlaskSingleMedia,
                                                    FlaskMediaFromPlaylist,
                                                    FlaskPlaylistMedia)
from website_youtube_dl.common.youtubeDataKeys import MediaInfo
from website_youtube_dl.config import TestingConfig
from website_youtube_dl import create_app, socketio
from website_youtube_dl.common.youtubeLogKeys import YoutubeVariables
from unittest.mock import MagicMock


class TestEmits(TestCase):
    testHash = "testHash"
    dataStr = "data"
    titleStr = "title"
    urlStr = "url"
    testPlaylistName = "playlistName"
    playlistStr = "playlistList"
    playlistUrlStr = "playlistUrl"
    trackList = "trackList"
    testTitle1 = "Society"
    testAlbum1 = "Into The Wild"
    testArtist1 = "Eddie Vedder"
    testOriginalUrl1 = 'https://www.youtube.com/watch?v=ABsslEoL0-c'

    testTitle2 = 'Hard Sun'
    testArtist2 = "Eddie Vedder"
    testExt2 = "webm"
    testPlaylistIndex2 = 2
    testOriginalUrl2 = 'https://www.youtube.com/watch?v=_EZUfnMv3Lg'
    youtubePlaylistURL = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"

    flaskSingleMedia = FlaskSingleMedia(testTitle1,
                                        testArtist1,
                                        testOriginalUrl1)

    flaskMediaFromPlaylist1 = FlaskMediaFromPlaylist(testTitle1,
                                                     testOriginalUrl1)

    flaskMediaFromPlaylist2 = FlaskMediaFromPlaylist(testTitle2,
                                                     testOriginalUrl2)
    trakListWithObjects = [flaskMediaFromPlaylist1, flaskMediaFromPlaylist2]
    trackListWithDict = [{titleStr: testTitle1,
                         urlStr: testOriginalUrl1},
                         {titleStr: testTitle2,
                          urlStr: testOriginalUrl2}]
    flaskPlaylistMedia = FlaskPlaylistMedia(
        testPlaylistName, trakListWithObjects)

    def setUp(self):
        self.downloadMediaFinishEmit = DownloadMediaFinishEmit()
        self.singleMediaInfoEmit = SingleMediaInfoEmit()
        self.playlistMediaInfoEmit = PlaylistMediaInfoEmit()
        self.uploadPlaylistToConfigEmit = UploadPlaylistToConfigEmit()
        self.getPlaylistUrlEmit = GetPlaylistUrlEmit()
        self.configManagerMock = MagicMock()
        app = create_app(TestingConfig, self.configManagerMock)
        app.config["TESTING"] = True
        self.socketIoTestClient = socketio.test_client(app)
        self.flask = app.test_client()
        self.app = app

    def testDownloadMediaFinishEmitConvertDataToMsg(self):
        result = self.downloadMediaFinishEmit.convertDataToMessage(
            self.testHash)
        self.assertEqual({YoutubeVariables.HASH.value: self.testHash},
                         result)

    def getEmitMassage(self, fullEmit, msgNumber):
        return fullEmit[msgNumber]

    def testDownloadMediaFinishEmitSendEmit(self):
        self.downloadMediaFinishEmit.sendEmit(self.testHash)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(self.downloadMediaFinishEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(self.dataStr, emitData.data)
        self.assertIn(YoutubeVariables.HASH.value,
                      emitData.data[self.dataStr])

    def testSingleMediaInfoEmitConvertDataToMsg(self):
        result = self.singleMediaInfoEmit.convertDataToMessage(
            self.flaskSingleMedia)
        self.assertEqual({
            MediaInfo.TITLE.value: self.flaskSingleMedia.title,
            MediaInfo.ARTIST.value: self.flaskSingleMedia.artist,
            MediaInfo.URL.value: self.flaskSingleMedia.url
        }, result)

    def testSingleMediaInfoEmitSendEmit(self):
        self.singleMediaInfoEmit.sendEmit(self.flaskSingleMedia)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(self.singleMediaInfoEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(self.dataStr, emitData.data)
        data = emitData.data[self.dataStr]
        self.assertEqual({
            MediaInfo.TITLE.value: self.flaskSingleMedia.title,
            MediaInfo.ARTIST.value: self.flaskSingleMedia.artist,
            MediaInfo.URL.value: self.flaskSingleMedia.url
        }, data)

    def testPlaylistMediaInfoEmitConvertDataToMsg(self):
        result = self.playlistMediaInfoEmit.convertDataToMessage(
            self.flaskPlaylistMedia)
        self.assertEqual({self.playlistMediaInfoEmit.playlistName: self.playlistMediaInfoEmit.playlistName,
                          self.playlistMediaInfoEmit.trackList: self.trackListWithDict}, result)

    def testPlaylistMediaInfoEmitConvertSendEmit(self):
        self.playlistMediaInfoEmit.sendEmit(self.flaskPlaylistMedia)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(self.playlistMediaInfoEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(self.dataStr, emitData.data)
        self.assertEqual(self.playlistMediaInfoEmit.playlistName,
                         emitData.data[self.dataStr][self.playlistMediaInfoEmit.playlistName])
        self.assertEqual(self.trackListWithDict,
                         emitData.data[self.dataStr][self.trackList])

    def testGetPlaylistUrlEmitConfigEmitConvertDataToMsg(self):
        result = self.getPlaylistUrlEmit.convertDataToMessage(
            self.youtubePlaylistURL)
        self.assertEqual(
            {self.playlistUrlStr: self.youtubePlaylistURL}, result)

    def testGetPlaylistUrlEmitConfigEmitSendEmit(self):
        self.getPlaylistUrlEmit.sendEmit(self.youtubePlaylistURL)
        pythonEmit = self.socketIoTestClient.get_received()
        receivedMsg = EmitData.getEmitMassage(pythonEmit, 0)
        emitData = EmitData.initFromMassage(receivedMsg)
        self.assertEqual(self.getPlaylistUrlEmit.emitMsg,
                         emitData.emitName)
        self.assertIn(self.dataStr, emitData.data)
        self.assertEqual(
            {self.playlistUrlStr: self.youtubePlaylistURL}, emitData.data[self.dataStr])


if __name__ == "__main__":
    main()
