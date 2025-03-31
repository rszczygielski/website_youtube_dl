import logging
from ..common.youtubeLogKeys import YoutubeLogs
from ..common.youtubeDL import SingleMedia, YoutubeDL
from ..common.easyID3Manager import EasyID3Manager
from ..common.youtubeConfigManager import ConfigParserManager
from ..common.myLogger import LoggerClass


logger = logging.getLogger(__name__)


class YoutubeHelper():
    def __init__(self):
        youtube_logger = LoggerClass()
        self.config_parser_manager = ConfigParserManager()

        self.youtube_downloder = YoutubeDL(
            self.config_parser_manager, youtube_logger)

    def get_youtube_downloader_instance(self):
        return self.youtube_downloder

    def download_single_video(self, single_media_url, video_type):
        # if send_full_emit:
        #     if not send_emit_single_media_info_from_youtube(single_media_url):
        #         return None
        single_media_info_result = self.youtube_downloder.download_video(
            single_media_url, video_type)
        if single_media_info_result.is_error():
            error_msg = single_media_info_result.get_error_info()
            # handle_error(error_msg)
            return None
        singleMedia: SingleMedia = single_media_info_result.get_data()
        directory_path = self.config_parser_manager.get_save_path()
        logger.info(
            f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {singleMedia.file_name}")
        logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directory_path}")
        return singleMedia.file_name

    def download_single_audio(self, single_media_url):
        # if not send_emit_single_media_info_from_youtube(single_media_url):
        #     return None
        single_media_info_result = self.youtube_downloder.download_audio(
            single_media_url)
        if single_media_info_result.is_error():
            error_msg = single_media_info_result.get_error_info()
            # handle_error(error_msg)
            return None
        singleMedia: SingleMedia = single_media_info_result.get_data()
        directory_path = self.config_parser_manager.get_save_path()
        singleMedia.file_name = str(
            singleMedia.file_name).replace(
            ".webm", ".mp3")
        easy_id3_manager = EasyID3Manager()
        easy_id3_manager.set_params(filePath=singleMedia.file_name,
                                    title=singleMedia.title,
                                    album=singleMedia.album,
                                    artist=singleMedia.artist,
                                    yt_hash=singleMedia.yt_hash)
        easy_id3_manager.save_meta_data()
        logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
        logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directory_path}")
        return singleMedia.file_name

    def download_audio_from_playlist(self, single_media_url, playlist_name, index):
        single_media_info_result = self.youtube_downloder.download_audio(
            single_media_url)
        if single_media_info_result.is_error():
            error_msg = single_media_info_result.get_error_info()
            # handle_error(error_msg)
            return None
        singleMedia: SingleMedia = single_media_info_result.get_data()
        singleMedia.file_name = str(
            singleMedia.file_name).replace(
            ".webm", ".mp3")
        easy_id3_manager = EasyID3Manager()
        easy_id3_manager.set_params(filePath=singleMedia.file_name,
                                    title=singleMedia.title,
                                    album=playlist_name,
                                    artist=singleMedia.artist,
                                    yt_hash=singleMedia.yt_hash,
                                    track_number=index)
        easy_id3_manager.save_meta_data()
        logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
        return singleMedia.file_name
