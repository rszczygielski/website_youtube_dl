import configparser
import argparse
import logging
from website_youtube_dl.common.youtubeConfigManager import ConfigParserManager
from website_youtube_dl.common.easyID3Manager import EasyID3Manager
from website_youtube_dl.common.youtubeDL import YoutubeDlPlaylists

logger = logging.getLogger(__name__)


class TerminalUser(YoutubeDlPlaylists):  # pragma: no_cover
    def __init__(self, configManager: ConfigParserManager, easyID3Manager: EasyID3Manager) -> None:
        super().__init__(configManager, easyID3Manager)

    def isPlaylist(self, url):
        if url != None and "list=" in url:
            return True
        else:
            return False

    def ifDoubleHash(self, url):
        if url != None and "list=" in url and "v=" in url:
            return True
        else:
            return False

    def downloadDoubleHashedLinkVideo(self, url, type):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press "s"
        If you want to download whole playlist press "p"
        """)
        if userResponse == "s":
            self.downloadVideo(url, type)
        elif userResponse == "p":
            self.downloadWholeVideoPlaylist(url, type)
        else:
            raise ValueError(
                "Please enter 's' for single video or 'p' for playlist")

    def downloadDoubleHashedLinkAudio(self, url):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press "s"
        If you want to download whole playlist press "p"
        """)
        if userResponse == "s":
            self.downloadAudio(url)
        elif userResponse == "p":
            self.downloadWholeAudioPlaylist(url)
        else:
            raise ValueError(
                "Please enter 's' for single video or 'p' for playlist")

    def downloadTerminal(self, url, type):
        if not url and type == "mp3":
            self.downoladAllConfigPlaylistsAudio()
            return
        elif not url and type != "mp3":
            self.downoladAllConfigPlaylistsVideo(type)
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
                self.downloadWholeAudioPlaylist(url)
            else:
                self.downloadWholeVideoPlaylist(url, type)
        else:
            if type == "mp3":
                self.downloadAudio(url)
            else:
                self.downloadVideo(url, type)


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
    configParserManager = ConfigParserManager(
        config, configparser.ConfigParser())
    easyID3Manager = EasyID3Manager()
    terminalUser = TerminalUser(configParserManager, easyID3Manager)
    terminalUser.downloadTerminal(url, type)


if __name__ == "__main__":
    main()
