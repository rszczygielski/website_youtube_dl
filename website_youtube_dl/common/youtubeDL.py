import yt_dlp
import logging
import os
from .youtubeConfigManager import ConfigParserManager
from .easyID3Manager import EasyID3Manager
from .myLogger import Logger, LoggerClass
from .youtubeDataKeys import (PlaylistInfo,
                              MediaInfo)
from .youtubeOptions import (YoutubeDefaultOptiones,
                            YoutubeGetSingleInfoOptiones,
                            YoutubeGetPlaylistInfoOptiones,
                            YoutubeAudioOptions,
                            YoutubeVideoOptions,
                            VideoVerificationOptiones)
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys


logger = logging.getLogger(__name__)


class SingleMedia():
    def __init__(self, file_name, title, album, artist, ytHash, url, extension):
        self.file_name = file_name
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
        self._ydl_opts = YoutubeDefaultOptiones().to_dict()
        self._ydl_single_info_opts = YoutubeGetSingleInfoOptiones().to_dict()
        self._ydl_playlist_info_opts = YoutubeGetPlaylistInfoOptiones().to_dict()

    def _downloadFile(self, singleMediaHash: str, ydl_opts=None):
        """Method used to download youtube media based on URL

        Args:
            singleMediaHash (str): Hash of YouTube media
            youtubeOptions (dict): YouTube options dict form init

        Returns:
            class: meta data form youtube
        """
        if ydl_opts is None:
            ydl_opts = self._ydl_opts
        resultOfYoutube = ResultOfYoutube()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
        mediaHash = self._getMediaResultHash(youtubeURL)
        videoOptions = self._getVideoOptions(type)
        resultOfYoutube = self._downloadFile(mediaHash, videoOptions)
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
        mediaHash = self._getMediaResultHash(youtubeURL)
        ydl_opts = self._getAudioOptions()
        resultOfYoutube = self._downloadFile(mediaHash, ydl_opts)
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
        with yt_dlp.YoutubeDL(self._ydl_playlist_info_opts) as ydl:
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
        with yt_dlp.YoutubeDL(self._ydl_single_info_opts) as ydl:
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

    def verifyLocalFiles(self, dirPath: str):
        """Method verifies if the local files still exists on YouTube

        Args:
            dirPath (str): path to file directory

        Returns:
            list: List of files which weren't verified, so those which are no longer present on YouTube
        """
        notVerifiedFiles = []
        listOfFiles = os.listdir(dirPath)
        for fileName in listOfFiles:
            fullFilePath = os.path.join(dirPath, fileName)
            if not os.path.isfile(fullFilePath) or not fullFilePath.endswith(".mp3"):
                continue
            audioManager = EasyID3Manager.initFromFileMetaData(fullFilePath)
            if not self.ifVideoExistOnYoutube(audioManager.website):
                notVerifiedFiles.append(fullFilePath)
        return notVerifiedFiles

    def ifQueryExistOnYoutube(self, ytHash: str):  # pragma: no_cover
        """Method checks if given query exists on YouTube, methos uses yt-dlp package

        Args:
            ytHash (str): query for to search YouTube

        Returns:
            bool: True if video exists, False if video not exists on YouTube
        """

        ydl_opts = VideoVerificationOptiones().to_dict()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info(ytHash, download=False)
                logger.error(f"Video with {ytHash} exists on YouTube")
                return True
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(
                    f"Video might be deleted from YouTube error: {errorInfo}")
                return False

    def ifVideoExistOnYoutube(self, ytHash: str):  # pragma: no_cover
        """Method checks if given YouTube video hash exists on YouTube, methos uses yt-dlp package

        Args:
            ytHash (str): YouTube video hash for YouTube search

        Returns:
            bool: True if video exists, False if video not exists on YouTube
        """

        ydl_opts = VideoVerificationOptiones().to_dict()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info(ytHash, download=False)
                logger.error(f"Video with {ytHash} exists on YouTube")
                return True
            except Exception as exception:
                errorInfo = str(exception)
                logger.error(
                    f"Video might be deleted from YouTube error: {errorInfo}")
                return False

    def _getMedia(self, metaData):
        """Method sets and returns SingleMedia instance based on meta data inptu

        Args:
            metaData (dict): meta data dict

        Returns:
            SingleMedia : SingleMedia instance with all the info set up
        """
        full_path = title = album = youtube_hash = artist = url = extension = ""
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
        if MainYoutubeKeys.REQUESTED_DOWNLOADS.value in metaData:
            requested_downloads = metaData[MainYoutubeKeys.REQUESTED_DOWNLOADS.value][0]
            if MainYoutubeKeys.FUL_PATH.value in requested_downloads:
                full_path = requested_downloads[MainYoutubeKeys.FUL_PATH.value]
        return SingleMedia(full_path, title, album, artist,
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

    def _getVideoOptions(self, type: str):
        """Method used to change and set proper

        Args:
            type (str): _description_
        """
        out_template = self._savePath + \
            self.titleTemplate + f"_{type}p" + ".%(ext)s"
        video_options_instance = YoutubeVideoOptions(out_template)
        video_options_instance.change_format(type, "mp4")
        return video_options_instance.to_dict()

    def _getAudioOptions(self):
        """Method sets audio options
        """
        out_template = self._savePath + \
            f"{self.titleTemplate}.%(ext)s"
        audio_options_instance = YoutubeAudioOptions(out_template)
        return audio_options_instance.to_dict()

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


class YoutubeDlPlaylists(YoutubeDL):
    def __init__(self, configManager: ConfigParserManager,
                 easyID3Manager: EasyID3Manager,
                 ytLogger: LoggerClass = Logger):
        super().__init__(configManager, ytLogger)
        self.easyID3Manager = easyID3Manager

    def downloadWholeAudioPlaylist(self, youtubeURL: str):
        """Method uded to download audio playlist from YouTube

        Args:
            youtubeURL (str): YouTube URL

        Returns:
            dict: dict with YouTube audio playlist meta data
        """
        playlistHash = self._getPlaylistHash(youtubeURL)
        ydl_opts = self._getAudioOptions()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
        playlistName = metaData[PlaylistInfo.TITLE.value]
        for playlistTrack in metaData[entriesKey]:
            if playlistTrack is None:
                logger.info("Track Not Found")
                continue
            directoryPath = self._configManager.getSavePath()
            title = artist = album = index = None
            if PlaylistInfo.TITLE.value in playlistTrack:
                title = playlistTrack[PlaylistInfo.TITLE.value]
            if PlaylistInfo.ARTIST.value in playlistTrack:
                artist = playlistTrack[PlaylistInfo.ARTIST.value]
            if PlaylistInfo.ALBUM.value in playlistTrack:
                album = playlistTrack[PlaylistInfo.TITLE.value]
            if PlaylistInfo.PLAYLIST_INDEX.value in playlistTrack:
                index = playlistTrack[PlaylistInfo.PLAYLIST_INDEX.value]
            filePath = f"{directoryPath}/{yt_dlp.utils.sanitize_filename(playlistTrack['title'])}.mp3"
            self.easyID3Manager.setParams(filePath=filePath,
                                          title=title,
                                          album=album,
                                          artist=artist,
                                          playlistName=playlistName,
                                          trackNumber=index)
            self.easyID3Manager.saveMetaData()
        return metaData

    def downloadWholeVideoPlaylist(self, youtubeURL: str, type: str):
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
            self.downloadWholeVideoPlaylist(playlistURL, type)
        return True

    def downoladAllConfigPlaylistsAudio(self):
        """Method used to download all playlists added to cofig file - type audo

        Returns:
            bool: True if finished successfully
        """
        playlistList = self._configManager.getUrlOfPlaylists()
        for playlistURL in playlistList:
            self.downloadWholeAudioPlaylist(playlistURL)
        return True
