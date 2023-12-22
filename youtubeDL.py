import yt_dlp
import configparser
import os
import argparse
from configParserManager import ConfigParserManager
from metaDataManager import MetaDataManager
import logging
from myLogger import Logger
from youtubeDataKeys import PlaylistInfo, MediaInfo, YoutubeOptiones

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SingleMedia():
    def __init__(self, title, album, artist, ytHash, url, extension, playlistIndex=None):
        self.title = title
        self.album = album
        self.artist = artist
        self.ytHash = ytHash
        self.url = url
        self.extension = extension
        self.playlistIndex = playlistIndex

class PlaylistMedia():
    def __init__(self, playlistName, singleMediaList:list):
        self.playlistName = playlistName
        self.singleMediaList = singleMediaList

class ResultOfYoutube():
    _isError = False
    _errorInfo = None

    def __init__(self, data=None) -> None:
        self._data = data

    def setError(self, errorInfo:str):
        self._isError = True
        self._errorInfo = errorInfo

    def setData(self, data):
        self._data = data

    def isError(self):
        if self._isError:
            return True

    def getData(self):
        if not self._isError:
            return self._data

    def getErrorInfo(self):
        if self._isError:
            return self._errorInfo

class YoutubeDL():
    def __init__(self, configManager:ConfigParserManager, metaDataMenager:MetaDataManager, ytLogger:Logger=Logger):
        self._metaDataMenager = metaDataMenager
        self._configManager = configManager
        self.ytLogger = ytLogger
        self._savePath = self._configManager.getSavePath()
        self._ydl_opts = {
        YoutubeOptiones.FORMAT.value: "bestvideo+bestaudio",
        # YoutubeOptiones.DOWNLOAD_ARCHIVE.value: 'downloaded_songs.txt',
        YoutubeOptiones.NO_OVERRIDE.value: False,
        YoutubeOptiones.LOGGER.value: self.ytLogger,
        YoutubeOptiones.ADD_META_DATA.value: True,
        }
        self._ydl_media_info_opts ={
            YoutubeOptiones.FORMAT.value: 'best/best',
            YoutubeOptiones.ADD_META_DATA.value: True,
            YoutubeOptiones.IGNORE_ERRORS.value: False,
            YoutubeOptiones.QUIET.value: True
            }

    def _downloadFile(self, youtubeMediaHash:str): #pragma: no_cover
        """Method used to download youtube media based on URL

        Args:
            youtubeMediaHash (str): Hash of YouTube media
            youtubeOptions (dict): YouTube options dict form init

        Returns:
            class: meta data form youtube
        """
        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            try:
                return ydl.extract_info(youtubeMediaHash)
            except Exception as error:
                logger.error("Download file error")
                return str(error)

    def _getDefaultOptions(self):
        """Method returns to the defualt youtubeDL options
        """
        return {
        YoutubeOptiones.FORMAT.value: "bestvideo+bestaudio",
        # YoutubeOptiones.DOWNLOAD_ARCHIVE.value: 'downloaded_songs.txt',
        YoutubeOptiones.NO_OVERRIDE.value: False,
        YoutubeOptiones.LOGGER.value: self.ytLogger,
        YoutubeOptiones.ADD_META_DATA.value: True,
        }

    def _getSingleMediaResult(self, metaData):
        title = album = youtube_hash = artist = url = extension = ""
        if MediaInfo.TITLE.value in metaData:
            title = yt_dlp.utils.sanitize_filename(metaData[MediaInfo.TITLE.value])
        if MediaInfo.ALBUM.value in metaData:
            album = metaData[MediaInfo.ALBUM.value]
        if MediaInfo.ARTIST.value in metaData:
            artist = metaData[MediaInfo.ARTIST.value]
        if MediaInfo.YOUTUBE_HASH.value in metaData:
            youtube_hash = metaData[MediaInfo.YOUTUBE_HASH.value]
        if MediaInfo.URL.value in metaData:
            url = metaData[MediaInfo.URL.value]
        if MediaInfo.EXTENSION.value in metaData:
            extension = metaData[MediaInfo.EXTENSION.value]
        return SingleMedia(title, album, artist, youtube_hash, url, extension)


    def _getPlaylistMediaResult(self, metaData):
        mediaInfoList = []
        playlistName = ""
        if PlaylistInfo.TITLE.value in metaData:
            playlistName = metaData[PlaylistInfo.TITLE.value]
        for track in metaData[PlaylistInfo.PLAYLIST_TRACKS.value]:
            title = album = youtube_hash = artist = url = extension = playlistIndex = ""
            if PlaylistInfo.TITLE.value in track:
                title = yt_dlp.utils.sanitize_filename(track[PlaylistInfo.TITLE.value])
            if PlaylistInfo.ALBUM.value in track:
                album = track[PlaylistInfo.ALBUM.value]
            if PlaylistInfo.ARTIST.value in track:
                artist = track[PlaylistInfo.ARTIST.value]
            if PlaylistInfo.YOUTUBE_HASH.value in track:
                youtube_hash = track[PlaylistInfo.YOUTUBE_HASH.value]
            if PlaylistInfo.URL.value in track:
                url = track[MediaInfo.URL.value]
            if PlaylistInfo.PLAYLIST_INDEX.value in track:
                playlistIndex = track[PlaylistInfo.PLAYLIST_INDEX.value]
            if PlaylistInfo.EXTENSION.value in metaData:
                extension = metaData[PlaylistInfo.EXTENSION.value]
            singleMediaStruct = SingleMedia(title, album, artist, youtube_hash, url, extension, playlistIndex)
            mediaInfoList.append(singleMediaStruct)
        return PlaylistMedia(playlistName, mediaInfoList)

    def getSingleMediaInfo(self, youtubeURL) -> ResultOfYoutube:
        """Method provides youtube media info based on youtube URL without downloading it

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with Youtube info
        """
        with yt_dlp.YoutubeDL(self._ydl_media_info_opts) as ydl:
            try:
                metaData = ydl.extract_info(youtubeURL, download=False)
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(f"Download media info error {errorInfo}")
                return ResultOfYoutube.setError(errorInfo)
        singleMedia = self._getSingleMediaResult(metaData)
        return ResultOfYoutube(singleMedia)

    def getPlaylistMediaInfo(self, youtubeURL) -> ResultOfYoutube:
        with yt_dlp.YoutubeDL(self._ydl_media_info_opts) as ydl:
            try:
                metaData = ydl.extract_info(youtubeURL, download=False)
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(f"Download media info error {errorInfo}")
                return ResultOfYoutube.setError(errorInfo)
        playlistMedia = self._getPlaylistMediaResult(metaData)
        return ResultOfYoutube(playlistMedia)

    def _setVideoOptions(self, type:str):
        """Method used to change and set proper

        Args:
            type (str): _description_
        """
        video_options = self._getDefaultOptions()
        video_options[YoutubeOptiones.FORMAT.value] = f'best[height={type}][ext=mp4]+bestaudio/bestvideo+bestaudio'
        video_options[YoutubeOptiones.OUT_TEMPLATE.value] = self._savePath + '/%(title)s' + f'_{type}p' + '.%(ext)s'
        self._ydl_opts = video_options

    def _setAudioOptions(self):
        audio_options = self._getDefaultOptions()
        audio_options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        audio_options['outtmpl'] =  self._savePath + '/%(title)s.%(ext)s'
        self._ydl_opts = audio_options

    def downloadVideo(self, youtubeURL:str, type:str) -> ResultOfYoutube:
        """Method uded to download video type from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video meta data
        """
        self._setVideoOptions(type)
        mediaHash = self._getSingleMediaHash(youtubeURL)
        singleMediaInfoResult = self.getSingleMediaInfo(mediaHash)
        if singleMediaInfoResult.isError():
            logger.error(f"Download video info error: {singleMediaInfoResult.getErrorInfo()}")
            return True
        mediaInfo = singleMediaInfoResult.getData()
        logger.info(mediaInfo)
        metaData = self._downloadFile(mediaInfo.ytHash)
        singleMedia = self._getSingleMediaResult(metaData)
        return ResultOfYoutube(singleMedia)

    def fastDownloadVideoPlaylist(self, youtubeURL:str, type:str):
        """Method uded to download video playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video playlist meta data
        """
        self._setVideoOptions(type)
        playlistHash = self._getPlaylistHash(youtubeURL)
        return self._downloadFile(playlistHash)

    def downloadAudio(self, youtubeURL:str):
        """Method uded to download audio type from Youtube, convert metadata
        into mp3 format used mutagen.easyid3

        Args:
            youtubeURL (str): YouTube URL
        """
        self._setAudioOptions()
        mediaHash = self._getSingleMediaHash(youtubeURL)
        singleMediaInfoResult = self.getSingleMediaInfo(mediaHash)
        if singleMediaInfoResult.isError():
            logger.error(f"Download audio info error: {singleMediaInfoResult.getErrorInfo()}")
            return True
        mediaInfo = singleMediaInfoResult.getData()
        logger.info(mediaInfo)
        metaData = self._downloadFile(mediaHash)
        self._metaDataMenager.setMetaDataSingleFile(metaData, self._savePath)
        singleMedia = self._getSingleMediaResult(metaData)
        return ResultOfYoutube(singleMedia)

    def downloadWholeAudioPlaylist(self, youtubeURL:str):
        """Method uded to download audio playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube audio playlist meta data
        """
        self._setAudioOptions()
        playlistHash = self._getPlaylistHash(youtubeURL)
        playlistMediaInfoResult = self.getPlaylistMediaInfo(playlistHash)
        if playlistMediaInfoResult.isError():
            logger.error(f"Download audio playlist info error: {playlistMediaInfoResult.getErrorInfo()}")
            return True
        playlistMediaInfo = playlistMediaInfoResult.getData()
        playlistMediaList = playlistMediaInfo.singleMediaList
        for trackInfo in playlistMediaList:
            metaData = self._downloadFile(trackInfo.ytHash)
            self._metaDataMenager.setMetaDataSingleFile(metaData, self._savePath)

    def downoladConfigPlaylistVideo(self, type):
        """Method used to download all playlists added to cofig file - type video

        Args:
            type (str): type of the video to download, like 480p

        Returns:
            bool: True if finished successfully
        """
        playlistList = self._configManager.getUrlOfPlaylists()
        self._setVideoOptions(type)
        for playlistURL in playlistList:
            self.fastDownloadVideoPlaylist(playlistURL, type)
        return True

    def downoladConfigPlaylistAudio(self):
        """Method used to download all playlists added to cofig file - type audo

        Returns:
            bool: True if finished successfully
        """
        playlistList = self._configManager.getUrlOfPlaylists()
        for playlistURL in playlistList:
            self.downloadWholeAudioPlaylist(playlistURL)
        return True

    def _getSingleMediaHash(self, url):
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

    def _getPlaylistHash(self, url):
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
            self.fastDownloadVideoPlaylist(url, type)
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
            self.downloadWholeAudioPlaylist(url)
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
                self.downloadWholeAudioPlaylist(url)
            else:
                self.fastDownloadVideoPlaylist(url, type)
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