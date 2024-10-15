from website_youtube_dl.flaskAPI import emits
from unittest import TestCase, main
from website_youtube_dl.flaskAPI.flaskMedia import (FlaskPlaylistMedia,
                                                    FlaskMediaFromPlaylist,
                                                    FlaskSingleMedia)
import os
from website_youtube_dl.common.youtubeDataKeys import PlaylistInfo, MediaInfo 

class TestEmits(TestCase):
    testTitle1 = "Society"
    testArtist = "Eddie Vedder"
    testOriginalUrl1 = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    testTitle2 = "Hard Sun"
    testOriginalUrl2 = "https://www.youtube.com/watch?v=_EZUfnMv3Lg"
    testPlaylistName = "testPlaylist"
    playlistName = "playlistName"
    trackList = "trackList"
    title = "title"
    url = "url"
    artist = "artist"


    mediaFromPlaylistTest1 = FlaskMediaFromPlaylist(testTitle1, testOriginalUrl1)

    mediaFromPlaylistTest2 = FlaskMediaFromPlaylist(testTitle2, testOriginalUrl2)

    

    playlistMediaTest = FlaskPlaylistMedia.initFromPlaylistMedia(testPlaylistName, [mediaFromPlaylistTest1,
                                                              mediaFromPlaylistTest2])
    
    singleMedia = FlaskSingleMedia(testTitle1, testArtist, testOriginalUrl1)


    def setUp(self):
        self.playlistMediaInfoEmits = emits.PlaylistMediaInfoEmit()
        self.singleMediaInfoEmits = emits.SingleMediaInfoEmit()

    def testConvertDataToMassagePlaylist(self):
        result = self.playlistMediaInfoEmits.convertDataToMessage(self.playlistMediaTest)
        expectedResult = {self.playlistName: self.testPlaylistName,
                          self.trackList: [{PlaylistInfo.TITLE.value: self.testTitle1,
                                            PlaylistInfo.URL.value: self.testOriginalUrl1},
                                        {PlaylistInfo.TITLE.value: self.testTitle2,
                                         PlaylistInfo.URL.value: self.testOriginalUrl2}]}
        self.assertEqual(result, expectedResult)
    
    def testConvertDataToMassageSingle(self):
        result = self.singleMediaInfoEmits.convertDataToMessage(self.singleMedia)
        expectedResult = {MediaInfo.TITLE.value:  self.testTitle1, 
                        MediaInfo.ARTIST.value: self.testArtist, 
                        MediaInfo.URL.value: self.testOriginalUrl1}
        self.assertEqual(result, expectedResult)

if __name__ == "__main_":
    main()