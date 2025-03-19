from enum import Enum


class YoutubeLogs(Enum):
    MEDIA_INFO_DOWNLAOD_ERROR = "Download media info error"
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