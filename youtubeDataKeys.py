from enum import Enum

class MetaDataType(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'

class PlaylistInfo(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'
    PLAYLIST_INDEX = 'playlist_index'
    YOUTUBE_HASH = 'id'
    PLAYLIST_TRACKS = 'entries'
    URL = 'original_url'