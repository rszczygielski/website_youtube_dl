from enum import Enum

class MetaDataType(Enum):
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"
    TRACK_NUMBER = "tracknumber"
    PLAYLIST_NAME = "playlist_name"
    WEBSITE = "website"


class PlaylistInfo(Enum):
    PLAYLIST_NAME = "playlist_name"
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"
    YOUTUBE_HASH = "id"
    PLAYLIST_TRACKS = "entries"
    URL = "url"
    EXTENSION = "ext"

class MediaInfo(Enum):
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    YOUTUBE_HASH = "id"
    URL = "webpage_url"
    EXTENSION = "ext"

class YoutubeOptiones(Enum):
    FORMAT = "format"
    DOWNLOAD_ARCHIVE = "download_archive"
    NO_OVERRIDE = "no-overwrites"
    ADD_META_DATA = "addmetadata"
    IGNORE_ERRORS = "ignoreerrors"
    QUIET = "quiet"
    LOGGER = "logger"
    OUT_TEMPLATE = "outtmpl"


