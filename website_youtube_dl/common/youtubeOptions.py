from enum import Enum


class VideoQuality(Enum):
    BEST = "best"
    Q2160 = "2160"
    Q1080 = "1080"
    Q720 = "720"
    Q480 = "480"
    Q360 = "360"


class VideoExtension(Enum):
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"


class YoutubeOptiones(Enum):
    FORMAT = "format"
    DOWNLOAD_ARCHIVE = "download_archive"
    NO_OVERWITES = "no-overwrites"
    ADD_META_DATA = "addmetadata"
    IGNORE_ERRORS = "ignoreerrors"
    QUIET = "quiet"
    LOGGER = "logger"
    OUT_TEMPLATE = "outtmpl"
    POSTPROCESSORS = "postprocessors"
    EXTRACT_FLAT = "extract_flat"
    NO_PLAYLIST = "noplaylist"


class PostProcessors(Enum):
    KEY = "key"
    PREFERREDCODEC = "preferredcodec"
    PREFERREDQUALITY = "preferredquality"


class RequestArgument():
    """Wrapper class for YouTube downloader option arguments.
    
    Stores an option name (from YoutubeOptiones enum) and its corresponding
    value to be used in yt-dlp configuration dictionaries.
    
    Attributes:
        argument_name (YoutubeOptiones): The option enum member.
        argument_value: The value for this option.
    """
    
    def __init__(self, argument_name: YoutubeOptiones, argument_value):
        """Initialize RequestArgument with option name and value.
        
        Args:
            argument_name (YoutubeOptiones): Enum member representing the option.
            argument_value: The value for this option.
        """
        self.argument_name = argument_name
        self.argument_value = argument_value


class BaseOption():
    """Base class for YouTube downloader options configuration.
    
    Provides functionality to manage yt-dlp options dynamically, including
    adding, overwriting, and converting options to dictionaries. Options
    are stored as RequestArgument instances and converted to dictionaries
    for use with yt-dlp.
    """
    
    def __init__(self):
        """Initialize BaseOption (no-op, options are set via class attributes)."""
        pass

    def to_dict(self):
        """Convert all options to a dictionary for yt-dlp.
        
        Scans class attributes for RequestArgument instances and converts
        them to a dictionary with enum values as keys.
        
        Returns:
            dict: Dictionary of options suitable for yt-dlp configuration.
        """
        options = {}
        for key in dir(self):
            class_atribute = getattr(self, key)
            if key in YoutubeOptiones.__members__ and isinstance(class_atribute, RequestArgument):
                options[class_atribute.argument_name] = class_atribute.argument_value
        return options

    def convert_video_extension(self, video_extension: str):
        """Convert video extension string to VideoExtension Enum.
        
        Args:
            video_extension (str): Extension string (e.g., "mp4", "webm").
            
        Returns:
            VideoExtension: Corresponding VideoExtension enum member.
            
        Raises:
            ValueError: If the extension is not a valid VideoExtension.
        """
        try:
            return VideoExtension(video_extension.lower())
        except KeyError:
            raise ValueError(
                f"Invalid video extension: {video_extension}. Must be one of {[e.name for e in VideoExtension]}")

    def set_format(self,
                   video_quality,
                   extension):
        """Set video format dynamically based on quality and extension.
        
        Creates a format string for yt-dlp that specifies video quality
        (height) and extension, with fallback to best audio/video.
        
        Args:
            video_quality (VideoQuality): Video quality enum (e.g., VideoQuality.Q720).
            extension (VideoExtension): Video extension enum (e.g., VideoExtension.MP4).
        """
        format_string = f"best[height={video_quality.value}][ext={extension.value}]+bestaudio/bestvideo+bestaudio"
        self.add_new_option(YoutubeOptiones.FORMAT,
                            format_string, overwrite=True)

    def overwrite_option(self, option_enum: YoutubeOptiones, new_value):
        """Overwrite an existing option's value.
        
        Args:
            option_enum (YoutubeOptiones): Enum member from YoutubeOptiones
                (e.g., YoutubeOptiones.FORMAT).
            new_value: The new value for the option.
            
        Raises:
            KeyError: If the option doesn't exist. Use add_new_option instead.
        """
        option_key = option_enum.value

        if not hasattr(self, option_enum.name):
            raise KeyError(
                f"Option '{option_key}' does not exist. Use add_new_option instead.")

        setattr(self, option_enum.name, RequestArgument(option_key, new_value))

    def add_new_option(self,
                       option_enum: YoutubeOptiones,
                       option_value,
                       overwrite=False):
        """Dynamically add a new option using an Enum key.
        
        Args:
            option_enum (YoutubeOptiones): Enum member from YoutubeOptiones
                (e.g., YoutubeOptiones.FORMAT).
            option_value: The value for the option.
            overwrite (bool, optional): If True, overwrite existing option.
                Defaults to False.
                
        Raises:
            KeyError: If the option already exists and overwrite is False.
        """
        option_key = option_enum.value

        if hasattr(self, option_enum.name) and not overwrite:
            raise KeyError(
                f"Option '{option_key}' already exists. Use change_value instead.")

        setattr(self, option_enum.name, RequestArgument(
            option_key, option_value))


# Default YouTube options
class YoutubeDefaultOptiones(BaseOption):
    """Default YouTube downloader options configuration.
    
    Provides standard options for downloading media from YouTube,
    including metadata addition, quiet mode, and output template.
    """
    # DOWNLOAD_ARCHIVE = (
    #     YoutubeOptiones.DOWNLOAD_ARCHIVE.value, "downloaded_songs.txt")
    NO_OVERWITES = RequestArgument(YoutubeOptiones.NO_OVERWITES.value, False)
    ADD_META_DATA = RequestArgument(YoutubeOptiones.ADD_META_DATA.value, True)
    QUIET = RequestArgument(YoutubeOptiones.QUIET.value, True)
    LOGGER = RequestArgument(YoutubeOptiones.LOGGER.value, None)
    OUT_TEMPLATE = RequestArgument(
        YoutubeOptiones.OUT_TEMPLATE.value, "%(title)s.%(ext)s")

    def __init__(self):
        """Initialize YoutubeDefaultOptiones with default settings."""
        super().__init__()


class YoutubeGetSingleInfoOptiones(BaseOption):  # pragma: no_cover
    """Options for extracting single media information without downloading.
    
    Configured for quiet operation with metadata extraction and error handling
    suitable for getting information about a single YouTube video/audio.
    """
    ADD_META_DATA = RequestArgument(YoutubeOptiones.ADD_META_DATA.value, True)
    IGNORE_ERRORS = RequestArgument(YoutubeOptiones.IGNORE_ERRORS.value, False)
    QUIET = RequestArgument(YoutubeOptiones.QUIET.value, True)
    LOGGER = RequestArgument(YoutubeOptiones.LOGGER.value, None)

    def __init__(self):
        """Initialize YoutubeGetSingleInfoOptiones with info extraction settings."""
        super().__init__()


class YoutubeGetPlaylistInfoOptiones(BaseOption):  # pragma: no_cover
    """Options for extracting playlist information without downloading.
    
    Configured with flat extraction mode for playlists, allowing quick
    retrieval of playlist structure and track information.
    """
    EXTRACT_FLAT = RequestArgument(
        YoutubeOptiones.EXTRACT_FLAT.value, "in_playlist")
    ADD_META_DATA = RequestArgument(YoutubeOptiones.ADD_META_DATA.value, True)
    IGNORE_ERRORS = RequestArgument(YoutubeOptiones.IGNORE_ERRORS.value, False)
    QUIET = RequestArgument(YoutubeOptiones.QUIET.value, True)

    def __init__(self):
        """Initialize YoutubeGetPlaylistInfoOptiones with playlist extraction settings."""
        super().__init__()


class VideoVerificationOptiones(BaseOption):  # pragma: no_cover
    """Options for verifying video existence on YouTube.
    
    Minimal configuration for checking if a video exists without downloading,
    using best format and no playlist extraction.
    """
    quiet = RequestArgument(YoutubeOptiones.QUIET.value, True)
    no_playlist = RequestArgument(YoutubeOptiones.NO_PLAYLIST, True)
    format = RequestArgument(YoutubeOptiones.FORMAT.value, "best")

    def __init__(self):
        """Initialize VideoVerificationOptiones with verification settings."""
        super().__init__()

# Video Options for YouTube


class YoutubeVideoOptions(YoutubeDefaultOptiones):
    """Options for downloading video from YouTube.
    
    Extends YoutubeDefaultOptiones with video-specific configuration,
    including custom output template and video quality conversion.
    """
    
    def __init__(self, outTemplate):  # pragma: no_cover
        """Initialize YoutubeVideoOptions with output template.
        
        Args:
            outTemplate (str): Output template for downloaded video files.
        """
        super().__init__()
        self.overwrite_option(YoutubeOptiones.OUT_TEMPLATE, outTemplate)

    def convert_video_quality(self, video_quality: str):
        """Convert video quality string to VideoQuality Enum.
        
        Args:
            video_quality (str): Quality string (e.g., "720", "1080").
            
        Returns:
            VideoQuality: Corresponding VideoQuality enum member.
            
        Raises:
            ValueError: If the quality is not a valid VideoQuality.
        """
        try:
            return VideoQuality(video_quality.lower())
        except KeyError:
            raise ValueError(
                f"Invalid video quality: {video_quality}. Must be one of {[e.name for e in VideoQuality]}")


# Audio Options for YouTube
class YoutubeAudioOptions(YoutubeDefaultOptiones):
    """Options for downloading audio from YouTube.
    
    Extends YoutubeDefaultOptiones with audio-specific configuration,
    including FFmpeg post-processing to extract MP3 audio with
    specified quality settings.
    """
    POSTPROCESSORS = RequestArgument(YoutubeOptiones.POSTPROCESSORS.value, [
        {PostProcessors.KEY.value: "FFmpegExtractAudio",
         PostProcessors.PREFERREDCODEC.value: "mp3",
         PostProcessors.PREFERREDQUALITY.value: "192"}
    ])
    FORMAT = RequestArgument(
        YoutubeOptiones.FORMAT.value, "bestaudio/best")

    def __init__(self, outTemplate):
        """Initialize YoutubeAudioOptions with output template.
        
        Args:
            outTemplate (str): Output template for downloaded audio files.
        """
        super().__init__()
        self.overwrite_option(YoutubeOptiones.OUT_TEMPLATE, outTemplate)
