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
    def __init__(self, argument_name: YoutubeOptiones, argument_value):
        self.argument_name = argument_name
        self.argument_value = argument_value


class BaseOption():
    def __init__(self):
        """Initialize options from class attributes (tuples) using Enum values as dictionary keys"""
        pass

    def to_dict(self):
        """Return all options as a dictionary with Enum values as keys."""
        options = {}
        for key in dir(self):
            class_atribute = getattr(self, key)
            if key in YoutubeOptiones.__members__ and isinstance(class_atribute, RequestArgument):
                options[class_atribute.argument_name] = class_atribute.argument_value
        return options

    def convert_video_extension(self, video_extension: str):
        """Convert video extension string to VideoExtension Enum."""
        try:
            return VideoExtension(video_extension.lower())
        except KeyError:
            raise ValueError(
                f"Invalid video extension: {video_extension}. Must be one of {[e.name for e in VideoExtension]}")

    def set_format(self,
                   video_quality,
                   extension):
        """Modify the format dynamically based on user input."""
        format_string = f"best[height={video_quality.value}][ext={extension.value}]+bestaudio/bestvideo+bestaudio"
        self.add_new_option(YoutubeOptiones.FORMAT,
                            format_string, overwrite=True)

    def overwrite_option(self, option_enum: YoutubeOptiones, new_value):
        """
        Overwrites an existing option's value.

        option_enum: Enum member from YoutubeOptiones (e.g., YoutubeOptiones.FORMAT)
        new_value: The new value for the option
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
        """
        Dynamically add a new option using an Enum key.

        option_enum: Enum member from YoutubeOptiones (e.g., YoutubeOptiones.FORMAT)
        option_value: The value for the option
        """
        option_key = option_enum.value

        if hasattr(self, option_enum.name) and not overwrite:
            raise KeyError(
                f"Option '{option_key}' already exists. Use change_value instead.")

        setattr(self, option_enum.name, RequestArgument(
            option_key, option_value))


# Default YouTube options
class YoutubeDefaultOptiones(BaseOption):
    FORMAT = RequestArgument(
        YoutubeOptiones.FORMAT.value, "bestvideo+bestaudio")
    # DOWNLOAD_ARCHIVE = (
    #     YoutubeOptiones.DOWNLOAD_ARCHIVE.value, "downloaded_songs.txt")
    NO_OVERWITES = RequestArgument(YoutubeOptiones.NO_OVERWITES.value, False)
    ADD_META_DATA = RequestArgument(YoutubeOptiones.ADD_META_DATA.value, True)
    QUIET = RequestArgument(YoutubeOptiones.QUIET.value, True)
    LOGGER = RequestArgument(YoutubeOptiones.LOGGER.value, None)
    OUT_TEMPLATE = RequestArgument(
        YoutubeOptiones.OUT_TEMPLATE.value, "%(title)s.%(ext)s")

    def __init__(self):
        super().__init__()


class YoutubeGetSingleInfoOptiones(BaseOption):  # pragma: no_cover
    FORMAT = RequestArgument(YoutubeOptiones.FORMAT.value, "best/best")
    ADD_META_DATA = RequestArgument(YoutubeOptiones.ADD_META_DATA.value, True)
    IGNORE_ERRORS = RequestArgument(YoutubeOptiones.IGNORE_ERRORS.value, False)
    QUIET = RequestArgument(YoutubeOptiones.QUIET.value, True)
    LOGGER = RequestArgument(YoutubeOptiones.LOGGER.value, None)

    def __init__(self):
        super().__init__()


class YoutubeGetPlaylistInfoOptiones(BaseOption):  # pragma: no_cover
    EXTRACT_FLAT = RequestArgument(
        YoutubeOptiones.EXTRACT_FLAT.value, "in_playlist")
    ADD_META_DATA = RequestArgument(YoutubeOptiones.ADD_META_DATA.value, True)
    IGNORE_ERRORS = RequestArgument(YoutubeOptiones.IGNORE_ERRORS.value, False)
    QUIET = RequestArgument(YoutubeOptiones.QUIET.value, True)

    def __init__(self):
        super().__init__()


class VideoVerificationOptiones(BaseOption):  # pragma: no_cover
    quiet = RequestArgument(YoutubeOptiones.QUIET.value, True)
    no_playlist = RequestArgument(YoutubeOptiones.NO_PLAYLIST, True)
    format = RequestArgument(YoutubeOptiones.FORMAT.value, "best")

    def __init__(self):
        super().__init__()

# Video Options for YouTube


class YoutubeVideoOptions(YoutubeDefaultOptiones):
    def __init__(self, outTemplate):  # pragma: no_cover
        super().__init__()
        self.overwrite_option(YoutubeOptiones.OUT_TEMPLATE, outTemplate)

    def convert_video_quality(self, video_quality: str):
        """Convert video quality string to VideoQuality Enum."""
        try:
            return VideoQuality(video_quality.lower())
        except KeyError:
            raise ValueError(
                f"Invalid video quality: {video_quality}. Must be one of {[e.name for e in VideoQuality]}")


# Audio Options for YouTube
class YoutubeAudioOptions(YoutubeDefaultOptiones):
    POSTPROCESSORS = RequestArgument(YoutubeOptiones.POSTPROCESSORS.value, [
        {PostProcessors.KEY.value: "FFmpegExtractAudio",
         PostProcessors.PREFERREDCODEC.value: "mp3",
         PostProcessors.PREFERREDQUALITY.value: "192"}
    ])

    def __init__(self, outTemplate):
        super().__init__()
        self.overwrite_option(YoutubeOptiones.OUT_TEMPLATE, outTemplate)
