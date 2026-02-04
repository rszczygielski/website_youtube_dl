from enum import Enum


class ConfigKeys(Enum):
    """Enumeration of configuration file keys and constants.
    
    This enum contains all the keys and constant values used throughout
    the configuration file management system.
    
    Attributes:
        GLOBAL (str): Section name for global configuration settings.
        PLAYLISTS (str): Section name for playlists configuration.
        SWUNG_DASH (str): Tilde character used for home directory expansion.
        MUSIC (str): Default music directory name.
        PATH (str): Key name for save path configuration.
        WRITE (str): File write mode for config file operations.
        CONFIG_ERROR (str): Error message for invalid configuration files.
    """
    GLOBAL = "global"
    PLAYLISTS = "playlists"
    SWUNG_DASH = "~"
    MUSIC = "Music"
    PATH = "path"
    WRITE = "w"
    CONFIG_ERROR = "Config file is not correct"
