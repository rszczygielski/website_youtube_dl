from enum import Enum, auto

class MetaDataType(Enum):
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"

class PlaylistInfo(Enum):
    PLAYLIST_NAME = "playlist_name"
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"
    YOUTUBE_HASH = "id"
    PLAYLIST_TRACKS = "entries"
    URL = "original_url"

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