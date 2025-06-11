import logging
from ..common.youtubeLogKeys import YoutubeLogs
from ..common.youtubeAPI import SingleMedia
from ..common.youtubeDL import YoutubeDL
from ..common.easyID3Manager import EasyID3Manager
from ..common.youtubeConfigManager import BaseConfigParser
from ..common.myLogger import LoggerClass
from ..common.youtubeAPI import FormatMP3
logger = logging.getLogger(__name__)


class YoutubeHelper():
    def __init__(self, config_parser: BaseConfigParser):
        youtube_logger = LoggerClass()
        self.config_parser_manager = config_parser

        self.youtube_downloder = YoutubeDL(
            self.config_parser_manager, youtube_logger)

    def get_youtube_downloader_instance(self):
        return self.youtube_downloder

    def download_single_video(self, single_media_url: str,
                              req_format):
        youtube_options = self.get_youtube_download_options(req_format)
        single_media_info_result = self.youtube_downloder.download_yt_media(
            single_media_url, youtube_options)
        if single_media_info_result.is_error():
            error_msg = single_media_info_result.get_error_info()
            logger.error(
                f"{YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value}: {error_msg}")
            return None
        singleMedia: SingleMedia = single_media_info_result.get_data()
        directory_path = self.config_parser_manager.get_save_path()
        logger.info(
            f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {singleMedia.file_path}")
        logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directory_path}")
        return singleMedia.file_path

    def download_single_audio(self, single_media_url: str,
                              req_format):
        youtube_options = self.get_youtube_download_options(req_format)
        single_media_info_result = self.youtube_downloder.download_yt_media(
            single_media_url, youtube_options)
        if single_media_info_result.is_error():
            error_msg = single_media_info_result.get_error_info()
            logger.error(
                f"{YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value}: {error_msg}")
            return None
        singleMedia: SingleMedia = single_media_info_result.get_data()
        directory_path = self.config_parser_manager.get_save_path()
        singleMedia.file_path = str(
            singleMedia.file_path).replace(".webm", ".mp3")\
                                  .replace(".mp4", ".mp3")
        easy_id3_manager = EasyID3Manager()
        easy_id3_manager.set_params(filePath=singleMedia.file_path,
                                    title=singleMedia.title,
                                    album=singleMedia.album,
                                    artist=singleMedia.artist,
                                    yt_hash=singleMedia.yt_hash)
        easy_id3_manager.save_meta_data()
        logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_path}")
        logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directory_path}")
        return singleMedia.file_path

    def download_audio_from_playlist(self, single_media_url: str,
                                     req_format,
                                     playlist_name: str,
                                     index: str):
        youtube_options = self.get_youtube_download_options(req_format)
        single_media_info_result = self.youtube_downloder.download_yt_media(
            single_media_url, youtube_options)
        if single_media_info_result.is_error():
            error_msg = single_media_info_result.get_error_info()
            logger.error(
                f"{YoutubeLogs.MEDIA_INFO_DOWNLOAD_ERROR.value}: {error_msg}")
            return None
        singleMedia: SingleMedia = single_media_info_result.get_data()
        singleMedia.file_path = str(
            singleMedia.file_path).replace(
            ".webm", ".mp3")
        easy_id3_manager = EasyID3Manager()
        easy_id3_manager.set_params(filePath=singleMedia.file_path,
                                    title=singleMedia.title,
                                    album=playlist_name,
                                    artist=singleMedia.artist,
                                    yt_hash=singleMedia.yt_hash,
                                    track_number=index)
        easy_id3_manager.save_meta_data()
        logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_path}")
        return singleMedia.file_path

    def get_youtube_download_options(self, req_format):
        if isinstance(req_format, FormatMP3):
            options_instance = self.youtube_downloder._get_audio_options()
        else:
            video_type = req_format.get_format_type()
            options_instance = self.youtube_downloder._get_video_options(
                video_type)
        return options_instance

    def request_single_media_info(self, single_media_url):
        return self.youtube_downloder.request_single_media_info(single_media_url)

    def request_playlist_media_info(self, playlist_url):
        return self.youtube_downloder.request_playlist_media_info(playlist_url)

    def set_title_template(self, title_template):
        self.youtube_downloder.set_title_template_one_time(
            title_template)
