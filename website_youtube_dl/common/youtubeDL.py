import yt_dlp
import logging
import os
from .youtubeConfigManager import BaseConfigParser
from .easyID3Manager import EasyID3Manager
from .myLogger import Logger, LoggerClass
from .youtubeDataKeys import (PlaylistInfo,
                              MediaInfo)
from .youtubeOptions import (YoutubeDefaultOptiones,
                             YoutubeGetSingleInfoOptiones,
                             YoutubeGetPlaylistInfoOptiones,
                             YoutubeAudioOptions,
                             YoutubeVideoOptions,
                             VideoVerificationOptiones)
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from website_youtube_dl.common.youtubeAPI import (SingleMedia,
                                                  MediaFromPlaylist,
                                                  PlaylistMedia,
                                                  ResultOfYoutube)


logger = logging.getLogger(__name__)


class YoutubeDL():
    title_template_default = "/%(title)s"
    title_template = title_template_default

    def __init__(
            self,
            configManager: BaseConfigParser,
            ytLogger: LoggerClass = logger):
        self._configManager = configManager
        self.yt_logger = ytLogger
        self._savePath = self._configManager.get_save_path()
        self._ydl_opts = YoutubeDefaultOptiones()
        self._ydl_single_info_opts = YoutubeGetSingleInfoOptiones()
        self._ydl_playlist_info_opts = YoutubeGetPlaylistInfoOptiones()

    def _download_file(self, single_media_hash: str, ydl_opts=None):
        """Method used to download youtube media based on URL

        Args:
            single_media_hash (str): Hash of YouTube media
            youtubeOptions (dict): YouTube options dict form init

        Returns:
            class: meta data form youtube
        """
        if ydl_opts is None:
            ydl_opts = self._ydl_opts.to_dict()
        result_of_youtube = ResultOfYoutube()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                meta_data = ydl.extract_info(single_media_hash)
            except Exception as exception:
                error_info = str(exception)
                logger.error(f"Download media info error {error_info}")
                result_of_youtube.set_error(error_info)
        if not result_of_youtube.is_error():
            single_media = self._get_media(meta_data)
            result_of_youtube.set_data(single_media)
        if self.title_template != self.title_template_default:
            self.title_template = self.title_template_default
        return result_of_youtube

    def download_video(self, youtubeURL: str, type: str) -> ResultOfYoutube:
        """Method uded to download video type from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video meta data
        """
        media_hash = self._get_media_result_hash(youtubeURL)
        video_options = self._get_video_options(type)
        result_of_youtube = self._download_file(media_hash, video_options)
        if result_of_youtube.is_error():
            error_msg = result_of_youtube.get_error_info()
            logger.error(f"Download video info error: {error_msg}")
            return result_of_youtube
        return result_of_youtube

    def download_audio(self, youtubeURL: str):
        """Method uded to download audio type from Youtube

        Args:
            youtubeURL (str): YouTube URL
        """
        media_hash = self._get_media_result_hash(youtubeURL)
        ydl_opts = self._get_audio_options()
        result_of_youtube = self._download_file(media_hash, ydl_opts)
        if result_of_youtube.is_error():
            error_msg = result_of_youtube.get_error_info()
            logger.error(f"Download audio info error: {error_msg}")
            return result_of_youtube
        return result_of_youtube

    def request_playlist_media_info(self, youtubeURL) -> ResultOfYoutube:
        """Method returns meta data based on youtube url

        Args:
            youtubeURL (string): Youtube URL

        Returns:
            ResultOfYoutube: result of youtube with metadata
        """
        yt_options = self._ydl_playlist_info_opts.to_dict()
        with yt_dlp.YoutubeDL(yt_options) as ydl:
            try:
                meta_data = ydl.extract_info(youtubeURL, download=False)
            except Exception as exception:
                error_info = str(exception)
                logger.error(f"Download media info error {error_info}")
                result_of_youtube = ResultOfYoutube()
                result_of_youtube.set_error(error_info)
                return result_of_youtube
        playlist_media = self._get_playlist_media(meta_data)
        return ResultOfYoutube(playlist_media)

    def request_single_media_info(self, youtubeURL) -> ResultOfYoutube:
        """Method provides youtube media info based on youtube URL without downloading it

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with Youtube info
        """
        youtube_hash = self._get_media_result_hash(youtubeURL)
        yt_options = self._ydl_single_info_opts.to_dict()
        with yt_dlp.YoutubeDL(yt_options) as ydl:
            try:
                meta_data = ydl.extract_info(youtube_hash, download=False)
            except Exception as exception:
                error_info = str(exception)
                logger.error(f"Download media info error {error_info}")
                result_of_youtube = ResultOfYoutube()
                result_of_youtube.set_error(error_info)
                return result_of_youtube
        single_media = self._get_media(meta_data)
        return ResultOfYoutube(single_media)

    def verify_local_files(self, dirPath: str, easy_id3_manager_class: EasyID3Manager):
        """Method verifies if the local files still exists on YouTube

        Args:
            dirPath (str): path to file directory

        Returns:
            list: List of files which weren't verified, so those which are no longer present on YouTube
        """
        not_verified_files = []
        list_of_files = os.listdir(dirPath)
        for file_name in list_of_files:
            full_file_path = os.path.join(dirPath, file_name)
            if not os.path.isfile(
                    full_file_path) or not full_file_path.endswith(".mp3"):
                continue
            audio_manager = easy_id3_manager_class(full_file_path)
            audio_manager.read_meta_data()
            if not self.if_video_exist_on_youtube(audio_manager.website):
                not_verified_files.append(full_file_path)
        return not_verified_files

    def if_query_exist_on_youtube(self, yt_hash: str):  # pragma: no_cover
        """Method checks if given query exists on YouTube, methos uses yt-dlp package

        Args:
            yt_hash (str): query for to search YouTube

        Returns:
            bool: True if video exists, False if video not exists on YouTube
        """

        ydl_opts = VideoVerificationOptiones().to_dict()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info(yt_hash, download=False)
                logger.error(f"Video with {yt_hash} exists on YouTube")
                return True
            except Exception as exception:
                error_info = str(exception)
                logger.error(
                    f"Video might be deleted from YouTube error: {error_info}")
                return False

    def if_video_exist_on_youtube(self, yt_hash: str):  # pragma: no_cover
        """Method checks if given YouTube video hash exists on YouTube, methos uses yt-dlp package

        Args:
            yt_hash (str): YouTube video hash for YouTube search

        Returns:
            bool: True if video exists, False if video not exists on YouTube
        """

        ydl_opts = VideoVerificationOptiones().to_dict()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info(yt_hash, download=False)
                logger.error(f"Video with {yt_hash} exists on YouTube")
                return True
            except Exception as exception:
                error_info = str(exception)
                logger.error(
                    f"Video might be deleted from YouTube error: {error_info}")
                return False

    def _get_media(self, meta_data):
        """Method sets and returns SingleMedia instance based on meta data inptu

        Args:
            meta_data (dict): meta data dict

        Returns:
            SingleMedia : SingleMedia instance with all the info set up
        """
        full_path = title = album = youtube_hash = artist = url = extension = ""
        if MediaInfo.TITLE.value in meta_data:
            title = yt_dlp.utils.sanitize_filename(
                meta_data[MediaInfo.TITLE.value])
        if MediaInfo.ALBUM.value in meta_data:
            album = meta_data[MediaInfo.ALBUM.value]
        if MediaInfo.ARTIST.value in meta_data:
            artist = meta_data[MediaInfo.ARTIST.value]
        if MediaInfo.YOUTUBE_HASH.value in meta_data:
            youtube_hash = meta_data[MediaInfo.YOUTUBE_HASH.value]
        if MediaInfo.URL.value in meta_data:
            url = meta_data[MediaInfo.URL.value]
        if MediaInfo.EXTENSION.value in meta_data:
            extension = meta_data[MediaInfo.EXTENSION.value]
        if MainYoutubeKeys.REQUESTED_DOWNLOADS.value in meta_data:
            requested_downloads = meta_data[MainYoutubeKeys.REQUESTED_DOWNLOADS.value][0]
            if MainYoutubeKeys.FUL_PATH.value in requested_downloads:
                full_path = requested_downloads[MainYoutubeKeys.FUL_PATH.value]
        return SingleMedia(full_path, title, album, artist,
                           youtube_hash, url, extension)

    def _get_playlist_media(self, meta_data) -> PlaylistMedia:
        """Method sets and returns PlaylistMedia instance based on meta data inptu

        Args:
            meta_data (dict): meta data dict

        Returns:
            PlaylistMedia: PlaylistMedia instance with all the info set up
        """
        media_info_list = []
        playlist_name = ""
        if PlaylistInfo.TITLE.value in meta_data:
            playlist_name = meta_data[PlaylistInfo.TITLE.value]
        for track in meta_data[PlaylistInfo.PLAYLIST_TRACKS.value]:
            if track is None:
                continue
            title = youtube_hash = ""
            if PlaylistInfo.TITLE.value in track:
                title = yt_dlp.utils.sanitize_filename(
                    track[PlaylistInfo.TITLE.value])
            if PlaylistInfo.URL.value in track:
                youtube_hash = track[PlaylistInfo.URL.value]
            media_from_playlist_struct = MediaFromPlaylist(
                title, youtube_hash)
            media_info_list.append(media_from_playlist_struct)
        return PlaylistMedia(playlist_name, media_info_list)

    def _get_video_options(self, type: str):
        """Method used to change and set proper

        Args:
            type (str): _description_
        """
        out_template = self._savePath + \
            self.title_template + f"_{type}p" + ".%(ext)s"
        video_options_instance = YoutubeVideoOptions(out_template)
        video_quality = video_options_instance.convert_video_quality(type)
        video_options_instance.change_format(video_quality=video_quality)
        return video_options_instance.to_dict()

    def _get_audio_options(self):
        """Method sets audio options
        """
        out_template = self._savePath + \
            f"{self.title_template}.%(ext)s"
        audio_options_instance = YoutubeAudioOptions(out_template)
        return audio_options_instance.to_dict()

    def _get_media_result_hash(self, url):
        """Method extracts single video hash from full url

        Args:
            url (str): full YouTube URL

        Raises:
            ValueError: ValueError if the URL is a playlist only

        Returns:
            str: single video hash
        """
        number_of_equal_sign = url.count("=")
        if number_of_equal_sign == 0:
            return url
        only_hashes_in_link = url.split("?")[1]
        splited_hashes = only_hashes_in_link.split("=")
        if number_of_equal_sign == 1:
            if "list=" in only_hashes_in_link:
                raise ValueError(
                    "This a playlist only - without video hash to download")
            else:
                media_hash = only_hashes_in_link[2:]
                return media_hash
        elif number_of_equal_sign > 2:
            media_hash = splited_hashes[1][:splited_hashes[1].index("&")]
            return media_hash
        elif number_of_equal_sign == 2:
            media_hash = splited_hashes[1][:splited_hashes[1].index("&")]
            return media_hash

    def _get_playlist_hash(self, url):
        """Method extracts playlist hash from full url

        Args:
            url (str): full YouTube URL

        Raises:
            ValueError: ValueError if the URL is not a playlist

        Returns:
            str: playlist hash
        """
        if "list=" not in url:
            raise ValueError("This is not a playlist")
        only_hashes_in_link = url.split("?")[1]
        number_of_equal_sign = url.count("=")
        splited_hashes = only_hashes_in_link.split("=")
        if number_of_equal_sign == 1:
            playlist_hash = only_hashes_in_link[5:]
            return playlist_hash
        elif number_of_equal_sign > 2:
            playlist_hash = splited_hashes[2][:splited_hashes[2].index("&")]
            return playlist_hash
        elif number_of_equal_sign == 2:
            playlist_hash = splited_hashes[2]
            return playlist_hash

    def set_title_template_one_time(self, newTitileTemplate):
        self.title_template = newTitileTemplate


class YoutubeDlPlaylists(YoutubeDL):
    def __init__(self, configManager: BaseConfigParser,
                 easy_id3_manager: EasyID3Manager,
                 ytLogger: LoggerClass = Logger):
        super().__init__(configManager, ytLogger)
        self.easy_id3_manager = easy_id3_manager

    def download_whole_audio_playlist(self, youtubeURL: str):
        """Method uded to download audio playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube audio playlist meta data
        """
        playlist_hash = self._get_playlist_hash(youtubeURL)
        ydl_opts = self._get_audio_options()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                meta_data = ydl.extract_info(playlist_hash)
            except Exception as exception:
                error_info = str(exception)
                logger.error(f"Download media info error {error_info}")
                return False
        entries_key = PlaylistInfo.PLAYLIST_TRACKS.value
        if entries_key not in meta_data:
            logger.error(
                "Playlist dosn't have track list - no entries key in meta data")
            return False
        playlist_name = meta_data[PlaylistInfo.TITLE.value]
        for playlistTrack in meta_data[entries_key]:
            if playlistTrack is None:
                logger.info("Track Not Found")
                continue
            directory_path = self._configManager.get_save_path()
            title = artist = album = index = None
            if PlaylistInfo.TITLE.value in playlistTrack:
                title = playlistTrack[PlaylistInfo.TITLE.value]
            if PlaylistInfo.ARTIST.value in playlistTrack:
                artist = playlistTrack[PlaylistInfo.ARTIST.value]
            if PlaylistInfo.ALBUM.value in playlistTrack:
                album = playlistTrack[PlaylistInfo.TITLE.value]
            if PlaylistInfo.PLAYLIST_INDEX.value in playlistTrack:
                index = playlistTrack[PlaylistInfo.PLAYLIST_INDEX.value]
            file_path = f"{directory_path}/{yt_dlp.utils.sanitize_filename(playlistTrack['title'])}.mp3"
            self.easy_id3_manager.setParams(file_path=file_path,
                                            title=title,
                                            album=album,
                                            artist=artist,
                                            playlist_name=playlist_name,
                                            track_number=index)
            self.easy_id3_manager.save_meta_data()
        return meta_data

    def download_whole_video_playlist(self, youtubeURL: str, type: str):
        """Method uded to download video playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video playlist meta data
        """
        ydl_opts = self._get_video_options(type)
        playlist_hash = self._get_playlist_hash(youtubeURL)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                meta_data = ydl.extract_info(playlist_hash)
            except Exception as exception:
                error_info = str(exception)
                logger.error(f"Download media info error {error_info}")
                return False
        return meta_data

    def downolad_all_config_playlists_video(self, type):
        """Method used to download all playlists added to cofig file - type video

        Args:
            type (str): type of the video to download, like 480p

        Returns:
            bool: True if finished successfully
        """
        playlist_list = self._configManager.get_url_of_playlists()
        for playlist_url in playlist_list:
            self.download_whole_video_playlist(playlist_url, type)
        return True

    def downolad_all_config_playlists_audio(self):
        """Method used to download all playlists added to cofig file - type audo

        Returns:
            bool: True if finished successfully
        """
        playlist_list = self._configManager.get_url_of_playlists()
        for playlist_url in playlist_list:
            self.download_whole_audio_playlist(playlist_url)
        return True
