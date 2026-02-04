import configparser
import os
import logging
from .configKeys import ConfigKeys

logger = logging.getLogger("__main__")


class BaseConfigParser():
    """Base configuration parser for YouTube downloader settings.
    
    Provides functionality to read and manage configuration files containing
    global settings (like save path) and playlist URLs. Automatically creates
    a default configuration file if none exists.
    
    Attributes:
        config_file_path (str): Path to the configuration file.
        config_parser (configparser.ConfigParser): ConfigParser instance
            used to read/write configuration.
    """
    
    def __init__(self, config_file_path,
                 config_parser=configparser.ConfigParser()):
        """Initialize BaseConfigParser with configuration file path.
        
        Args:
            config_file_path (str): Path to the configuration file.
            config_parser (configparser.ConfigParser, optional): ConfigParser
                instance to use. Defaults to a new ConfigParser instance.
        """
        self.config_file_path = config_file_path
        logger.info(f"Config file path: {self.config_file_path}")
        self.config_parser = config_parser
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            self.create_default_config_file()

    def get_save_path(self):
        """Get the save path from configuration file.
        
        Reads the global save path setting from the configuration file.
        
        Returns:
            str: The save path directory, or None if config file is invalid.
        """
        logger.debug("Getting save path from config file")
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            logger.warning("Config file has no sections, returning None for save path")
            return None
        save_path = self.config_parser[ConfigKeys.GLOBAL.value][ConfigKeys.PATH.value]
        logger.info(f"Retrieved save path: {save_path}")
        return save_path

    def get_playlist_url(self, playlist_name):
        """Get URL for a specific playlist by name.
        
        Args:
            playlist_name (str): Name of the playlist to look up.
            
        Returns:
            str: The playlist URL if found, None otherwise.
        """
        logger.debug(f"Getting URL for playlist: {playlist_name}")
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            logger.warning("Config file has no sections, returning None for playlist URL")
            return None
        for config_playlist_name in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            if config_playlist_name == playlist_name:
                playlist_url = self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name]
                logger.info(f"Found playlist URL for '{playlist_name}': {playlist_url}")
                return playlist_url
        logger.warning(f"Playlist '{playlist_name}' not found in config file")
        return None

    def get_playlists(self):
        """Get all playlists from configuration file as a dictionary.
        
        Returns:
            dict: Dictionary mapping playlist names to their URLs.
                Returns empty dict if config file is invalid.
        """
        logger.debug("Getting all playlists from config file")
        playlists_from_config = {}
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            logger.warning("Config file has no sections, returning empty playlists dict")
            return playlists_from_config
        logger.debug(f"Playlists from config file: {self.config_parser[ConfigKeys.PLAYLISTS.value]}")
        for playlist_name in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            playlists_from_config[playlist_name] = self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name]
        logger.info(f"Retrieved {len(playlists_from_config)} playlists from config file")
        return playlists_from_config

    def get_url_of_playlists(self):
        """Get list of all playlist URLs from configuration file.
        
        Returns:
            list: List of playlist URLs (strings). Returns empty list
                if config file is invalid.
        """
        logger.debug("Getting URLs of all playlists from config file")
        playlist_list = []
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            logger.warning("Config file has no sections, returning empty playlist URLs list")
            return playlist_list
        for playlist_name in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            playlist_list.append(
                self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name])
        logger.info(f"Retrieved {len(playlist_list)} playlist URLs from config file")
        return playlist_list

    def create_default_config_file(self):
        """Create a default configuration file with standard settings.
        
        Creates a new config file with global and playlists sections.
        Sets the default save path to ~/Music and creates the directory
        if it doesn't exist.
        """
        logger.info("Creating default config file")
        self.config_parser.add_section(ConfigKeys.GLOBAL.value)
        logger.debug(f"Added section: {ConfigKeys.GLOBAL.value}")
        self.config_parser.add_section(ConfigKeys.PLAYLISTS.value)
        logger.debug(f"Added section: {ConfigKeys.PLAYLISTS.value}")
        home_path = os.path.expanduser(ConfigKeys.SWUNG_DASH.value)
        music_path = os.path.join(home_path, ConfigKeys.MUSIC.value)
        logger.debug(f"Default music path: {music_path}")
        self._handle_default_dir(music_path)
        self.config_parser[ConfigKeys.GLOBAL.value][ConfigKeys.PATH.value] = music_path
        self.save_config()
        logger.info(
            f"Default config file created at {self.config_file_path}")

    def _handle_default_dir(self, dirPath):  # pragma: no_cover
        """Create default directory if it doesn't exist.
        
        Args:
            dirPath (str): Path to the directory to create.
        """
        logger.debug(f"Handling default directory: {dirPath}")
        print(f"Default directory: {dirPath}")
        if not os.path.exists(dirPath):
            logger.info(f"Default directory {dirPath} does not exist, creating it")
            os.mkdir(dirPath)
            logger.info(f"Default directory {dirPath} created successfully")
        else:
            logger.debug(f"Default directory {dirPath} already exists")

    def save_config(self):  # pragma: no_cover
        """Save configuration to file.
        
        Writes the current configuration state to the config file.
        Creates the config directory if it doesn't exist.
        """
        logger.debug(f"Starting to save config file at {self.config_file_path}")
        # os.chmod(self.config_file_path, 0o644)
        config_dir = os.path.dirname(self.config_file_path)
        if config_dir:
            os.makedirs(config_dir, mode=0o755, exist_ok=True)
            logger.debug(f"Ensured config directory exists: {config_dir}")
        with open(self.config_file_path, ConfigKeys.WRITE.value) as configfile:
            logger.info(f"Saving config file at {self.config_file_path}")
            self.config_parser.write(configfile)
            logger.debug("Config file written successfully")


class ConfigParserManager(BaseConfigParser):
    """Extended configuration parser with playlist management capabilities.
    
    Extends BaseConfigParser to provide methods for adding and deleting
    playlists from the configuration file.
    
    Attributes:
        config_file_path (str): Path to the configuration file.
        config_parser (configparser.ConfigParser): ConfigParser instance
            used to read/write configuration.
    """
    
    def __init__(self, config_file_path,
                 config_parser=configparser.ConfigParser()):
        """Initialize ConfigParserManager with configuration file path.
        
        Args:
            config_file_path (str): Path to the configuration file.
            config_parser (configparser.ConfigParser, optional): ConfigParser
                instance to use. Defaults to a new ConfigParser instance.
        """
        logger.debug("Initializing ConfigParserManager")
        super().__init__(config_file_path, config_parser)
        logger.info("ConfigParserManager initialized successfully")

    def add_playlist(self, playlist_name, playlist_url):
        """Add or update a playlist in the configuration file.
        
        Args:
            playlist_name (str): Name of the playlist to add.
            playlist_url (str): YouTube URL of the playlist.
            
        Returns:
            bool: True if playlist was added successfully, False if
                config file is invalid or PLAYLISTS section is missing.
        """
        logger.info(f"Attempting to add playlist: {playlist_name} with URL: {playlist_url}")
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if ConfigKeys.PLAYLISTS.value not in self.config_parser:
            logger.error(f"{ConfigKeys.CONFIG_ERROR.value} - PLAYLISTS section not found in config file")
            return False
        if playlist_name in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            logger.warning(f"Playlist '{playlist_name}' already exists, overwriting with new URL")
        self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name] = playlist_url
        logger.info(f"Playlist {playlist_name}: {playlist_url} added to config")
        self.save_config()
        logger.debug(f"Successfully added playlist '{playlist_name}' to config file")
        return True

    def delete_playlist(self, playlist_name):
        """Delete a playlist from the configuration file.
        
        Args:
            playlist_name (str): Name of the playlist to delete.
            
        Returns:
            bool: True if playlist was deleted successfully, False if
                playlist doesn't exist, config file is invalid, or
                PLAYLISTS section is missing.
        """
        logger.info(f"Attempting to delete playlist: {playlist_name}")
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            logger.error(f"{ConfigKeys.CONFIG_ERROR.value} - Config file has no sections")
            return False
        if ConfigKeys.PLAYLISTS.value not in self.config_parser:
            logger.error(f"{ConfigKeys.CONFIG_ERROR.value} - PLAYLISTS section not found in config file")
            return False
        if playlist_name not in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            logger.warning(f"Playlist '{playlist_name}' not found in config file, cannot delete")
            return False
        self.config_parser.remove_option(
            ConfigKeys.PLAYLISTS.value, playlist_name)
        logger.info(f"Playlist '{playlist_name}' removed from config")
        self.save_config()
        logger.debug(f"Successfully deleted playlist '{playlist_name}' from config file")
        return True

