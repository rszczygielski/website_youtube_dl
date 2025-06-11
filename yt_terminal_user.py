import configparser
import argparse
import logging
from website_youtube_dl.common.youtubeConfigManager import BaseConfigParser
from website_youtube_dl.common.easyID3Manager import EasyID3Manager
from website_youtube_dl.common.youtubeDL import YoutubeDlPlaylists

logger = logging.getLogger(__name__)


class TerminalUser(YoutubeDlPlaylists):  # pragma: no_cover
    def __init__(self, configManager: BaseConfigParser, easy_id3_manager: EasyID3Manager) -> None:
        super().__init__(configManager, easy_id3_manager)

    def is_playlist(self, url):
        if url != None and "list=" in url:
            return True
        else:
            return False

    def if_double_hash(self, url):
        if url != None and "list=" in url and "v=" in url:
            return True
        else:
            return False

    def download_double_hashed_link_video(self, url, type):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press "s"
        If you want to download whole playlist press "p"
        """)
        if userResponse == "s":
            self.download_yt_media(url, type)
        elif userResponse == "p":
            self.download_whole_video_playlist(url, type)
        else:
            raise ValueError(
                "Please enter 's' for single video or 'p' for playlist")

    def download_double_hashed_link_audio(self, url):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press "s"
        If you want to download whole playlist press "p"
        """)
        if userResponse == "s":
            self.download_yt_media(url)
        elif userResponse == "p":
            self.download_whole_audio_playlist(url)
        else:
            raise ValueError(
                "Please enter 's' for single video or 'p' for playlist")

    def download_terminal(self, url, type):
        if not url and type == "mp3":
            self.downolad_all_config_playlists_audio()
            return
        elif not url and type != "mp3":
            self.downolad_all_config_playlists_video(type)
            return
        isPlaylist = self.isPlaylist(url)
        isDouble = self.ifDoubleHash(url)
        if isPlaylist and isDouble:
            if type == "mp3":
                self.downloadDoubleHashedLinkAudio(url)
            else:
                self.downloadDoubleHashedLinkVideo(url, type)
        elif isPlaylist and not isDouble:
            if type == "mp3":
                self.download_whole_audio_playlist(url)
            else:
                self.download_whole_video_playlist(url, type)
        else:
            if type == "mp3":
                self.download_yt_media(url)
            else:
                self.download_yt_media(url, type)


def main():  # pragma: no_cover
    parser = argparse.ArgumentParser(
        "Program downloads mp3 form given youtube URL")
    parser.add_argument("-u", metavar="url", dest="url",
                        help="Link to the youtube video")
    parser.add_argument("-t", metavar="type", dest="type",
                        choices=["360", "480", "720", "1080", "4k", "mp3"],
                        default="mp3",
                        help="Select downolad type --> ['360', '720', '1080', '2160', 'mp3'], default: mp3")
    parser.add_argument("-c", metavar="config", dest="config",
                        default="youtube_config.ini",
                        help="Path to the config file --> default youtube_config.ini")
    args = parser.parse_args()
    url = args.url
    type = args.type
    config = args.config
    config_parser_manager = BaseConfigParser(
        config, configparser.ConfigParser())
    easy_id3_manager = EasyID3Manager()
    terminalUser = TerminalUser(config_parser_manager, easy_id3_manager)
    terminalUser.downloadTerminal(url, type)


if __name__ == "__main__":
    main()
