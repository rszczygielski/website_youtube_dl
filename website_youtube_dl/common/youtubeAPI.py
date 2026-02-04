class SingleMedia():
    """Data class representing a single media item from YouTube.
    
    Stores metadata about a downloaded or requested single media file,
    including file path, title, album, artist, YouTube hash, URL, and
    file extension.
    
    Attributes:
        file_path (str): Full path to the downloaded file.
        title (str): Title of the media.
        album (str): Album name (if available).
        artist (str): Artist name (if available).
        yt_hash (str): YouTube video ID or hash.
        url (str): Full YouTube URL.
        extension (str): File extension (e.g., "mp3", "mp4").
    """
    
    def __init__(
            self,
            file_path,
            title,
            album,
            artist,
            yt_hash,
            url,
            extension):
        """Initialize SingleMedia with metadata.
        
        Args:
            file_path (str): Full path to the downloaded file.
            title (str): Title of the media.
            album (str): Album name.
            artist (str): Artist name.
            yt_hash (str): YouTube video ID or hash.
            url (str): Full YouTube URL.
            extension (str): File extension.
        """
        self.file_path = file_path
        self.title = title
        self.album = album
        self.artist = artist
        self.yt_hash = yt_hash
        self.url = url
        self.extension = extension


class MediaFromPlaylist():
    """Data class representing a media item from a playlist.
    
    Stores minimal information about a track within a playlist,
    containing only the title and YouTube hash needed to identify
    and download the track.
    
    Attributes:
        title (str): Title of the track.
        yt_hash (str): YouTube video ID or hash.
    """
    
    def __init__(self, title, yt_hash):
        """Initialize MediaFromPlaylist with track information.
        
        Args:
            title (str): Title of the track.
            yt_hash (str): YouTube video ID or hash.
        """
        self.title = title
        self.yt_hash = yt_hash


class PlaylistMedia():
    """Data class representing a YouTube playlist with its tracks.
    
    Stores playlist metadata including the playlist name and a list
    of all media items (tracks) contained in the playlist.
    
    Attributes:
        playlist_name (str): Name of the playlist.
        media_from_playlist_list (list): List of MediaFromPlaylist objects
            representing tracks in the playlist.
    """
    
    def __init__(self, playlist_name, media_from_playlist_list: list):
        """Initialize PlaylistMedia with playlist information.
        
        Args:
            playlist_name (str): Name of the playlist.
            media_from_playlist_list (list): List of MediaFromPlaylist objects.
        """
        self.playlist_name = playlist_name
        self.media_from_playlist_list = media_from_playlist_list



class ResultOfYoutube():
    """Result wrapper for YouTube operations.
    
    Provides a standardized way to return results from YouTube operations,
    supporting both successful data returns and error information. This
    allows callers to check for errors before accessing data.
    
    Attributes:
        _is_error (bool): Internal flag indicating if an error occurred.
        _error_info (str): Error message if an error occurred.
        _data: The result data (SingleMedia, PlaylistMedia, etc.) if successful.
    """
    _is_error = False
    _error_info = None
    data = None

    def __init__(self, data=None) -> None:
        """Initialize ResultOfYoutube with optional data.
        
        Args:
            data: Optional data to set. Defaults to None.
        """
        self.set_data(data)

    def set_error(self, error_info: str):
        """Mark the result as an error and set error information.
        
        Args:
            error_info (str): Error message describing what went wrong.
        """
        self._is_error = True
        self._error_info = error_info

    def set_data(self, data):
        """Set the result data (marks as successful).
        
        Args:
            data: The data to store as the result.
        """
        self._data = data

    def is_error(self):
        """Check if the result represents an error.
        
        Returns:
            bool: True if an error occurred, False otherwise.
        """
        return self._is_error

    def get_data(self):
        """Get the result data if no error occurred.
        
        Returns:
            The stored data if successful, None if an error occurred.
        """
        if not self._is_error:
            return self._data

    def get_error_info(self):
        """Get the error message if an error occurred.
        
        Returns:
            str: Error message if an error occurred, None otherwise.
        """
        if self._is_error:
            return self._error_info


class FormatBase():
    """Base class for media format specifications.
    
    Provides common functionality for different media formats, including
    format type and file suffix management.
    
    Attributes:
        file_format (str): The format identifier.
        file_suffix (str): Suffix to append to filenames for this format.
    """
    
    def __init__(self, fileFormat):
        """Initialize FormatBase with format specification.
        
        Args:
            fileFormat (str): Format identifier (e.g., "mp3", "360").
        """
        self.file_format = fileFormat
        self.file_suffix = fileFormat

    def get_format_type(self):
        """Get the format type identifier.
        
        Returns:
            str: The format identifier.
        """
        return self.file_format

    def get_file_suffix(self):
        """Get the file suffix for this format.
        
        Returns:
            str: The file suffix string.
        """
        return self.file_suffix

    def set_file_suffix(self, fileSuffix):
        """Set a custom file suffix.
        
        Args:
            fileSuffix (str): New file suffix to use.
        """
        self.file_suffix = fileSuffix


class FormatMP3(FormatBase):
    """Format specification for MP3 audio files."""
    
    def __init__(self):
        """Initialize FormatMP3 with "mp3" format."""
        super().__init__("mp3")


class VideoFormat(FormatBase):
    """Base class for video format specifications.
    
    Extends FormatBase to add video-specific suffix formatting
    that includes resolution information.
    """
    
    def __init__(self, resolution):
        """Initialize VideoFormat with resolution.
        
        Args:
            resolution (str): Video resolution (e.g., "360", "720", "1080").
        """
        super().__init__(resolution)
        self.set_file_suffix(f"f_{resolution}p")


class Format360p(VideoFormat):
    """Format specification for 360p video resolution."""
    
    def __init__(self):
        """Initialize Format360p with 360p resolution."""
        super().__init__("360")


class Format480p(VideoFormat):
    """Format specification for 480p video resolution."""
    
    def __init__(self):
        """Initialize Format480p with 480p resolution."""
        super().__init__("480")


class Format720p(VideoFormat):
    """Format specification for 720p video resolution."""
    
    def __init__(self):
        """Initialize Format720p with 720p resolution."""
        super().__init__("720")


class Format1080p(VideoFormat):
    """Format specification for 1080p video resolution."""
    
    def __init__(self):
        """Initialize Format1080p with 1080p resolution."""
        super().__init__("1080")


class Format2160p(VideoFormat):
    """Format specification for 2160p (4K) video resolution."""
    
    def __init__(self):
        """Initialize Format2160p with 2160p resolution."""
        super().__init__("2160")
