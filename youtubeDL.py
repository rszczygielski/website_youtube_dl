import yt_dlp
import configparser
import os
import argparse
from configParserManager import ConfigParserManager
from metaDataManager import MetaDataManager
import logging
from myLogger import Logger
from youtubeDataKeys import PlaylistInfo, MediaInfo

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

class YoutubeDL():
    def __init__(self, configManager:ConfigParserManager, metaDataMenager:MetaDataManager, ytLogger:Logger=Logger):
        self.metaDataMenager = metaDataMenager
        self.configManager = configManager
        self.ytLogger = ytLogger
        self.savePath = self.configManager.getSavePath()
        self.ydl_opts = {
        "format": "bestvideo+bestaudio",
        # 'download_archive': 'downloaded_songs.txt',
        "no-override": False,
        "logger": self.ytLogger,
        'addmetadata': True,
        }
        self.ydl_media_info_opts ={
              'format': 'best/best',
              'addmetadata': True,
              'ignoreerrors': False,
              'quiet':True
              }

    def downloadFile(self, youtubeMediaHash:str): #pragma: no_cover
        """Method used to download youtube media based on URL

        Args:
            youtubeMediaHash (str): Hash of YouTube media
            youtubeOptions (dict): YouTube options dict form init

        Returns:
            class: meta data form youtube
        """
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                return ydl.extract_info(youtubeMediaHash)
            except Exception as error:
                logger.error("Download file error")
                return str(error)

    def getDefaultOptions(self):
        """Method returns to the defualt youtubeDL options
        """
        return {
        "format": "bestvideo+bestaudio",
        # 'download_archive': 'downloaded_songs.txt',
        "no-override": False,
        "logger": self.ytLogger,
        'addmetadata': True,
        }

    def getSingleMediaInfo(self, youtubeURL):
        """Method provides youtube media info based on youtube URL without downloading it

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with Youtube info
        """
        with yt_dlp.YoutubeDL(self.ydl_media_info_opts) as ydl:
            try:
                metaData = ydl.extract_info(youtubeURL, download=False)
            except Exception as exception:
                logger.error(f"Download media info error {str(exception)}")
                return str(exception)
        singleMediaInfo = {}
        for data in MediaInfo:
            if data.value in metaData:
                if data.value == "id":
                    singleMediaInfo["hash"] = metaData[data.value]
                    continue
                singleMediaInfo[data.value] = metaData[data.value]
        return singleMediaInfo

    def getPlaylistMediaInfo(self, youtubeURL):
        """Method provides youtube playlist media info based on youtube URL without downloading it

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with Youtube info
        """
        with yt_dlp.YoutubeDL(self.ydl_media_info_opts) as ydl:
            try:
                metaData = ydl.extract_info(youtubeURL, download=False)
            except Exception as exception:
                logger.error(f"Download media info error {str(exception)}")
                return str(exception)
        playlistMediaInfo = []
        for track in metaData[PlaylistInfo.PLAYLIST_TRACKS.value]:
            essentialMetaData = {}
            for data in PlaylistInfo:
                if data.value in track:
                    if data.value == "id":
                        essentialMetaData["hash"] = track[data.value]
                        continue
                    essentialMetaData[data.value] = track[data.value]
            playlistMediaInfo.append(essentialMetaData)
        return playlistMediaInfo

    def setVideoOptions(self, type:str):
        """Method used to change and set proper

        Args:
            type (str): _description_
        """
        video_options = self.getDefaultOptions()
        video_options['format'] = f'best[height={type}][ext=mp4]+bestaudio/bestvideo+bestaudio'
        video_options['outtmpl'] = self.savePath + '/%(title)s' + f'_{type}p' + '.%(ext)s'
        self.ydl_opts = video_options

    def setAudioOptions(self):
        audio_options = self.getDefaultOptions()
        audio_options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        audio_options['outtmpl'] =  self.savePath + '/%(title)s.%(ext)s'
        self.ydl_opts = audio_options

    def downloadVideo(self, youtubeURL:str, type:str):
        """Method uded to download video type from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video meta data
        """
        self.setVideoOptions(type)
        mediaHash = self.getSingleMediaHash(youtubeURL)
        mediaInfo = self.getSingleMediaInfo(mediaHash)
        logger.info(mediaInfo)
        return self.downloadFile(mediaHash)

    def downloadVideoPlaylist(self, youtubeURL:str, type:str):
        """Method uded to download video playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video playlist meta data
        """
        self.setVideoOptions(type)
        playlistHash = self.getPlaylistHash(youtubeURL)
        mediaInfoList = self.getPlaylistMediaInfo(playlistHash)
        logger.info(mediaInfoList)
        if isinstance(mediaInfoList, str):
            return mediaInfoList
        for trackInfo in mediaInfoList:
            self.downloadFile(trackInfo["hash"])

    def downloadAudio(self, youtubeURL:str):
        """Method uded to download audio type from Youtube, convert metadata
        into mp3 format used mutagen.easyid3

        Args:
            youtubeURL (str): YouTube URL
        """
        self.setAudioOptions()
        mediaHash = self.getSingleMediaHash(youtubeURL)
        mediaInfo = self.getSingleMediaInfo(mediaHash)
        logger.info(mediaInfo)
        metaData = self.downloadFile(mediaHash)
        if isinstance(metaData, str):
            return metaData
        self.metaDataMenager.setMetaDataSingleFile(metaData, self.savePath)
        return metaData

    # def downloadAudioPlaylist(self, youtubeURL:str):
    #     """Method uded to download audio playlist from YouTube

    #     Args:
    #         youtubeURL (str): YouTube URL

    #     Returns:
    #         dict: dict with YouTube audio playlist meta data
    #     """
    #     self.setAudioOptions()
    #     playlistHash = self.getPlaylistHash(youtubeURL)
    #     metaData = self.downloadFile(playlistHash)
    #     if isinstance(metaData, str):
    #         return metaData
    #     self.metaDataMenager.setMetaDataPlaylist(metaData, self.savePath)
    #     return metaData

    def downloadAudioPlaylist(self, youtubeURL:str):
        """Method uded to download audio playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube audio playlist meta data
        """
        self.setAudioOptions()
        playlistHash = self.getPlaylistHash(youtubeURL)
        mediaInfoList = self.getPlaylistMediaInfo(playlistHash)
        logger.info(mediaInfoList)
        if isinstance(mediaInfoList, str):
            return mediaInfoList
        for trackInfo in mediaInfoList:
            metaData = self.downloadFile(trackInfo["hash"])
            self.metaDataMenager.setMetaDataSingleFile(metaData, self.savePath)

    def downoladConfigPlaylistVideo(self, type):
        """Method used to download all playlists added to cofig file - type video

        Args:
            type (str): type of the video to download, like 480p

        Returns:
            bool: True if finished successfully
        """
        playlistList = self.configManager.getUrlOfPlaylists()
        self.setVideoOptions(type)
        for playlistURL in playlistList:
            self.downloadVideoPlaylist(playlistURL, type)
        return True

    def downoladConfigPlaylistAudio(self):
        """Method used to download all playlists added to cofig file - type audo

        Returns:
            bool: True if finished successfully
        """
        playlistList = self.configManager.getUrlOfPlaylists()
        for playlistURL in playlistList:
            self.downloadAudioPlaylist(playlistURL)
        return True

    def getSingleMediaHash(self, url):
        """Method extracts single video hash from full url

        Args:
            url (str): full YouTube URL

        Raises:
            ValueError: ValueError if the URL is a playlist only

        Returns:
            str: single video hash
        """
        onlyHashesInLink = url.split("?")[1]
        numberOfEqualSign = url.count("=")
        splitedHashes = onlyHashesInLink.split("=")
        if numberOfEqualSign == 1:
            if "list=" in onlyHashesInLink:
                raise ValueError("This a playlist only - without video hash to download")
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
        """Method extracts playlist hash from full url

        Args:
            url (str): full YouTube URL

        Raises:
            ValueError: ValueError if the URL is not a playlist

        Returns:
            str: playlist hash
        """
        if not "list=" in url:
            raise ValueError("This is not a playlist")
        onlyHashesInLink = url.split("?")[1]
        numberOfEqualSign = url.count("=")
        splitedHashes = onlyHashesInLink.split("=")
        if numberOfEqualSign == 1:
            playlistHash = onlyHashesInLink[5:]
            return playlistHash
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