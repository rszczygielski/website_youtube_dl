import configparser
import os
import logging
from .configKeys import ConfigKeys

logger = logging.getLogger("__main__")


class ConfigParserManager():
    def __init__(
            self,
            configFilePath,
            config_parser=configparser.ConfigParser()):
        self.config_file_path = configFilePath
        self.config_parser = config_parser

    def create_default_config_file(self):
        self.config_parser.add_section(ConfigKeys.GLOBAL.value)
        self.config_parser.add_section(ConfigKeys.PLAYLISTS.value)
        home_path = os.path.expanduser(ConfigKeys.SWUNG_DASH.value)
        music_path = os.path.join(home_path, ConfigKeys.MUSIC.value)
        self.handle_default_dir(music_path)
        self.config_parser[ConfigKeys.GLOBAL.value][ConfigKeys.PATH.value] = music_path
        self.save_config()

    def get_save_path(self):
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            self.create_default_config_file()
        return self.config_parser[ConfigKeys.GLOBAL.value][ConfigKeys.PATH.value]

    def handle_default_dir(self, dirPath):  # pragma: no_cover
        if not os.path.exists(dirPath):
            logger.info(
                f"Default directory {dirPath} not exists, creating one")
            os.mkdir(dirPath)

    def get_playlist_url(self, playlist_name):
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            self.create_default_config_file()
        for config_playlist_name in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            if config_playlist_name == playlist_name:
                return self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name]
        return None

    def get_playlists(self):
        playlists_from_config = {}
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            self.create_default_config_file()
        for playlist_name in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            playlists_from_config[playlist_name] = self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name]
        return playlists_from_config

    def get_url_of_playlists(self):
        playlist_list = []
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            self.create_default_config_file()
        for playlist_name in self.config_parser[ConfigKeys.PLAYLISTS.value]:
            playlist_list.append(
                self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name])
        return playlist_list

    def save_config(self):  # pragma: no_cover
        with open(self.config_file_path, ConfigKeys.WRITE.value) as configfile:
            self.config_parser.write(configfile)

    def add_playlist(self, playlist_name, playlist_url):
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if ConfigKeys.PLAYLISTS.value not in self.config_parser:
            logger.error(ConfigKeys.CONFIG_ERROR.value)
            return False
        self.config_parser[ConfigKeys.PLAYLISTS.value][playlist_name] = playlist_url
        logger.info(f"Playlist {playlist_name}: {playlist_url} added")
        self.save_config()

    def delete_playlist(self, playlist_name):
        self.config_parser.clear()
        self.config_parser.read(self.config_file_path)
        if len(self.config_parser.sections()) == 0:
            logger.error(ConfigKeys.CONFIG_ERROR.value)
            return False
        self.config_parser.remove_option(
            ConfigKeys.PLAYLISTS.value, playlist_name)
        self.save_config()


if __name__ == "__main__":
    config = ConfigParserManager(
        "/home/rszczygielski/pythonVSC/personal_classes/website/youtube_config.ini")
