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
                             VideoVerificationOptiones,
                             VideoExtension)
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from website_youtube_dl.common.youtubeAPI import (SingleMedia,
                                                  MediaFromPlaylist,
                                                  PlaylistMedia,
                                                  ResultOfYoutube)


logger = logging.getLogger(__name__)


class YoutubeDL():
    """Main class for YouTube media downloading operations.
    
    Provides functionality to download single media items and playlists
    from YouTube, extract metadata, and verify video existence. Uses
    yt-dlp library for actual downloading operations.
    
    Attributes:
        title_template_default (str): Default output template for file names.
        title_template (str): Current output template (can be modified temporarily).
        _configManager (BaseConfigParser): Configuration manager instance.
        yt_logger (LoggerClass): Logger instance for logging operations.
        _savePath (str): Path where downloaded files are saved.
        _ydl_opts (YoutubeDefaultOptiones): Default download options.
        _ydl_single_info_opts (YoutubeGetSingleInfoOptiones): Options for single media info.
        _ydl_playlist_info_opts (YoutubeGetPlaylistInfoOptiones): Options for playlist info.
    """
    title_template_default = "/%(title)s"
    title_template = title_template_default

    def __init__(
            self,
            configManager: BaseConfigParser,
            ytLogger: LoggerClass = logger):
        """Initialize YoutubeDL with configuration manager and logger.
        
        Args:
            configManager (BaseConfigParser): Configuration manager for
                accessing save paths and settings.
            ytLogger (LoggerClass, optional): Logger instance. Defaults to
                standard logger.
        """
        self._configManager = configManager
        self.yt_logger = ytLogger
        self._savePath = self._configManager.get_save_path()
        self._ydl_opts = YoutubeDefaultOptiones()
        self._ydl_single_info_opts = YoutubeGetSingleInfoOptiones()
        self._ydl_playlist_info_opts = YoutubeGetPlaylistInfoOptiones()

    def download_yt_media(self, youtubeURL: str,
                          options) -> ResultOfYoutube:
        """Download media from YouTube using specified options.

        Args:
            youtubeURL (str): YouTube URL of the media to download.
            options: Download options (YoutubeAudioOptions, YoutubeVideoOptions, etc.).

        Returns:
            ResultOfYoutube: Result object containing media metadata or error information.
        """
        media_hash = self._get_media_result_hash(youtubeURL)
        result_of_youtube = self._download_file(media_hash, options)
        if result_of_youtube.is_error():
            error_msg = result_of_youtube.get_error_info()
            logger.error(f"Download media info error: {error_msg}")
            return result_of_youtube
        return result_of_youtube

    def request_playlist_media_info(self, youtubeURL) -> ResultOfYoutube:
        """Request playlist metadata from YouTube without downloading.

        Args:
            youtubeURL (str): YouTube playlist URL.

        Returns:
            ResultOfYoutube: Result object containing PlaylistMedia with
                playlist name and track list, or error information.
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
        """Request single media metadata from YouTube without downloading.

        Args:
            youtubeURL (str): YouTube URL of the media.

        Returns:
            ResultOfYoutube: Result object containing SingleMedia with
                metadata, or error information.
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

    def verify_local_mp3_files(self, dirPath: str, easy_id3_manager_class: EasyID3Manager):
        """Verify if local MP3 files still exist on YouTube.

        Scans a directory for MP3 files, reads their ID3 metadata to get
        YouTube URLs, and checks if those videos still exist on YouTube.

        Args:
            dirPath (str): Path to directory containing MP3 files.
            easy_id3_manager_class (EasyID3Manager): EasyID3Manager class
                or instance for reading metadata.

        Returns:
            list: List of file paths for files that no longer exist on YouTube.
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
        """Check if a given query/search term exists on YouTube.

        Uses yt-dlp to attempt to extract information for the query.
        This method can be used with search queries, not just video URLs.

        Args:
            yt_hash (str): Query string or YouTube URL to search for.

        Returns:
            bool: True if the query returns valid results, False otherwise.
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
        """Check if a YouTube video exists on YouTube.

        Uses yt-dlp to verify if a video with the given hash/ID still exists
        on YouTube. Useful for verifying that downloaded videos haven't been
        removed.

        Args:
            yt_hash (str): YouTube video ID or hash.

        Returns:
            bool: True if video exists, False if video not found or deleted.
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

    def _download_file(self, single_media_hash: str, ydl_opts=None):
        """Download YouTube media file using yt-dlp.

        Internal method that performs the actual download operation using
        yt-dlp. Resets title_template to default after download.

        Args:
            single_media_hash (str): YouTube video ID or URL.
            ydl_opts: Optional download options. If None, uses default options.

        Returns:
            ResultOfYoutube: Result object containing SingleMedia with
                file path and metadata, or error information.
        """
        if ydl_opts is None:
            ydl_opts = self._ydl_opts.to_dict()
        else:
            ydl_opts = ydl_opts.to_dict()
        logger.debug(f"Using YouTube DL options: {ydl_opts}")
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

    def _get_media(self, meta_data):
        """Extract media information and create SingleMedia instance.

        Parses yt-dlp metadata dictionary and extracts relevant information
        including title, album, artist, YouTube hash, URL, extension, and
        file path. Handles post-processing to get correct file extension.

        Args:
            meta_data (dict): Metadata dictionary from yt-dlp extract_info().

        Returns:
            SingleMedia: SingleMedia instance with all extracted information.
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
                # Extract actual extension from full_path (after postprocessing)
                # This ensures correct extension for audio files converted to mp3
                if full_path and os.path.splitext(full_path)[1]:
                    actual_extension = os.path.splitext(full_path)[1][1:]
                    if actual_extension:
                        extension = actual_extension
        logger.debug(f"Full path: {full_path}")
        logger.debug(f"Title: {title}")
        logger.debug(f"Album: {album}")
        logger.debug(f"Artist: {artist}")
        logger.debug(f"Youtube hash: {youtube_hash}")
        logger.debug(f"Url: {url}")
        logger.debug(f"Extension: {extension}")
        return SingleMedia(full_path, title, album, artist,
                           youtube_hash, url, extension)

    def _get_playlist_media(self, meta_data) -> PlaylistMedia:
        """Extract playlist information and create PlaylistMedia instance.

        Parses yt-dlp playlist metadata dictionary and extracts playlist name
        and all tracks, creating MediaFromPlaylist instances for each track.

        Args:
            meta_data (dict): Metadata dictionary from yt-dlp extract_info()
                for a playlist.

        Returns:
            PlaylistMedia: PlaylistMedia instance with playlist name and
                list of tracks.
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
        """Create video download options for specified quality.

        Creates YoutubeVideoOptions instance configured for the specified
        video quality (e.g., "720", "1080") with MP4 extension and
        appropriate output template.

        Args:
            type (str): Video quality string (e.g., "720", "1080", "480").

        Returns:
            YoutubeVideoOptions: Configured video options instance.
        """
        out_template = self._savePath + \
            self.title_template + f"_{type}p" + ".%(ext)s"
        video_options_instance = YoutubeVideoOptions(out_template)
        video_quality = video_options_instance.convert_video_quality(type)
        video_extension = VideoExtension.MP4
        video_options_instance.set_format(video_quality=video_quality,
                                          extension=video_extension)
        return video_options_instance

    def _get_audio_options(self):
        """Create audio download options.

        Creates YoutubeAudioOptions instance configured for MP3 audio
        extraction with appropriate output template.

        Returns:
            YoutubeAudioOptions: Configured audio options instance.
        """
        out_template = self._savePath + \
            f"{self.title_template}.%(ext)s"
        audio_options_instance = YoutubeAudioOptions(out_template)
        return audio_options_instance

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
        """Set a custom title template for the next download.

        Temporarily overrides the default title template. The template
        will be reset to default after the next download operation.

        Args:
            newTitileTemplate (str): New output template string (e.g., "/%(title)s").
        """
        self.title_template = newTitileTemplate


class YoutubeDlPlaylists(YoutubeDL):
    """Extended YouTube downloader with playlist-specific functionality.
    
    Extends YoutubeDL to provide methods for downloading entire playlists
    (both audio and video) and managing ID3 metadata for downloaded tracks.
    
    Attributes:
        easy_id3_manager (EasyID3Manager): Manager for ID3 metadata operations.
    """
    
    def __init__(self, configManager: BaseConfigParser,
                 easy_id3_manager: EasyID3Manager,
                 ytLogger: LoggerClass = Logger):
        """Initialize YoutubeDlPlaylists with config manager and ID3 manager.
        
        Args:
            configManager (BaseConfigParser): Configuration manager instance.
            easy_id3_manager (EasyID3Manager): EasyID3Manager instance for
                metadata operations.
            ytLogger (LoggerClass, optional): Logger instance. Defaults to Logger.
        """
        super().__init__(configManager, ytLogger)
        self.easy_id3_manager = easy_id3_manager

    def download_whole_audio_playlist(self, youtubeURL: str):
        """Download entire audio playlist from YouTube as MP3 files.

        Downloads all tracks from a playlist, converts them to MP3, and
        adds ID3 metadata including title, artist, album, playlist name,
        and track number.

        Args:
            youtubeURL (str): YouTube playlist URL.

        Returns:
            dict: Metadata dictionary from yt-dlp, or False on error.
        """
        playlist_hash = self._get_playlist_hash(youtubeURL)
        audio_options = self._get_audio_options()
        ydl_opts = audio_options.to_dict()
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
        """Download entire video playlist from YouTube.

        Downloads all videos from a playlist at the specified quality.

        Args:
            youtubeURL (str): YouTube playlist URL.
            type (str): Video quality string (e.g., "720", "1080", "480").

        Returns:
            dict: Metadata dictionary from yt-dlp, or False on error.
        """
        video_options = self._get_video_options(type)
        ydl_opts = video_options.to_dict()
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
        """Download all playlists from configuration file as video.

        Iterates through all playlists defined in the configuration file
        and downloads them as video files at the specified quality.

        Args:
            type (str): Video quality type (e.g., "480p", "720p", "1080p").

        Returns:
            bool: True when all playlists have been processed.
        """
        playlist_list = self._configManager.get_url_of_playlists()
        for playlist_url in playlist_list:
            self.download_whole_video_playlist(playlist_url, type)
        return True

    def downolad_all_config_playlists_audio(self):
        """Download all playlists from configuration file as audio.

        Iterates through all playlists defined in the configuration file
        and downloads them as MP3 audio files with ID3 metadata.

        Returns:
            bool: True when all playlists have been processed.
        """
        playlist_list = self._configManager.get_url_of_playlists()
        for playlist_url in playlist_list:
            self.download_whole_audio_playlist(playlist_url)
        return True
