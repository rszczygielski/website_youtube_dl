from enum import Enum, auto

class MetaDataType(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'
    PLAYLIST_INDEX = 'playlist_index'

class PlaylistInfo(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'
    PLAYLIST_INDEX = 'playlist_index'
    YOUTUBE_HASH = 'id'
    PLAYLIST_TRACKS = 'entries'
    URL = 'original_url'

class MediaInfo(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'
    YOUTUBE_HASH = 'id'
    URL = 'original_url'

class YoutubeOptiones(Enum):
    FORMAT = "format"
    DOWNLOAD_ARCHIVE = 'downloaded_songs.txt'
    NO_OVERRIDE = "no-override"
    ADD_META_DATA = "addmetadata"
    IGNORE_ERRORS = "ignoreerrors"
    QIET = "quiet"
    LOGGER = "logger"
    OUT_TEMPLATE = "outtmpl"

class YoutubeDlStructure():

    def __init__(self) -> None:
        pass
