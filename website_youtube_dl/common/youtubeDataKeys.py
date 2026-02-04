from enum import Enum


class MainYoutubeKeys(Enum):
    """Enumeration of main YouTube-related keys used in the application.
    
    Contains keys used for request/response data structures, file paths,
    and download-related identifiers throughout the application.
    
    Attributes:
        FUL_PATH (str): Key for full file path.
        REQUESTED_DOWNLOADS (str): Key for requested downloads list.
        DOWNLOAD_FILE_NAME (str): Key for download file name.
        DOWNLOAD_DIRECOTRY_PATH (str): Key for download directory path.
        YOUTUBE_URL (str): Key for YouTube URL.
        DOWNLOAD_TYP (str): Key for download type.
        URL_LIST (str): URL parameter for playlist list.
        URL_VIDEO (str): URL parameter for video.
        MP3 (str): MP3 format identifier.
        FORM_DATA (str): Key for form data.
        DATA (str): Key for data payload.
        HASH (str): Key for hash identifier.
        NAME (str): Key for name field.
        ERROR (str): Key for error information.
        ARGS (str): Key for arguments.
    """
    FUL_PATH = "filepath"
    REQUESTED_DOWNLOADS = "requested_downloads"
    DOWNLOAD_FILE_NAME = "downloadFileName"
    DOWNLOAD_DIRECOTRY_PATH = "downloadDirectoryPath"
    YOUTUBE_URL = "youtubeURL"
    DOWNLOAD_TYP = "downloadType"
    URL_LIST = "list="
    URL_VIDEO = "v="
    MP3 = "mp3"
    FORM_DATA = "FormData"
    DATA = "data"
    HASH = "HASH"
    NAME = "name"
    ERROR = 'error'
    ARGS = "args"


class MetaDataType(Enum):
    """Enumeration of metadata type keys for audio file tags.
    
    Contains keys used for ID3 metadata tags in MP3 files, including
    title, album, artist, track information, and playlist details.
    
    Attributes:
        TITLE (str): Key for track title.
        ALBUM (str): Key for album name.
        ARTIST (str): Key for artist name.
        PLAYLIST_INDEX (str): Key for playlist index position.
        TRACK_NUMBER (str): Key for track number.
        PLAYLIST_NAME (str): Key for playlist name.
        WEBSITE (str): Key for website/URL information.
    """
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"
    TRACK_NUMBER = "tracknumber"
    PLAYLIST_NAME = "playlistName"
    WEBSITE = "website"


class PlaylistInfo(Enum):
    """Enumeration of playlist information keys from YouTube API.
    
    Contains keys used to extract playlist and track information from
    YouTube API responses when processing playlists.
    
    Attributes:
        PLAYLIST_NAME (str): Key for playlist name.
        TITLE (str): Key for track title.
        ALBUM (str): Key for album name.
        ARTIST (str): Key for artist name.
        PLAYLIST_INDEX (str): Key for track index in playlist.
        YOUTUBE_HASH (str): Key for YouTube video ID.
        PLAYLIST_TRACKS (str): Key for playlist entries/tracks list.
        URL (str): Key for track URL.
        EXTENSION (str): Key for file extension.
    """
    PLAYLIST_NAME = "playlistName"
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST_INDEX = "playlist_index"
    YOUTUBE_HASH = "id"
    PLAYLIST_TRACKS = "entries"
    URL = "url"
    EXTENSION = "ext"


class MediaInfo(Enum):
    """Enumeration of media information keys from YouTube API.
    
    Contains keys used to extract media metadata from YouTube API
    responses for single media items (videos/audio).
    
    Attributes:
        TITLE (str): Key for media title.
        ALBUM (str): Key for album name.
        ARTIST (str): Key for artist name.
        YOUTUBE_HASH (str): Key for YouTube video ID.
        URL (str): Key for webpage URL.
        EXTENSION (str): Key for file extension.
        FUL_PATH (str): Key for full file path.
        REQUESTED_DOWNLOADS (str): Key for requested downloads list.
    """
    TITLE = "title"
    ALBUM = "album"
    ARTIST = "artist"
    YOUTUBE_HASH = "id"
    URL = "webpage_url"
    EXTENSION = "ext"
    FUL_PATH = "filename"
    REQUESTED_DOWNLOADS = "requested_downloads"


class YoutubeOptiones(Enum):
    """Enumeration of YouTube downloader option keys.
    
    Contains keys used for configuring yt-dlp options, including
    format, output template, metadata, and logging settings.
    
    Attributes:
        FORMAT (str): Key for format specification.
        DOWNLOAD_ARCHIVE (str): Key for download archive file.
        NO_OVERWITES (str): Key for no-overwrites option.
        ADD_META_DATA (str): Key for add-metadata option.
        IGNORE_ERRORS (str): Key for ignore-errors option.
        QUIET (str): Key for quiet mode.
        LOGGER (str): Key for logger configuration.
        OUT_TEMPLATE (str): Key for output template.
    """
    FORMAT = "format"
    DOWNLOAD_ARCHIVE = "download_archive"
    NO_OVERWITES = "no-overwrites"
    ADD_META_DATA = "addmetadata"
    IGNORE_ERRORS = "ignoreerrors"
    QUIET = "quiet"
    LOGGER = "logger"
    OUT_TEMPLATE = "outtmpl"
