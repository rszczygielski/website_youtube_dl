import yt_dlp
import configparser
import os
import argparse
from configParserManager import ConfigParserManager
from metaDataManager import MetaDataManager
import logging
from myLogger import Logger

class YoutubeDL():
    def __init__(self, configManager:ConfigParserManager, metaDataMenager:MetaDataManager, ytLogger:Logger=Logger):
        self.metaDataMenager = metaDataMenager
        self.configManager = configManager
        self.savePath = self.configManager.getSavePath()
        self.ydl_video_opts = {
        "format": "bestvideo+bestaudio",
        # 'download_archive': 'downloaded_songs.txt',
        "no-override": False,
        "logger": ytLogger,
        'addmetadata': True,
        }
        self.ydl_audio_opts = {
        "format": "bestvideo+bestaudio",
        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
        # 'download_archive': 'downloaded_songs.txt',
        # "no-override": False,
        "logger": ytLogger,
        'addmetadata': True,
        'outtmpl':  self.savePath + '/%(title)s.%(ext)s',
        }

    def downloadFile(self, youtubeURL:str, youtubeOptions:dict): #pragma: no_cover
        """Method used to download youtube media based on URL

        Args:
            youtubeURL (str): YouTube URL
            youtubeOptions (dict): YouTube options dict form init

        Returns:
            class: meta data form youtube
        """
        with yt_dlp.YoutubeDL(youtubeOptions) as ydl:
            try:
                return ydl.extract_info(youtubeURL)
            except Exception as exception:
                return str(exception)

    def setVideoOptions(self, type):
        self.ydl_video_opts['format'] = f'bestvideo[height={type}][ext=mp4]+bestaudio/bestvideo+bestaudio'
        if type == "2160":
            self.ydl_video_opts['outtmpl'] = self.savePath + '/%(title)s' + f'_4k' + '.%(ext)s'
        else:
            self.ydl_video_opts['outtmpl'] = self.savePath + '/%(title)s' + f'_{type}p' + '.%(ext)s'

    def downloadVideo(self, youtubeURL:str, type:str):
        """Method uded to download video type from YouTube

        Args:
            youtubeURL (str): YouTube URL
        """
        self.setVideoOptions(type)
        mediaHash = self.getMediaHash(youtubeURL)
        return self.downloadFile(mediaHash, self.ydl_video_opts)

    def downloadVideoPlaylist(self, youtubeURL:str, type:str):
        self.setVideoOptions(type)
        playlistHash = self.getPlaylistHash(youtubeURL)
        return self.downloadFile(playlistHash, self.ydl_video_opts)

    def downloadAudio(self, youtubeURL:str):
        """Method uded to download audio type from Youtube, convert metadata
        into mp3 format used mutagen.easyid3

        Args:
            youtubeURL (str): YouTube URL
        """
        mediaHash = self.getMediaHash(youtubeURL)
        metaData = self.downloadFile(mediaHash, self.ydl_audio_opts)
        if isinstance(metaData, str):
            return metaData
        self.metaDataMenager.setMetaDataSingleFile(metaData, self.savePath)
        return metaData

    def downloadAudioPlaylist(self, youtubeURL:str):
        playlistHash = self.getPlaylistHash(youtubeURL)
        metaData = self.downloadFile(playlistHash, self.ydl_audio_opts)
        if isinstance(metaData, str):
            return metaData
        self.metaDataMenager.setMetaDataPlaylist(metaData, self.savePath)
        return metaData

    def downoladConfigPlaylistVideo(self, type):
        """Method used to download all playlists added to cofig file - type video
        """
        playlistList = self.configManager.getUrlOfPlaylists()
        self.setVideoOptions(type)
        for playlistURL in playlistList:
            self.downloadVideoPlaylist(playlistURL, type)

    def downoladConfigPlaylistAudio(self):
        """Method used to dowload all playlists added to cofig file - type audio
        """
        playlistList = self.configManager.getUrlOfPlaylists()
        for playlistURL in playlistList:
            self.downloadAudioPlaylist(playlistURL)

    def getMediaHash(self, url):
        onlyHashesInLink = url.split("?")[1]
        numberOfEqualSign = url.count("=")
        splitedHashes = onlyHashesInLink.split("=")
        if numberOfEqualSign == 1:
            if "list=" in onlyHashesInLink:
                return ""
            else:
                mediaHash = onlyHashesInLink[2:]
                return mediaHash
        elif numberOfEqualSign > 2:
            mediaHash = splitedHashes[1][:splitedHashes[1].index("&")]
            return mediaHash
        elif numberOfEqualSign == 2:
            mediaHash = splitedHashes[1][:splitedHashes[1].index("&")]
            return mediaHash

    def getPlaylistHash(self, url):
        onlyHashesInLink = url.split("?")[1]
        numberOfEqualSign = url.count("=")
        splitedHashes = onlyHashesInLink.split("=")
        if numberOfEqualSign == 1:
            if "list=" in onlyHashesInLink:
                playlistHash = onlyHashesInLink[5:]
                return playlistHash
            else:
                raise ValueError("This is not a playlist")
        elif numberOfEqualSign > 2:
            playlistHash = splitedHashes[2][:splitedHashes[2].index("&")]
            return playlistHash
        elif numberOfEqualSign == 2:
            playlistHash = splitedHashes[2]
            return playlistHash


class TerminalUser(YoutubeDL): #pragma: no_cover
    def __init__(self, configManager:ConfigParserManager, metaDataMenager:MetaDataManager) -> None:
        super().__init__(configManager, metaDataMenager)

    def isPlaylist(self, url):
        if url == None:
            return False
        elif "list=" in url:
            return True
        else:
            return False

    def ifDoubleHash(self, url):
        if url == None:
            return False
        elif "list=" in url and "v=" in url:
            return True
        else:
            return False

    def downloadDoubleHashedLinkVideo(self, url, type):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press 's'
        If you want to download whole playlist press 'p'
        """)
        if userResponse == "s":
            self.downloadVideo(url, type)
        elif userResponse == "p":
            self.downloadVideoPlaylist(url, type)
        else:
            raise ValueError("Please enter 's' for single video or 'p' for playlist")

    def downloadDoubleHashedLinkAudio(self, url):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press 's'
        If you want to download whole playlist press 'p'
        """)
        if userResponse == "s":
            self.downloadAudio(url)
        elif userResponse == "p":
            self.downloadAudioPlaylist(url)
        else:
            raise ValueError("Please enter 's' for single video or 'p' for playlist")

    def downloadTerminal(self, url, type):
        if url == None and type == "mp3":
            self.downoladConfigPlaylistAudio()
            return
        elif url == None and type != "mp3":
            self.downoladConfigPlaylistVideo(type)
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
                self.downloadAudioPlaylist(url)
            else:
                self.downloadVideoPlaylist(url, type)
        else:
            if type == "mp3":
                self.downloadAudio(url)
            else:
                self.downloadVideo(url, type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Program downloads mp3 form given youtube URL")
    parser.add_argument("-u", metavar="url", dest="url",
    help="Link to the youtube video")
    parser.add_argument("-t", metavar="type", dest="type", choices=['360','480', '720', '1080', '4k', 'mp3'], default="1080",
    help="Select downolad type --> ['360', '720', '1080', '2160', 'mp3'], default: 1080")
    parser.add_argument("-c", metavar="config", dest= "config", default="youtube_config.ini",
    help="Path to the config file --> default youtube_config.ini")
    args = parser.parse_args()
    url = args.url
    type = args.type
    config= args.config
    configParserMenager = ConfigParserManager(config, configparser.ConfigParser())
    metaDataMenager = MetaDataManager()
    terminalUser = TerminalUser(configParserMenager, metaDataMenager)
    terminalUser.downloadTerminal(url, type)