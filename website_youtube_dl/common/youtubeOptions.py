from enum import Enum

class YoutubeOptiones(Enum):
    FORMAT = "format"
    DOWNLOAD_ARCHIVE = "download_archive"
    NO_OVERRIDE = "no-overwrites"
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


class BaseOption():
    def __init__(self):
        """Initialize options from class attributes (tuples) using Enum values as dictionary keys"""
        self.options = {
            getattr(self, key)[0]: getattr(self, key)[1] for key in dir(self)
            if key in YoutubeOptiones.__members__ and isinstance(getattr(self, key), tuple)
        }

    def to_dict(self):
        """Return all options as a dictionary with Enum values as keys."""
        return self.options

    def change_format(self, video_quality="best", extension="mp4"):
        """Modify the format dynamically based on user input."""
        format_string = f"best[height={video_quality}][ext={extension}]+bestaudio/bestvideo+bestaudio"
        self.add_new_option(YoutubeOptiones.FORMAT,
                            format_string, overwrite=True)

    def overwrite_option(self, option: YoutubeOptiones, new_value):
        """Change the value of an option dynamically using YoutubeOptiones Enum (without loop)."""
        option_key = option.value

        if option_key in self.options:
            setattr(self, option.name, (option_key, new_value))
            self.options[option_key] = new_value
        else:
            raise KeyError(
                f"Option '{option_key}' not found in {self.__class__.__name__}")

    def add_new_option(self, option: YoutubeOptiones, option_value, overwrite=False):
        """Dynamically add a new option."""
        option_name = option.value

        if option_name in self.options and not overwrite:
            raise KeyError(
                f"Option '{option_name}' already exists. Use overwrite=True to modify.")

        setattr(self, option_name.upper(), (option_name, option_value))

        self.options[option_name] = option_value


# Default YouTube options
class YoutubeDefaultOptiones(BaseOption):
    FORMAT = (YoutubeOptiones.FORMAT.value, "bestvideo+bestaudio")
    # DOWNLOAD_ARCHIVE = (
    #     YoutubeOptiones.DOWNLOAD_ARCHIVE.value, "downloaded_songs.txt")
    NO_OVERRIDE = (YoutubeOptiones.NO_OVERRIDE.value, False)
    ADD_META_DATA = (YoutubeOptiones.ADD_META_DATA.value, True)
    QUIET = (YoutubeOptiones.QUIET.value, True)
    LOGGER = (YoutubeOptiones.LOGGER.value, None)
    OUT_TEMPLATE = (YoutubeOptiones.OUT_TEMPLATE.value, "%(title)s.%(ext)s")

    def __init__(self):
        super().__init__()


# Get Info Options for YouTube
class YoutubeGetSingleInfoOptiones(BaseOption):
    FORMAT = (YoutubeOptiones.FORMAT.value, "best/best")
    ADD_META_DATA = (YoutubeOptiones.ADD_META_DATA.value, True)
    IGNORE_ERRORS = (YoutubeOptiones.IGNORE_ERRORS.value, False)
    QUIET = (YoutubeOptiones.QUIET.value, True)
    LOGGER = (YoutubeOptiones.LOGGER.value, None)

    def __init__(self):
        super().__init__()

class YoutubeGetPlaylistInfoOptiones(BaseOption):
    EXTRACT_FLAT = (YoutubeOptiones.EXTRACT_FLAT.value, "in_playlist")
    ADD_META_DATA = (YoutubeOptiones.ADD_META_DATA.value, True)
    IGNORE_ERRORS = (YoutubeOptiones.IGNORE_ERRORS.value, False)
    QUIET = (YoutubeOptiones.QUIET.value, True)

    def __init__(self):
        super().__init__()

class VideoVerificationOptiones(BaseOption):
    QUIET = (YoutubeOptiones.QUIET.value, True)
    NO_PLAYLIST = (YoutubeOptiones.NO_PLAYLIST, True)
    FORMAT = (YoutubeOptiones.FORMAT.value, "best")

    def __init__(self):
        super().__init__()

# Video Options for YouTube
class YoutubeVideoOptions(YoutubeDefaultOptiones):
    def __init__(self, outTemplate):
        super().__init__()
        self.overwrite_option(YoutubeOptiones.OUT_TEMPLATE, outTemplate)

# Audio Options for YouTube
class YoutubeAudioOptions(YoutubeDefaultOptiones):
    POSTPROCESSORS = (YoutubeOptiones.POSTPROCESSORS.value, [
        {PostProcessors.KEY.value: "FFmpegExtractAudio",
         PostProcessors.PREFERREDCODEC.value: "mp3",
         PostProcessors.PREFERREDQUALITY.value: "192"}
    ])

    def __init__(self, outTemplate):
        super().__init__()
        self.overwrite_option(YoutubeOptiones.OUT_TEMPLATE, outTemplate)


if __name__ == "__main__":

    default_options = YoutubeDefaultOptiones()
    info_options = YoutubeGetSingleInfoOptiones()

    print("Before modification:")
    print(default_options.to_dict())

    default_options.change_format(video_quality=1080, extension="mp4")

    print("\nAfter modification:")
    print(default_options.to_dict())

    info_options.overwrite_option(YoutubeOptiones.FORMAT, "test000")

    print("\nUpdated Info Options:")
    print(info_options.to_dict())

    audio_options = YoutubeAudioOptions("test_path")
    print(audio_options.to_dict())
