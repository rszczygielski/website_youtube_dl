from enum import Enum, auto

class MetaDataType(Enum):
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"
    TRACK_NUMBER = "tracknumber"

class PlaylistInfo(Enum):
    PLAYLIST_NAME = "playlist_name"
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"
    YOUTUBE_HASH = "id"
    PLAYLIST_TRACKS = "entries"
    URL = "original_url"
    EXTENSION = "ext"

class MediaInfo(Enum):
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    YOUTUBE_HASH = "id"
    URL = "original_url"
    EXTENSION = "ext"

class YoutubeOptiones(Enum):
    FORMAT = "format"
    DOWNLOAD_ARCHIVE = "download_archive"
    NO_OVERRIDE = "no-override"
    ADD_META_DATA = "addmetadata"
    IGNORE_ERRORS = "ignoreerrors"
    QUIET = "quiet"
    LOGGER = "logger"
    OUT_TEMPLATE = "outtmpl"


# w innym pliku enumy do formularzy 

class YoutubeLogs(Enum):
    MEDIA_INFO_DOWNLAOD_ERROR = "Download media info error"
    PLAYLIST_INFO_DOWNLAOD_ERROR = "Download playlist info error"
    DIRECTORY_PATH = "Direcotry path"
    DOWNLAOD_PLAYLIST = "Download playlist"
    DOWNLOAD_SINGLE_VIDEO = "Download single video"
    VIDEO_DOWNLOADED = "Video file donwloaded"
    PLAYLIST_DOWNLAODED = "Playlist donwloaded"
    PLAYLIST_DOWNLAODED_CONFIG = "Config playlist downloaded"
    NO_FORMAT = "Format not specified"
    SPECIFIED_FORMAT = "Specified format"
    NO_URL = "Youtube URL empty"
    SENDING_TO_ATTACHMENT = "Sending file to download as a attachment"
    FLASH_CONFIG_PALYLIST = "All config playlist has been downloaded"
    PLAYLIST_AND_VIDEO_HASH_IN_URL = "Playlist detected and video deceted, don't want what to do"

class YoutubeVariables(Enum):
    DOWNLOAD_FILE_NAME = "downloadFileName"
    DOWNLOAD_DIRECOTRY_PATH = "downloadDirectoryPath"
    YOUTUBE_URL = "youtubeURL"
    DOWNLOAD_TYP = "downloadType"
    EMPTY_STRING = ""
    URL_LIST = "list="
    URL_VIDEO = "v="
    MP3 = "mp3"