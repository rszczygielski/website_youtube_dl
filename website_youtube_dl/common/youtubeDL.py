import yt_dlp
import configparser
import argparse
from .youtubeConfigManager import ConfigParserManager
from .easyID3Manager import EasyID3Manager
from .myLogger import Logger, LoggerClass
from .youtubeDataKeys import PlaylistInfo, MediaInfo, YoutubeOptiones
import logging

logger = logging.getLogger(__name__)


class SingleMedia():
    def __init__(self, title, album, artist, ytHash, url, extension):
        self.title = title
        self.album = album
        self.artist = artist
        self.ytHash = ytHash
        self.url = url
        self.extension = extension


class MediaFromPlaylist():
    def __init__(self, title, ytHash):
        self.title = title
        self.ytHash = ytHash


class PlaylistMedia():
    def __init__(self, playlistName, mediaFromPlaylistList: list):
        self.playlistName = playlistName
        self.mediaFromPlaylistList = mediaFromPlaylistList


class ResultOfYoutube():
    _isError = False
    _errorInfo = None
    data = None

    def __init__(self, data=None) -> None:
        self.setData(data)

    def setError(self, errorInfo: str):
        self._isError = True
        self._errorInfo = errorInfo

    def setData(self, data):
        self._data = data

    def isError(self):
        return self._isError

    def getData(self):
        if not self._isError:
            return self._data

    def getErrorInfo(self):
        if self._isError:
            return self._errorInfo


class YoutubeDL():
    titleTemplateDefault = "/%(title)s"
    titleTemplate = titleTemplateDefault

    def __init__(self, configManager: ConfigParserManager, ytLogger: LoggerClass = Logger):
        self._configManager = configManager
        self.ytLogger = ytLogger
        self._savePath = self._configManager.getSavePath()
        self._ydl_opts = {
            YoutubeOptiones.FORMAT.value: "bestvideo+bestaudio",
            # YoutubeOptiones.DOWNLOAD_ARCHIVE.value: "downloaded_songs.txt",
            YoutubeOptiones.NO_OVERRIDE.value: False,
            YoutubeOptiones.LOGGER.value: None,
            YoutubeOptiones.QUIET.value: True,
            YoutubeOptiones.ADD_META_DATA.value: True,
        }
        self._ydl_media_info_opts = {
            YoutubeOptiones.FORMAT.value: "best/best",
            YoutubeOptiones.ADD_META_DATA.value: True,
            YoutubeOptiones.IGNORE_ERRORS.value: False,
            YoutubeOptiones.QUIET.value: True,
            YoutubeOptiones.LOGGER.value: None,
        }

        self._fast_info_opts = {
            "extract_flat": "in_playlist",
            "addmetadata": True,
            "ignoreerrors": False,
            "quiet": True
        }

    def _downloadFile(self, singleMediaHash: str):
        """Method used to download youtube media based on URL

        Args:
            singleMediaHash (str): Hash of YouTube media
            youtubeOptions (dict): YouTube options dict form init

        Returns:
            class: meta data form youtube
        """
        resultOfYoutube = ResultOfYoutube()
        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            try:
                metaData = ydl.extract_info(singleMediaHash)
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(f"Download media info error {errorInfo}")
                resultOfYoutube.setError(errorInfo)
        if not resultOfYoutube.isError():
            singleMedia = self._getMedia(metaData)
            resultOfYoutube.setData(singleMedia)
        if self.titleTemplate != self.titleTemplateDefault:
            self.titleTemplate = self.titleTemplateDefault
        return resultOfYoutube

    def downloadVideo(self, youtubeURL: str, type: str) -> ResultOfYoutube:
        """Method uded to download video type from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video meta data
        """
        self._setVideoOptions(type)
        mediaHash = self._getMediaResultHash(youtubeURL)
        resultOfYoutube = self._downloadFile(mediaHash)
        if resultOfYoutube.isError():
            errorMsg = resultOfYoutube.getErrorInfo()
            logger.error(f"Download video info error: {errorMsg}")
            return resultOfYoutube
        return resultOfYoutube

    def downloadAudio(self, youtubeURL: str):
        """Method uded to download audio type from Youtube

        Args:
            youtubeURL (str): YouTube URL
        """
        self._setAudioOptions()
        mediaHash = self._getMediaResultHash(youtubeURL)
        resultOfYoutube = self._downloadFile(mediaHash)
        if resultOfYoutube.isError():
            errorMsg = resultOfYoutube.getErrorInfo()
            logger.error(f"Download audio info error: {errorMsg}")
            return resultOfYoutube
        return resultOfYoutube

    def requestPlaylistMediaInfo(self, youtubeURL) -> ResultOfYoutube:
        """Method returns meta data based on youtube url

        Args:
            youtubeURL (string): Youtube URL

        Returns:
            ResultOfYoutube: result of youtube with metadata
        """
        with yt_dlp.YoutubeDL(self._fast_info_opts) as ydl:
            try:
                metaData = ydl.extract_info(youtubeURL, download=False)
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(f"Download media info error {errorInfo}")
                resultOfYoutube = ResultOfYoutube()
                resultOfYoutube.setError(errorInfo)
                return resultOfYoutube
        playlistMedia = self._getPlaylistMedia(metaData)
        return ResultOfYoutube(playlistMedia)

    def requestSingleMediaInfo(self, youtubeURL) -> ResultOfYoutube:
        """Method provides youtube media info based on youtube URL without downloading it

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with Youtube info
        """
        youtubeHash = self._getMediaResultHash(youtubeURL)
        with yt_dlp.YoutubeDL(self._ydl_media_info_opts) as ydl:
            try:
                metaData = ydl.extract_info(youtubeHash, download=False)
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(f"Download media info error {errorInfo}")
                resultOfYoutube = ResultOfYoutube()
                resultOfYoutube.setError(errorInfo)
                return resultOfYoutube
        singleMedia = self._getMedia(metaData)
        return ResultOfYoutube(singleMedia)

    def _getDefaultOptions(self):
        """Method returns to the defualt youtubeDL options
        """
        return {
            YoutubeOptiones.FORMAT.value: "bestvideo+bestaudio",
            # YoutubeOptiones.DOWNLOAD_ARCHIVE.value: "downloaded_songs.txt",
            YoutubeOptiones.NO_OVERRIDE.value: False,
            YoutubeOptiones.LOGGER.value: None,
            YoutubeOptiones.QUIET.value: True,
            YoutubeOptiones.ADD_META_DATA.value: True,
        }

    def _getMedia(self, metaData):
        """Method sets and returns SingleMedia instance based on meta data inptu

        Args:
            metaData (dict): meta data dict

        Returns:
            SingleMedia : SingleMedia instance with all the info set up
        """
        title = album = youtube_hash = artist = url = extension = ""
        if MediaInfo.TITLE.value in metaData:
            title = yt_dlp.utils.sanitize_filename(
                metaData[MediaInfo.TITLE.value])
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
        return SingleMedia(title, album, artist,
                           youtube_hash, url, extension)

    def _getPlaylistMedia(self, metaData) -> PlaylistMedia:
        """Method sets and returns PlaylistMedia instance based on meta data inptu

        Args:
            metaData (dict): meta data dict

        Returns:
            PlaylistMedia: PlaylistMedia instance with all the info set up
        """
        mediaInfoList = []
        playlistName = ""
        if PlaylistInfo.TITLE.value in metaData:
            playlistName = metaData[PlaylistInfo.TITLE.value]
        for track in metaData[PlaylistInfo.PLAYLIST_TRACKS.value]:
            if track is None:
                continue
            title = youtube_hash = ""
            if PlaylistInfo.TITLE.value in track:
                title = yt_dlp.utils.sanitize_filename(
                    track[PlaylistInfo.TITLE.value])
            if PlaylistInfo.URL.value in track:
                youtube_hash = track[PlaylistInfo.URL.value]
            mediaFromPlaylistStruct = MediaFromPlaylist(
                title, youtube_hash)
            mediaInfoList.append(mediaFromPlaylistStruct)
        return PlaylistMedia(playlistName, mediaInfoList)

    def _setVideoOptions(self, type: str):
        """Method used to change and set proper

        Args:
            type (str): _description_
        """
        video_options = self._getDefaultOptions()
        video_options[YoutubeOptiones.FORMAT.value] = f"best[height={type}][ext=mp4]+bestaudio/bestvideo+bestaudio"
        video_options[YoutubeOptiones.OUT_TEMPLATE.value] = self._savePath + \
            self.titleTemplate + f"_{type}p" + ".%(ext)s"
        self._ydl_opts = video_options

    def _setAudioOptions(self):
        """Method sets audio options
        """
        audio_options = self._getDefaultOptions()
        audio_options["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
        audio_options["outtmpl"] = self._savePath + f"{self.titleTemplate}.%(ext)s"
        self._ydl_opts = audio_options

    def _getMediaResultHash(self, url):
        """Method extracts single video hash from full url

        Args:
            url (str): full YouTube URL

        Raises:
            ValueError: ValueError if the URL is a playlist only

        Returns:
            str: single video hash
        """
        numberOfEqualSign = url.count("=")
        if numberOfEqualSign == 0:
            return url
        onlyHashesInLink = url.split("?")[1]
        splitedHashes = onlyHashesInLink.split("=")
        if numberOfEqualSign == 1:
            if "list=" in onlyHashesInLink:
                raise ValueError(
                    "This a playlist only - without video hash to download")
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

    def setTitleTemplateOneTime(self, newTitileTemplate):
        self.titleTemplate = newTitileTemplate


class YoutubeDlConfig(YoutubeDL):
    def __init__(self, configManager: ConfigParserManager,
                 easyID3Manager: EasyID3Manager,
                 ytLogger: LoggerClass = Logger):
        super().__init__(configManager, ytLogger)
        self.easyID3Manager = easyID3Manager

    def fastDownloadAudioPlaylist(self, youtubeURL: str):
        """Method uded to download audio playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube audio playlist meta data
        """
        self._setAudioOptions()
        playlistHash = self._getPlaylistHash(youtubeURL)
        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            try:
                metaData = ydl.extract_info(playlistHash)
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(f"Download media info error {errorInfo}")
                return False
        entriesKey = PlaylistInfo.PLAYLIST_TRACKS.value
        if entriesKey not in metaData:
            logger.error(
                "Playlist dosn't have track list - no entries key in meta data")
            return False
        playlistName = metaData["title"]
        for playlistTrack in metaData[entriesKey]:
            if playlistTrack is None:
                logger.info("Track Not Found")
                continue
            directoryPath = self._configManager.getSavePath()
            title = artist = album = index = None
            if "title" in playlistTrack:
                title = playlistTrack["title"]
            if "artist" in playlistTrack:
                artist = playlistTrack["artist"]
            if "album" in playlistTrack:
                album = playlistTrack["album"]
            if "playlist_index" in playlistTrack:
                index = playlistTrack["playlist_index"]
            filePath = f"{directoryPath}/{yt_dlp.utils.sanitize_filename(playlistTrack['title'])}.mp3"
            self.easyID3Manager.setParams(filePath=filePath, title=title, album=album,
                                          artist=artist, playlistName=playlistName,
                                          trackNumber=index)
            self.easyID3Manager.saveMetaData()
        return metaData

    def fastDownloadVideoPlaylist(self, youtubeURL: str, type: str):
        """Method uded to download video playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube video playlist meta data
        """
        self._setVideoOptions(type)
        playlistHash = self._getPlaylistHash(youtubeURL)
        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            try:
                metaData = ydl.extract_info(playlistHash)
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(f"Download media info error {errorInfo}")
                return False
        return metaData

    def downoladAllConfigPlaylistsVideo(self, type):
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

    def downoladAllConfigPlaylistsAudio(self):
        """Method used to download all playlists added to cofig file - type audo

        Returns:
            bool: True if finished successfully
        """
        playlistList = self._configManager.getUrlOfPlaylists()
        for playlistURL in playlistList:
            self.fastDownloadAudioPlaylist(playlistURL)
        return True


class TerminalUser(YoutubeDL):  # pragma: no_cover
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
            self.fastDownloadVideoPlaylist(url, type)
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
            self.fastDownloadAudioPlaylist(url)
        else:
            raise ValueError(
                "Please enter 's' for single video or 'p' for playlist")

    def downloadTerminal(self, url, type):
        if url == None and type == "mp3":
            self.downoladAllConfigPlaylistsAudio()
            return
        elif url == None and type != "mp3":
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
                self.fastDownloadAudioPlaylist(url)
            else:
                self.fastDownloadVideoPlaylist(url, type)
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
    parser.add_argument("-t", metavar="type", dest="type", choices=["360", "480", "720", "1080", "4k", "mp3"], default="1080",
                        help="Select downolad type --> ['360', '720', '1080', '2160', 'mp3'], default: 1080")
    parser.add_argument("-c", metavar="config", dest="config", default="youtube_config.ini",
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