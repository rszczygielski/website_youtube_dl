import os
import yt_dlp
from unittest import TestCase, main
from unittest.mock import patch, call, MagicMock
from website_youtube_dl.common.youtubeConfigManager import BaseConfigParser
from website_youtube_dl.common.youtubeDataKeys import PlaylistInfo, MediaInfo
import website_youtube_dl.common.youtubeDL as youtubeDL
from website_youtube_dl.common.youtubeAPI import (SingleMedia,
                                                  MediaFromPlaylist,
                                                  PlaylistMedia)
from test.configParserMock import ConfigParserMock
from test.easyID3ManagerMock import EasyID3ManagerMock
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from website_youtube_dl.common.youtubeOptions import YoutubeOptiones


class TestYoutubeDL(TestCase):
    mainURL1 = "https://www.youtube.com/watch?v=ABsslEoL0-c"
    main_playlist_url_with_video_hash1 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    main_playlist_url_no_video_hash1 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    main_playlist_url_no_video_hash2 = "https://www.youtube.com/playlist?list=PLAz00b-z3I5WEWEj9eWN_xvTmAtwI0_gU"
    main_playlist_url_with_index1 = "https://www.youtube.com/watch?v=ABsslEoL0-c&list=PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO&index=1"
    main_playlist_hash = "PLAz00b-z3I5Um0R1_XqkbiqqkB0526jxO"
    main_media_download_error = "Download media info error ValueError"
    main_playlist_without_video_error = 'This a playlist only - without video hash to download'

    folder_path = os.path.abspath(__file__)

    test_playlist_name = "test_playlist"
    test_title1 = "Society"
    test_album1 = "Into The Wild"
    test_artist1 = "Eddie Vedder"
    test_ext1 = "webm"
    test_playlistIndex1 = 1
    test_original_url1 = 'https://www.youtube.com/watch?v=ABsslEoL0-c'
    testId1 = 'ABsslEoL0-c'
    test_full_path1 = f"{folder_path}/{test_title1}.webm"

    test_title2 = 'Hard Sun'
    test_artist2 = "Eddie Vedder"
    test_ext2 = "webm"
    test_playlist_index2 = 2
    test_original_url2 = 'https://www.youtube.com/watch?v=_EZUfnMv3Lg'
    testId2 = '_EZUfnMv3Lg'
    test_full_path2 = f"{folder_path}/{test_title2}.webm"

    list_of_formats = ['360', '480', '720', '1080', '2160']

    # Global test file names
    test_file_1 = "file1.mp3"
    test_file_2 = "file2.mp3"
    test_file_3 = "file3.txt"

    songMetaData1 = {
        MediaInfo.TITLE.value: test_title1,
        MediaInfo.ALBUM.value: test_album1,
        MediaInfo.ARTIST.value: test_artist1,
        MediaInfo.EXTENSION.value: test_ext1,
        PlaylistInfo.PLAYLIST_INDEX.value: test_playlistIndex1,
        MediaInfo.URL.value: test_original_url1,
        MediaInfo.YOUTUBE_HASH.value: testId1,
        MainYoutubeKeys.REQUESTED_DOWNLOADS.value: [
            {MainYoutubeKeys.FUL_PATH.value: test_full_path1}]
    }

    songMetaData2 = {
        MediaInfo.TITLE.value: test_title2,
        MediaInfo.ARTIST.value: test_artist2,
        MediaInfo.ALBUM.value: test_album1,
        MediaInfo.EXTENSION.value: test_ext2,
        PlaylistInfo.PLAYLIST_INDEX.value: test_playlist_index2,
        MediaInfo.URL.value: test_original_url2,
        MediaInfo.YOUTUBE_HASH.value: testId2,
        MainYoutubeKeys.REQUESTED_DOWNLOADS.value: [
            {MainYoutubeKeys.FUL_PATH.value: test_full_path2}]

    }

    songFromPlaylist1 = {
        PlaylistInfo.TITLE.value: test_title1,
        PlaylistInfo.URL.value: testId1,
    }

    songFromPlaylist2 = {
        PlaylistInfo.TITLE.value: test_title2,
        PlaylistInfo.URL.value: testId2,
    }

    test_playlistFullEntries = [songMetaData1, songMetaData2, None]
    playlistMetaDataFull = {
        PlaylistInfo.TITLE.value: test_playlist_name,
        PlaylistInfo.PLAYLIST_TRACKS.value: test_playlistFullEntries
    }

    testEntriesList = [songFromPlaylist1, songFromPlaylist2, None]
    testPlaylsitUrlsList = [
        main_playlist_url_no_video_hash1, main_playlist_url_no_video_hash2]

    plalistMetaData = {
        PlaylistInfo.TITLE.value: test_playlist_name,
        PlaylistInfo.PLAYLIST_TRACKS.value: testEntriesList
    }

    singleMediaTest = SingleMedia(test_full_path1, test_title1, test_album1,
                                  test_artist1, testId1,
                                  test_original_url1, test_ext1)

    mediaFromPlaylistTest1 = MediaFromPlaylist(test_title1, testId1)

    mediaFromPlaylistTest2 = MediaFromPlaylist(test_title2, testId2)

    # pisz tak zmienne testowe MEDIA_FROM_PLAYLIST2

    playlist_mediaTest = PlaylistMedia(test_playlist_name, [mediaFromPlaylistTest1,
                                                            mediaFromPlaylistTest2])

    def setUp(self):
        self.testDir = os.path.dirname(os.path.abspath(__file__))
        config_parser_manager = BaseConfigParser(f'{self.testDir}/test_youtube_config.ini',
                                                 ConfigParserMock())
        self.youtube_test = youtubeDL.YoutubeDL(config_parser_manager)
        self.youtubeConfigPlaylists = youtubeDL.YoutubeDlPlaylists(config_parser_manager,
                                                                   MagicMock())
        self.youtube_test._savePath = self.testDir
        self.youtube_test._ydl_opts.overwrite_option(YoutubeOptiones.OUT_TEMPLATE,
                                                     self.testDir + '/%(title)s.%(ext)s')
        self.easy_id3_manager_mock = EasyID3ManagerMock()
        self.easy_id3_manager_mock.set_params(
            filePath=self.testDir,
            title=self.test_title1,
            album=self.test_album1,
            artist=self.test_artist1,
            track_number=self.test_playlistIndex1,
            playlist_name=self.test_playlist_name,
        )

    def check_result_single_media(self, singleMedia, singleMediaExpected):
        self.assertEqual(singleMedia.title, singleMediaExpected.title)
        self.assertEqual(singleMedia.album, singleMediaExpected.album)
        self.assertEqual(singleMedia.artist, singleMediaExpected.artist)
        self.assertEqual(singleMedia.extension, singleMediaExpected.extension)
        self.assertEqual(singleMedia.url, singleMediaExpected.url)
        self.assertEqual(singleMedia.yt_hash, singleMediaExpected.yt_hash)

    def check_media_from_playlist(self, mediaFromPlaylist, mediaFromPlaylistExpected):
        self.assertEqual(mediaFromPlaylist.title,
                         mediaFromPlaylistExpected.title)
        self.assertEqual(mediaFromPlaylist.yt_hash,
                         mediaFromPlaylistExpected.yt_hash)

    def check_resul_playlist_meida(self, playlist_media: youtubeDL.PlaylistMedia,
                                   playlist_mediaExpected: youtubeDL.PlaylistMedia):
        self.assertEqual(playlist_media.playlist_name,
                         playlist_mediaExpected.playlist_name)
        self.assertEqual(len(playlist_media.media_from_playlist_list), len(
            playlist_mediaExpected.media_from_playlist_list))
        for idex in range(len(playlist_media.media_from_playlist_list)):
            self.check_media_from_playlist(playlist_media.media_from_playlist_list[idex],
                                           playlist_mediaExpected.media_from_playlist_list[idex])

    # bez sensu testować ale błedy sprawdzać
    def check_fast_download_result(self, metaData):
        resultTest = {'title': 'test_playlist', 'entries': [
            self.songFromPlaylist1, self.songFromPlaylist2, None]}
        if metaData != resultTest:
            return False
        else:
            return True

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def test_download_file(self, mockExtractinfo):
        resultOfYoutube = self.youtube_test._download_file(self.mainURL1)
        self.assertEqual(False, resultOfYoutube.is_error())
        mockExtractinfo.assert_called_once_with(self.mainURL1)
        singleMedia = resultOfYoutube.get_data()
        self.check_result_single_media(singleMedia, self.singleMediaTest)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def test_download_file_different_title_template(self, mockExtractinfo):
        self.youtube_test.set_title_template_one_time("test")
        self.assertEqual("test", self.youtube_test.title_template)
        resultOfYoutube = self.youtube_test._download_file(self.mainURL1)
        self.assertEqual(False, resultOfYoutube.is_error())
        mockExtractinfo.assert_called_once_with(self.mainURL1)
        singleMedia = resultOfYoutube.get_data()
        self.check_result_single_media(singleMedia, self.singleMediaTest)
        self.assertEqual('/%(title)s', self.youtube_test.title_template)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(main_media_download_error))
    def test_download_file_with_error(self, mockExtractinfo):
        resultOfYoutube = self.youtube_test._download_file(self.mainURL1)
        self.assertEqual(True, resultOfYoutube.is_error())
        mockExtractinfo.assert_called_once_with(self.mainURL1)
        error_msg = resultOfYoutube.get_error_info()
        self.assertEqual(error_msg, self.main_media_download_error)

    def test_get_video_hash(self):
        correctVideoHash = self.testId1
        testVideoHash1 = self.youtube_test._get_media_result_hash(
            self.mainURL1)
        self.assertEqual(testVideoHash1, correctVideoHash)
        testVideoHash2 = self.youtube_test._get_media_result_hash(
            self.main_playlist_url_with_video_hash1)
        self.assertEqual(testVideoHash2, correctVideoHash)
        testVideoHash3 = self.youtube_test._get_media_result_hash(
            self.main_playlist_url_with_index1)
        self.assertEqual(testVideoHash3, correctVideoHash)
        testVideoHash4 = self.youtube_test._get_media_result_hash(
            self.testId1)
        self.assertEqual(testVideoHash4, self.testId1)
        wrong_link_with_video = self.main_playlist_url_no_video_hash1
        with self.assertRaises(ValueError) as context:
            self.youtube_test._get_media_result_hash(wrong_link_with_video)
        self.assertTrue(
            self.main_playlist_without_video_error in str(context.exception))

    def test_get_playlist_hash(self):
        correectPlaylistHash = self.main_playlist_hash
        testVideoHash1 = self.youtube_test._get_playlist_hash(
            self.main_playlist_url_no_video_hash1)
        self.assertEqual(testVideoHash1, correectPlaylistHash)
        testVideoHash2 = self.youtube_test._get_playlist_hash(
            self.main_playlist_url_with_video_hash1)
        self.assertEqual(testVideoHash2, correectPlaylistHash)
        testVideoHash3 = self.youtube_test._get_playlist_hash(
            self.main_playlist_url_with_index1)
        self.assertEqual(testVideoHash3, correectPlaylistHash)
        wrong_link_with_video = self.mainURL1
        with self.assertRaises(ValueError) as context:
            self.youtube_test._get_playlist_hash(wrong_link_with_video)
        self.assertTrue('This is not a playlist' in str(context.exception))

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value=songMetaData1)
    def test_download_video(self, mockDownloadFile):
        youtubeResult = self.youtube_test.download_video(self.mainURL1, "480")
        singleMedia = youtubeResult.get_data()
        mockDownloadFile.assert_called_once_with(self.testId1)
        self.check_result_single_media(singleMedia, self.singleMediaTest)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(main_media_download_error))
    def test_download_video_with_error(self, mockDownloadFile,):
        youtubeResult = self.youtube_test.download_video(self.mainURL1, "480")
        mockDownloadFile.assert_any_call(self.testId1)
        self.assertEqual(mockDownloadFile.mock_calls[0], call(self.testId1))
        self.assertEqual(youtubeResult.is_error(), True)
        self.assertEqual(youtubeResult.get_error_info(),
                         self.main_media_download_error)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": test_playlist_name,
                                "entries": testEntriesList})
    def testdownload_whole_video_playlist(self, mockExtractinfo):
        metaData = self.youtubeConfigPlaylists.download_whole_video_playlist(
            self.main_playlist_url_no_video_hash1, "480")
        mockExtractinfo.assert_called_once_with(self.main_playlist_hash)
        checkResult = self.check_fast_download_result(metaData)
        self.assertEqual(True, checkResult)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(main_media_download_error))
    def test_download_video_playlist_with_error(self, mockDownloadError):
        error_msg = self.youtubeConfigPlaylists.download_whole_video_playlist(
            self.main_playlist_url_no_video_hash1, "480")
        mockDownloadError.assert_called_once_with(self.main_playlist_hash)
        self.assertFalse(error_msg)

# importować easy_id3_manager to już imporotwać zmocowanaą wersję
    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": test_playlist_name,
                                "entries": test_playlistFullEntries})
    def test_fast_download_playlist_audio(self, mockExtractinfo):
        metaData = self.youtubeConfigPlaylists.download_whole_audio_playlist(
            self.main_playlist_url_no_video_hash1)
        mockExtractinfo.assert_called_once_with(self.main_playlist_hash)
        self.assertEqual(self.playlistMetaDataFull, metaData)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  return_value={"title": test_playlist_name})
    def test_fast_download_playlist_audio_no_entries(self, mockExtractinfo):
        functionResult = self.youtubeConfigPlaylists.download_whole_audio_playlist(
            self.main_playlist_url_no_video_hash1)
        mockExtractinfo.assert_called_once_with(self.main_playlist_hash)
        self.assertEqual(False, functionResult)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(main_media_download_error))
    def test_fast_download_playlist_audio_with_error(self, mockDownloadError):
        error_msg = self.youtubeConfigPlaylists.download_whole_audio_playlist(
            self.main_playlist_url_no_video_hash1)
        mockDownloadError.assert_called_once_with(self.main_playlist_hash)
        self.assertFalse(error_msg)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def test_download_audio(self, mock_save):
        single_media_info_result = self.youtube_test.download_audio(
            self.mainURL1)
        singleMedia = single_media_info_result.get_data()
        mock_save.assert_called_once()
        self.check_result_single_media(singleMedia, self.singleMediaTest)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(main_media_download_error))
    def test_download_audio_with_error(self, mockDownloadFile):
        youtubeResult = self.youtube_test.download_audio(self.mainURL1)
        self.assertEqual(youtubeResult.is_error(), True)
        mockDownloadFile.assert_called_once_with(self.testId1)
        self.assertEqual(youtubeResult.get_error_info(),
                         self.main_media_download_error)

    @patch.object(youtubeDL.YoutubeDlPlaylists, "download_whole_audio_playlist")
    @patch.object(youtubeDL.BaseConfigParser,
                  "get_url_of_playlists",
                  return_value=testPlaylsitUrlsList)
    def test_download_audio_from_config_two_playlists(
            self, mockGetPlaylists, mock_download_audio):
        metaData = self.youtubeConfigPlaylists.downolad_all_config_playlists_audio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mock_download_audio.call_count, 2)
        self.assertEqual(metaData, True)

    @patch.object(youtubeDL.YoutubeDlPlaylists, "download_whole_audio_playlist")
    @patch.object(youtubeDL.BaseConfigParser,
                  "get_url_of_playlists", return_value=[])
    def test_download_audio_from_config_zero_playlists(
            self, mockGetPlaylists, mock_download_audio):
        metaData = self.youtubeConfigPlaylists.downolad_all_config_playlists_audio()
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mock_download_audio.call_count, 0)
        self.assertEqual(metaData, True)

    @patch.object(youtubeDL.YoutubeDlPlaylists, "download_whole_video_playlist")
    @patch.object(youtubeDL.BaseConfigParser,
                  "get_url_of_playlists",
                  return_value=[main_playlist_url_no_video_hash1])
    def test_download_video_from_config_one_playlists(
            self, mockGetPlaylists, mockDownloadVideo):
        type = "720"
        metaData = self.youtubeConfigPlaylists.downolad_all_config_playlists_video(
            type)
        mockGetPlaylists.assert_called_once()
        mockDownloadVideo.assert_called_once_with(
            self.main_playlist_url_no_video_hash1, type)
        self.assertEqual(metaData, True)

    @patch.object(youtubeDL.YoutubeDlPlaylists, "download_whole_video_playlist")
    @patch.object(youtubeDL.BaseConfigParser,
                  "get_url_of_playlists",
                  return_value=testPlaylsitUrlsList)
    def test_download_video_from_config_two_playlists(
            self, mockGetPlaylists, mockDownloadVideo):
        type = "720"
        metaData = self.youtubeConfigPlaylists.downolad_all_config_playlists_video(
            type)
        mockGetPlaylists.assert_called_once()
        self.assertEqual(mockDownloadVideo.call_count, 2)
        mockDownloadVideo.assert_has_calls([call(self.main_playlist_url_no_video_hash1, type),
                                            call(self.main_playlist_url_no_video_hash2, type)])
        self.assertEqual(mockDownloadVideo.call_count, 2)
        self.assertEqual(metaData, True)

    @patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=songMetaData1)
    def testrequest_single_media_info(self, mockExtractInfo):
        resultOfYoutube = self.youtube_test.request_single_media_info(
            self.mainURL1)
        mockExtractInfo.assert_called_once()
        self.assertEqual(False, resultOfYoutube.is_error())
        singleMedia = resultOfYoutube.get_data()
        self.check_result_single_media(singleMedia, self.singleMediaTest)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(main_media_download_error))
    def testget_single_media_info_with_error(self, mockExtractInfo):
        resultOfYoutube = self.youtube_test.request_single_media_info(
            self.mainURL1)
        mockExtractInfo.assert_called_once()
        self.assertEqual(True, resultOfYoutube.is_error())
        error_msg = resultOfYoutube.get_error_info()
        self.assertTrue(error_msg, self.main_media_download_error)
        self.assertFalse(resultOfYoutube.get_data())

    @patch.object(yt_dlp.YoutubeDL,
                  "extract_info",
                  return_value={"title": test_playlist_name,
                                "entries": testEntriesList})
    def test_get_playlist_media_info(self, mockDownloadFile):
        resultOfYoutube = self.youtube_test.request_playlist_media_info(
            self.main_playlist_url_no_video_hash1)
        mockDownloadFile.assert_called_once()
        self.assertEqual(False, resultOfYoutube.is_error())
        playlist_media = resultOfYoutube.get_data()
        self.check_resul_playlist_meida(playlist_media,
                                        self.playlist_mediaTest)

    @patch.object(yt_dlp.YoutubeDL, "extract_info",
                  side_effect=ValueError(main_media_download_error))
    def testget_playlist_media_info_with_error(self, mockExtractInfo):
        resultOfYoutube = self.youtube_test.request_playlist_media_info(
            self.main_playlist_url_no_video_hash1)
        mockExtractInfo.assert_called_once()
        self.assertEqual(True, resultOfYoutube.is_error())
        error_msg = resultOfYoutube.get_error_info()
        self.assertTrue(error_msg, self.main_media_download_error)
        self.assertFalse(resultOfYoutube.get_data())

    def test_get_playlist_media_result(self):
        playlist_media = self.youtube_test._get_playlist_media(
            self.plalistMetaData)
        self.check_resul_playlist_meida(playlist_media,
                                        self.playlist_mediaTest)

    def test_get_single_media_result(self):
        singleMedia = self.youtube_test._get_media(
            self.songMetaData1)
        self.check_result_single_media(singleMedia, self.singleMediaTest)

    @patch("os.listdir", return_value=[test_file_1, test_file_2, test_file_3])
    @patch("os.path.isfile", side_effect=lambda path: path.endswith(".mp3"))
    @patch.object(youtubeDL.YoutubeDL, "if_video_exist_on_youtube", side_effect=[True, False])
    def test_verify_local_files(self, mock_if_video_exist, mock_isfile, mock_listdir):
        not_verified_files = self.youtube_test.verify_local_files(
            self.testDir, EasyID3ManagerMock)
        mock_listdir.assert_called_once_with(self.testDir)
        self.assertEqual(mock_isfile.call_count, 3)
        self.assertEqual(mock_if_video_exist.call_count,
                         2)
        self.assertEqual(not_verified_files, [
            os.path.join(self.testDir, self.test_file_2)
        ])

    @patch("os.listdir", return_value=[test_file_1, test_file_2])
    @patch("os.path.isfile", side_effect=lambda path: path.endswith(".mp3"))
    @patch.object(youtubeDL.YoutubeDL, "if_video_exist_on_youtube", return_value=True)
    def test_verify_local_files_all_verified(self, mock_if_video_exist, mock_isfile, mock_listdir):
        not_verified_files = self.youtube_test.verify_local_files(
            self.testDir, EasyID3ManagerMock)

        mock_listdir.assert_called_once_with(self.testDir)
        self.assertEqual(mock_isfile.call_count, 2)
        self.assertEqual(mock_if_video_exist.call_count,
                         2)
        self.assertEqual(not_verified_files, [])

    @patch("os.listdir", return_value=[test_file_1, test_file_2])
    @patch("os.path.isfile", side_effect=lambda path: path.endswith(".mp3"))
    @patch.object(youtubeDL.YoutubeDL, "if_video_exist_on_youtube", return_value=False)
    def test_verify_local_files_none_verified(self, mock_if_video_exist, mock_isfile, mock_listdir):
        not_verified_files = self.youtube_test.verify_local_files(
            self.testDir, EasyID3ManagerMock)
        mock_listdir.assert_called_once_with(self.testDir)
        self.assertEqual(mock_isfile.call_count, 2)
        self.assertEqual(mock_if_video_exist.call_count,
                         2)
        self.assertEqual(not_verified_files, [
            os.path.join(self.testDir, self.test_file_1),
            os.path.join(self.testDir, self.test_file_2),
        ])


if __name__ == "__main__":
    main()
