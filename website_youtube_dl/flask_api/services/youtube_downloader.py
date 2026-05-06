import os
import logging
from ...common.youtube_log_keys import YoutubeLogs
from ...common.youtube_api import SingleMedia, FormatMP3
from ...common.youtube_dl import YoutubeDL
from ...common.easyID3_manager import EasyID3Manager
from ...common.youtube_config_manager import BaseConfigParser
from ...common.my_logger import LoggerClass
from ..utils.general_funcions import zip_all_files_in_list, generate_title_template_for_youtube_downloader

logger = logging.getLogger(__name__)


class BaseYoutubeDownloader:
    """
    Base service handling the core mechanics of downloading and tagging single media files.

    This class manages the configuration and direct interaction with YoutubeDL
    and EasyID3Manager. It does not handle batch processes like playlists.
    """

    def __init__(self, config_parser: BaseConfigParser):
        """
        Initialize the core service.

        Args:
            config_parser (BaseConfigParser): Manager providing paths and configs.
        """
        self.config_parser_manager = config_parser
        youtube_logger = LoggerClass()
        self.youtube_downloader = YoutubeDL(self.config_parser_manager, youtube_logger)

    def download_single_track(self, youtube_url: str, req_format):
        """
        Route a single media download request to the appropriate audio/video handler.
        """
        logger.info(f"Processing single track URL: {youtube_url}")

        if isinstance(req_format, FormatMP3):
            return self._download_and_tag_audio(youtube_url, req_format)
        else:
            return self.download_single_video(youtube_url, req_format)

    def download_single_video(self, single_media_url: str, req_format):
        """
        Download a video file without applying audio metadata.
        """
        youtube_options = self._get_youtube_download_options(req_format)
        result = self.youtube_downloader.download_yt_media(single_media_url, youtube_options)

        if result.is_error():
            logger.error(f"{YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value}: {result.get_error_info()}")
            return None

        singleMedia: SingleMedia = result.get_data()
        logger.info(f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {singleMedia.file_path}")

        return singleMedia.file_path

    def _download_and_tag_audio(
        self, single_media_url: str, req_format,
        playlist_name: str = None, track_index: str = None
        ):
        """
        Download an audio file and inject ID3 metadata tags.
        Can be used for isolated singles or tracks belonging to a larger playlist.
        """
        youtube_options = self._get_youtube_download_options(req_format)
        result = self.youtube_downloader.download_yt_media(single_media_url, youtube_options)

        if result.is_error():
            logger.error(f"{YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value}: {result.get_error_info()}")
            return None

        singleMedia: SingleMedia = result.get_data()

        # Fallback to the media's default album if no playlist name is provided
        album_name = playlist_name if playlist_name else singleMedia.album

        easy_id3_manager = EasyID3Manager()
        easy_id3_manager.set_params(
            filePath=singleMedia.file_path,
            title=singleMedia.title,
            album=album_name,
            artist=singleMedia.artist,
            yt_hash=singleMedia.yt_hash,
            track_number=track_index
        )
        easy_id3_manager.save_meta_data()

        logger.info(f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_path}")
        return singleMedia.file_path

    def _get_youtube_download_options(self, req_format):
        """Extract the specific download parameters based on the requested format."""
        if isinstance(req_format, FormatMP3):
            return self.youtube_downloader._get_audio_options()
        else:
            video_type = req_format.get_format_type()
            return self.youtube_downloader._get_video_options(video_type)

    def request_single_media_info(self, single_media_url):
        return self.youtube_downloader.request_single_media_info(single_media_url)

    def request_playlist_media_info(self, playlist_url):
        return self.youtube_downloader.request_playlist_media_info(playlist_url)


class YoutubePlaylistDownloader(BaseYoutubeDownloader):
    """
    Advanced service extending core capabilities to handle batch processes.

    Inherits from BaseYoutubeDownloader and is responsible for orchestrating
    playlist downloads, safe file naming, and generating ZIP archives.
    """

    def __init__(self, config_parser: BaseConfigParser):
        """
        Initialize the playlist service and its inherited core mechanics.
        """
        super().__init__(config_parser)

    def process_playlist_track(
        self, playlistTrack, req_format,
        playlist_name: str, index: int, downloaded_files: list
        ):
        """
        Download a single track as part of a playlist process, applying proper naming.

        Args:
            playlistTrack: Object containing track metadata (title, hash).
            req_format (Format): Requested format (e.g., FormatMP3).
            playlist_name (str): Name of the parent playlist.
            index (int): Track's index in the playlist loop.
            downloaded_files (list): List of existing file names to avoid duplicates.

        Returns:
            tuple: (full_file_path, title_template). Path is None if download fails.
        """
        title = playlistTrack.title
        title_template = generate_title_template_for_youtube_downloader(downloaded_files, title)

        # Accessing the inherited youtube_downloader instance from the parent class
        self.youtube_downloader.set_title_template_one_time(title_template)

        full_path = None
        if isinstance(req_format, FormatMP3):
            logger.debug(f"Downloading audio for track: {title}")
            # Utilizing the protected method from the parent class
            full_path = self._download_and_tag_audio(
                single_media_url=playlistTrack.yt_hash,
                req_format=req_format,
                playlist_name=playlist_name,
                track_index=str(index + 1)
            )
        else:
            logger.debug(f"Downloading video for track: {title}")
            # Utilizing the public method from the parent class
            full_path = self.download_single_video(
                single_media_url=playlistTrack.yt_hash,
                req_format=req_format
            )

        return full_path, title_template

    def zip_downloaded_playlist(self, directory_path, playlist_name, file_paths):
        """
        Compresses a list of downloaded files into a ZIP archive.

        Args:
            directory_path (str): The directory where files are saved.
            playlist_name (str): Name of the playlist (used for the zip filename).
            file_paths (list): List of absolute paths to the downloaded files.

        Returns:
            str: The full absolute path to the generated zip file.
        """
        zip_name_file = zip_all_files_in_list(directory_path, playlist_name, file_paths)
        logger.info(f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlist_name}")
        full_zip_path = os.path.join(directory_path, zip_name_file)

        return full_zip_path