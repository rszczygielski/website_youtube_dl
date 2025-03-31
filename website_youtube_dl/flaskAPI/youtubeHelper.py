
class YoutubeHelper():
    def __init__(self):
        pass


    def downloadSingleVideo(singleMediaURL, videoType, sendFullEmit=True):
        if sendFullEmit:
            if not sendEmitSingleMediaInfoFromYoutube(singleMediaURL):
                return None
        singleMediaInfoResult = app.youtubeDownloder.downloadVideo(
            singleMediaURL, videoType)
        if singleMediaInfoResult.isError():
            errorMsg = singleMediaInfoResult.getErrorInfo()
            handleError(errorMsg)
            return None
        singleMedia: SingleMedia = singleMediaInfoResult.getData()
        directoryPath = app.configParserManager.getSavePath()
        app.logger.info(
            f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {singleMedia.file_name}")
        app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
        return singleMedia.file_name


    def downloadSingleAudio(singleMediaURL):
        if not sendEmitSingleMediaInfoFromYoutube(singleMediaURL):
            return None
        singleMediaInfoResult = app.youtubeDownloder.downloadAudio(singleMediaURL)
        if singleMediaInfoResult.isError():
            errorMsg = singleMediaInfoResult.getErrorInfo()
            handleError(errorMsg)
            return None
        singleMedia: SingleMedia = singleMediaInfoResult.getData()
        directoryPath = app.configParserManager.getSavePath()
        singleMedia.file_name = str(singleMedia.file_name).replace(".webm", ".mp3")
        easyID3Manager = EasyID3Manager()
        easyID3Manager.setParams(filePath=singleMedia.file_name,
                                title=singleMedia.title,
                                album=singleMedia.album,
                                artist=singleMedia.artist,
                                ytHash=singleMedia.ytHash)
        easyID3Manager.saveMetaData()
        app.logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
        app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
        return singleMedia.file_name


    def downloadAudioFromPlaylist(singleMediaURL, playlistName, index):
        singleMediaInfoResult = app.youtubeDownloder.downloadAudio(singleMediaURL)
        if singleMediaInfoResult.isError():
            errorMsg = singleMediaInfoResult.getErrorInfo()
            handleError(errorMsg)
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
        app.logger.info(
            f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
        return singleMedia.file_name

