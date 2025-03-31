from enum import Enum

# TYP 1
# class YoutubeOptiones(Enum):
#     FORMAT = "format"
#     DOWNLOAD_ARCHIVE = "download_archive"
#     NO_OVERRIDE = "no-overwrites"
#     ADD_META_DATA = "addmetadata"
#     IGNORE_ERRORS = "ignoreerrors"
#     QUIET = "quiet"
#     LOGGER = "logger"
#     OUT_TEMPLATE = "outtmpl"


# class BaseOption(Enum):

#     def __init__(self, ytOption, optionValue):
#         self.ytOption = ytOption
#         self.optionValue = optionValue

#     @classmethod
#     def changeOptionValue(cls, optionName, newValue):
#         """Change the value of an option dynamically without a loop."""
#         option = cls.__members__.get(optionName.upper())
#         if option:
#             object.__setattr__(option, "optionValue", newValue)
#             object.__setattr__(option, "_value_", (option.ytOption, newValue))
#         else:
#             raise KeyError(f"Option '{optionName}' not found in {cls.__name__}")

#     @classmethod
#     def toDict(cls):
#         return {option.ytOption: option.optionValue for option in cls}


# class YoutubeDefaultOptiones(BaseOption):
#     FORMAT = YoutubeOptiones.FORMAT.value, "bestvideo+bestaudio"
#     DOWNLOAD_ARCHIVE = YoutubeOptiones.DOWNLOAD_ARCHIVE.value, "downloaded_songs.txt"
#     NO_OVERRIDE = YoutubeOptiones.NO_OVERRIDE.value, False
#     ADD_META_DATA = YoutubeOptiones.ADD_META_DATA.value, True
#     QUIET = YoutubeOptiones.QUIET.value, True
#     LOGGER = YoutubeOptiones.LOGGER.value, True


# class YoutubeGetInfoOptiones(BaseOption):
#     FORMAT = YoutubeOptiones.FORMAT.value, "best/best"
#     ADD_META_DATA = YoutubeOptiones.ADD_META_DATA.value, True
#     IGNORE_ERRORS = YoutubeOptiones.IGNORE_ERRORS.value, False
#     QUIET = YoutubeOptiones.QUIET.value, True
#     LOGGER = YoutubeOptiones.LOGGER.value, None


# TYPE 2
# # Enum for YouTube option names (keeping this as an Enum for clarity)
# from enum import Enum

# class YoutubeOptiones(Enum):
#     FORMAT = "format"
#     DOWNLOAD_ARCHIVE = "download_archive"
#     NO_OVERRIDE = "no-overwrites"
#     ADD_META_DATA = "addmetadata"
#     IGNORE_ERRORS = "ignoreerrors"
#     QUIET = "quiet"
#     LOGGER = "logger"
#     OUT_TEMPLATE = "outtmpl"

# class BaseOption():
#     def __init__(self, **options):
#         """Initialize options dictionary."""
#         self.options = options

#     def to_dict(self):
#         """Return all options as a dictionary."""
#         return self.options

# def change_value(self, option_name, new_value):
#     """Change the value of an option dynamically."""
#     if option_name in self.options:
#         self.options[option_name] = new_value
#     else:
#         raise KeyError(f"Option '{option_name}' not found in {self.__class__.__name__}")

# # Default YouTube options
# class YoutubeDefaultOptiones(BaseOption):
#     def __init__(self):
#         super().__init__(
#             format="bestvideo+bestaudio",
#             download_archive="downloaded_songs.txt",
#             no_overwrites=False,
#             addmetadata=True,
#             quiet=True,
#             logger=True,
#             outtmpl="%(title)s.%(ext)s",
#         )

#     def set_format(self, video_quality="best", extension="mp4"):
#         """Modify the format dynamically based on user input."""
#         format_string = f"best[height={video_quality}][ext={extension}]+bestaudio/bestvideo+bestaudio"
#         self.change_value("format", format_string)

# # Get Info Options for YouTube
# class YoutubeGetInfoOptiones(BaseOption):
#     def __init__(self):
#         super().__init__(
#             format="best/best",
#             addmetadata=True,
#             ignoreerrors=False,
#             quiet=True,
#             logger=None,
#         )

# # Usage Example:
# default_options = YoutubeDefaultOptiones()
# info_options = YoutubeGetInfoOptiones()

# print("Before modification:")
# print(default_options.to_dict())

# # Dynamically update the FORMAT option
# default_options.set_format(video_quality=1080, extension="mp4")

# print("\nAfter modification:")
# print(default_options.to_dict())

# # Directly modifying an option
# info_options.change_value("format", "test000")

# print("\nUpdated Info Options:")
# print(info_options.to_dict())


# TYPE 3
from enum import Enum

# Enum to define option names (Main Source of Option Names)


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


class PostProcessors(Enum):
    KEY = "key"
    PREFERREDCODEC = "preferredcodec"
    PREFERREDQUALITY = "preferredquality"


# Base class for options with tuple storage
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
    DOWNLOAD_ARCHIVE = (
        YoutubeOptiones.DOWNLOAD_ARCHIVE.value, "downloaded_songs.txt")
    NO_OVERRIDE = (YoutubeOptiones.NO_OVERRIDE.value, False)
    ADD_META_DATA = (YoutubeOptiones.ADD_META_DATA.value, True)
    QUIET = (YoutubeOptiones.QUIET.value, True)
    LOGGER = (YoutubeOptiones.LOGGER.value, True)
    OUT_TEMPLATE = (YoutubeOptiones.OUT_TEMPLATE.value, "%(title)s.%(ext)s")

    def __init__(self):
        super().__init__()


# Get Info Options for YouTube
class YoutubeGetInfoOptiones(BaseOption):
    FORMAT = (YoutubeOptiones.FORMAT.value, "best/best")
    ADD_META_DATA = (YoutubeOptiones.ADD_META_DATA.value, True)
    IGNORE_ERRORS = (YoutubeOptiones.IGNORE_ERRORS.value, False)
    QUIET = (YoutubeOptiones.QUIET.value, True)
    LOGGER = (YoutubeOptiones.LOGGER.value, None)

    def __init__(self):
        super().__init__()


class YoutubeVideoOptions(YoutubeDefaultOptiones):
    def __init__(self, outTemplate):
        super().__init__()
        self.overwrite_option(YoutubeOptiones.OUT_TEMPLATE, outTemplate)


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
    info_options = YoutubeGetInfoOptiones()

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
