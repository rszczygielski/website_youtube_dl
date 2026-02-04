from enum import Enum


class YoutubeLogs(Enum):
    """Enumeration of log message strings for YouTube operations.
    
    Contains standardized log messages used throughout the application
    for logging YouTube download operations, errors, and status updates.
    
    Attributes:
        MEDIA_INFO_DOWNLOAD_ERROR (str): Error message for media info download failures.
        PLAYLIST_INFO_DOWNLAOD_ERROR (str): Error message for playlist info download failures.
        DIRECTORY_PATH (str): Log message for directory path information.
        DOWNLAOD_PLAYLIST (str): Log message for playlist download start.
        DOWNLOAD_SINGLE_VIDEO (str): Log message for single video download start.
        VIDEO_DOWNLOADED (str): Log message for successful video download.
        AUDIO_DOWNLOADED (str): Log message for successful audio download.
        PLAYLIST_DOWNLAODED (str): Log message for successful playlist download.
        PLAYLIST_DOWNLAODED_CONFIG (str): Log message for config playlist download.
        NO_FORMAT (str): Error message when format is not specified.
        SPECIFIED_FORMAT (str): Log message for specified format.
        NO_URL (str): Error message when YouTube URL is empty.
        SENDING_TO_ATTACHMENT (str): Log message for sending file as attachment.
        FLASH_CONFIG_PALYLIST (str): Log message when all config playlists are downloaded.
        PLAYLIST_AND_VIDEO_HASH_IN_URL (str): Warning message when both playlist and video detected in URL.
    """
    MEDIA_INFO_DOWNLOAD_ERROR = "Download media info error"
    PLAYLIST_INFO_DOWNLAOD_ERROR = "Download playlist info error"
    DIRECTORY_PATH = "Direcotry path"
    DOWNLAOD_PLAYLIST = "Download playlist"
    DOWNLOAD_SINGLE_VIDEO = "Download single video"
    VIDEO_DOWNLOADED = "Video file donwloaded"
    AUDIO_DOWNLOADED = "Audio file donwloaded"
    PLAYLIST_DOWNLAODED = "Playlist donwloaded"
    PLAYLIST_DOWNLAODED_CONFIG = "Config playlist downloaded"
    NO_FORMAT = "Format not specified"
    SPECIFIED_FORMAT = "Specified format"
    NO_URL = "Youtube URL empty"
    SENDING_TO_ATTACHMENT = "Sending file to download as a attachment"
    FLASH_CONFIG_PALYLIST = "All config playlist has been downloaded"
    PLAYLIST_AND_VIDEO_HASH_IN_URL = "Playlist detected and video deceted, don't want what to do"
