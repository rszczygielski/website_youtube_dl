import logging
from ..common.youtubeLogKeys import YoutubeLogs
from ..common.youtubeDL import SingleMedia
from ..common.easyID3Manager import EasyID3Manager
from ..common.youtubeConfigManager import ConfigParserManager
from ..common.myLogger import LoggerClass
from ..common.youtubeDL import YoutubeDL


logger = logging.getLogger(__name__)


class YoutubeHelper():
    def __init__(self):
        youtubeLogger = LoggerClass()
        self.configParserManager = ConfigParserManager()

        self.youtubeDownloder = YoutubeDL(
            self.configParserManager, youtubeLogger)

    def getYoutubeDownloaderInstance(self):
        return self.youtubeDownloder

    def downloadSingleVideo(self, singleMediaURL, videoType):
        # if sendFullEmit:
        #     if not sendEmitSingleMediaInfoFromYoutube(singleMediaURL):
        #         return None
        singleMediaInfoResult = self.youtubeDownloder.downloadVideo(
            singleMediaURL, videoType)
        if singleMediaInfoResult.isError():
            errorMsg = singleMediaInfoResult.getErrorInfo()
            # handleError(errorMsg)
            return None
        singleMedia: SingleMedia = singleMediaInfoResult.getData()
        directoryPath = self.configParserManager.getSavePath()
        logger.info(
            f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {singleMedia.file_name}")
        logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
        return singleMedia.file_name


    def downloadSingleAudio(self, singleMediaURL):
        # if not sendEmitSingleMediaInfoFromYoutube(singleMediaURL):
        #     return None
        singleMediaInfoResult = self.youtubeDownloder.downloadAudio(singleMediaURL)
        if singleMediaInfoResult.isError():
            errorMsg = singleMediaInfoResult.getErrorInfo()
            # handleError(errorMsg)
            return None
        singleMedia: SingleMedia = singleMediaInfoResult.getData()
        directoryPath = self.configParserManager.getSavePath()
        singleMedia.file_name = str(singleMedia.file_name).replace(".webm", ".mp3")
        easyID3Manager = EasyID3Manager()
        easyID3Manager.setParams(filePath=singleMedia.file_name,
                                title=singleMedia.title,
                                album=singleMedia.album,
                                artist=singleMedia.artist,
                                ytHash=singleMedia.ytHash)
        easyID3Manager.saveMetaData()
        logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
        logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
        return singleMedia.file_name


    def downloadAudioFromPlaylist(self, singleMediaURL, playlistName, index):
        singleMediaInfoResult = self.youtubeDownloder.downloadAudio(singleMediaURL)
        if singleMediaInfoResult.isError():
            errorMsg = singleMediaInfoResult.getErrorInfo()
            # handleError(errorMsg)
            return None
        singleMedia: SingleMedia = singleMediaInfoResult.getData()
        singleMedia.file_name = str(singleMedia.file_name).replace(".webm", ".mp3")
        easyID3Manager = EasyID3Manager()
        easyID3Manager.setParams(filePath=singleMedia.file_name,
                                title=singleMedia.title,
                                album=playlistName,
                                artist=singleMedia.artist,
                                ytHash=singleMedia.ytHash,
                                trackNumber=index)
        easyID3Manager.saveMetaData()
        logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
        return singleMedia.file_name

