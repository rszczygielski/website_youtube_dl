from enum import Enum

class EmitMessages(Enum):
    DOWNLOAD_MEDIA_FINISH = "downloadMediaFinish"
    MEDIA_INFO = "mediaInfo"
    PLAYLIST_MEDIA_INFO = "playlistMediaInfo"
    UPLOAD_PLAYLISTS = "uploadPlalists"
    PLAYLIST_URL = "playlistUrl"

class EmitAttributes(Enum):
    DATA = "data"
    HASH = "HASH"
    ERROR = "error"
    PLAYLIST_NAME = "playlistName"
    TRACK_LIST = "trackList"
    PLAYLIST_LIST = "plalistList"
