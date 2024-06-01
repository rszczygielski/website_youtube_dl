from mainWebPage import app, logger, youtubeDownloder, socketio, configParserMenager
from common.youtubeLogKeys import YoutubeLogs, YoutubeVariables
from common.metaDataManager import EasyID3Manager
from common.youtubeDL import SingleMedia, PlaylistMedia, MediaFromPlaylist
from common.emits import DownloadMediaFinishEmit, SingleMediaInfoEmit, PlaylistMediaInfoEmit
from flask import send_file, render_template, Blueprint
from typing import List
import zipfile
import os
import yt_dlp
import random
import string

hashTable = {}


class FlaskSingleMedia():  # pragma: no_cover
    def __init__(self, title: str, artist: str, url: str) -> None:
        self.title = title
        self.artist = artist
        self.url = url


class FlaskPlaylistMedia():  # pragma: no_cover
    def __init__(self, plyalistName: str, trackList: List[FlaskSingleMedia]) -> None:
        self.playlistName = plyalistName
        self.trackList = trackList

    @classmethod
    def initFromPlaylistMedia(cls, playlistName, trackList):
        flaskSingleMediaList = []
        for track in trackList:
            flaskSingleMediaList.append(FlaskSingleMedia(track.title,
                                                         track.artist,
                                                         track.url))
        return cls(playlistName, flaskSingleMediaList)


def zipAllFilesInList(direcoryPath, playlistName, listOfFilePaths):  # pragma: no_cover
    zipFileFullPath = os.path.join(direcoryPath,
                                   playlistName)
    with zipfile.ZipFile(f"{zipFileFullPath}.zip", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{zipFileFullPath.split('/')[-1]}.zip"


def handleError(errorMsg):  # pragma: no_cover
    downloadMediaFinishEmit = DownloadMediaFinishEmit()
    downloadMediaFinishEmit.sendEmitError(errorMsg)
    logger.error(
        f"{YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")


def downloadSingleInfoAndMedia(youtubeURL, type=False):
    logger.debug(YoutubeLogs.DOWNLOAD_SINGLE_VIDEO.value)
    singleMediaInfoResult = youtubeDownloder.requestSingleMediaInfo(youtubeURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    mediaInfo = singleMediaInfoResult.getData()
    flaskSingleMedia = FlaskSingleMedia(mediaInfo.title,
                                        mediaInfo.artist,
                                        mediaInfo.url)
    mediaInfoEmit = SingleMediaInfoEmit()
    print(dir(flaskSingleMedia))
    mediaInfoEmit.sendEmit(flaskSingleMedia)
    fullPath = downloadSingleMedia(mediaInfo.url,
                                   mediaInfo.title,
                                   type)
    return fullPath


def downloadSingleMedia(singleMediaURL, singleMediaTitle, type):
    directoryPath = configParserMenager.getSavePath()
    trackTitle = singleMediaTitle
    if type:
        singleMediaInfoResult = youtubeDownloder.downloadVideo(
            singleMediaURL, type)
        trackInfo = singleMediaInfoResult.getData()
        fileName = f"{trackTitle}_{type}p.{trackInfo.extension}"
    else:
        singleMediaInfoResult = youtubeDownloder.downloadAudio(singleMediaURL)
        fileName = f"{trackTitle}.{YoutubeVariables.MP3.value}"
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    logger.info(f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)


def downloadSingleVideo(singleMediaURL, singleMediaTitle, type):
    directoryPath = configParserMenager.getSavePath()
    trackTitle = singleMediaTitle
    singleMediaInfoResult = youtubeDownloder.downloadVideo(
            singleMediaURL, type)
    trackInfo = singleMediaInfoResult.getData()
    fileName = f"{trackTitle}_{type}p.{trackInfo.extension}"
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    logger.info(f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)


def downloadSingleAudio(singleMediaURL, singleMediaTitle):
    directoryPath = configParserMenager.getSavePath()
    trackTitle = singleMediaTitle
    singleMediaInfoResult = youtubeDownloder.downloadAudio(singleMediaURL)
    fileName = f"{trackTitle}.{YoutubeVariables.MP3.value}"
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    easyID3Manager = EasyID3Manager(title=singleMedia.title, album=singleMedia.album,
                                    artist=singleMedia.artist)
    easyID3Manager.setFilePath(directoryPath)
    easyID3Manager.saveMetaData()
    logger.info(f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)


def downloadAudioFromPlaylist(singleMediaURL, singleMediaTitle,
                                     playlistName, index):
    directoryPath = configParserMenager.getSavePath()
    trackTitle = singleMediaTitle
    singleMediaInfoResult = youtubeDownloder.downloadAudio(singleMediaURL)
    fileName = f"{trackTitle}.{YoutubeVariables.MP3.value}"
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    easyID3Manager = EasyID3Manager(title=singleMedia.title, album=singleMedia.album,
                                    artist=singleMedia.artist, playlistName=playlistName,
                                    trackNumber=index)
    easyID3Manager.setFilePath(directoryPath)
    easyID3Manager.saveMetaData()
    logger.info(f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)

def downloadTracksFromPlaylistAudio(playlistMedia:PlaylistMedia):
    playlistName = playlistMedia.playlistName
    filePaths = []
    playlistTrack: MediaFromPlaylist
    for playlistTrack, index in enumerate(playlistMedia.mediaFromPlaylistList):
        fullPath = downloadAudioFromPlaylist(singleMediaURL=playlistTrack.ytHash,
                                  singleMediaTitle=playlistTrack.title,
                                  playlistName=playlistName,
                                  index=index)
        filePaths.append(fullPath)
    return filePaths
    
def downloadTracksFromPlaylistVideo(playlistMedia:PlaylistMedia, type):
    filePaths = []
    playlistTrack: MediaFromPlaylist
    for playlistTrack in playlistMedia.mediaFromPlaylistList:
        fullPath = downloadSingleVideo(singleMediaURL=playlistTrack.ytHash,
                                       singleMediaTitle=playlistTrack.ytHash,
                                       type=type)
        filePaths.append(fullPath)
    return filePaths

def downloadPlaylist(youtubeURL, type="mp3"):
    playlistInfoEmit = DownloadMediaFinishEmit()
    logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
    playlistMediaInfoResult = youtubeDownloder.requestPlaylistMediaInfo(
        youtubeURL)
    if playlistMediaInfoResult.isError():
        errorMsg = playlistMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    playlistMedia: PlaylistMedia = playlistMediaInfoResult.getData()
    playlistName = playlistMedia.playlistName
    flaskPlaylistMedia = FlaskPlaylistMedia(playlistName,
                                            playlistMedia.MediaFromPlaylistList)
    playlistInfoEmit = PlaylistMediaInfoEmit()
    playlistInfoEmit.sendEmit(flaskPlaylistMedia)
    if type == YoutubeVariables.MP3.value:
        filePaths = downloadTracksFromPlaylistAudio(playlistMedia=playlistMedia)
    else:
        filePaths = downloadTracksFromPlaylistVideo(playlistMedia=playlistMedia,
                                                type=type)
    directoryPath = configParserMenager.getSavePath()
    zipNameFile = zipAllFilesInList(directoryPath, playlistName, filePaths)
    logger.info(f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlistName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directoryPath}")
    fullZipPath = os.path.join(directoryPath, zipNameFile)
    return fullZipPath


def generateHash():
    return ''.join(random.sample(
        string.ascii_letters + string.digits, 6))


def emitHashWithDownloadedFile(fullFilePath):
    splitedFilePath = fullFilePath.split("/")
    fileName = splitedFilePath[-1]
    directoryPath = "/".join(splitedFilePath[:-1])
    generatedHash = generateHash()
    hashTable[generatedHash] = {
        YoutubeVariables.DOWNLOAD_FILE_NAME.value: fileName,
        YoutubeVariables.DOWNLOAD_DIRECOTRY_PATH.value: directoryPath
    }
    downloadMediaFinishEmit = DownloadMediaFinishEmit()
    downloadMediaFinishEmit.sendEmit(generatedHash)


def downloadCorrectData(youtubeURL, type, isPlaylist):
    if isPlaylist:
        fullFilePath = downloadPlaylist(youtubeURL, type)
    elif type == YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleInfoAndMedia(youtubeURL)
    elif type != YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleInfoAndMedia(youtubeURL, type)
    return fullFilePath


@socketio.on("FormData")
def socketDownloadServer(formData):
    logger.debug(formData)
    youtubeURL = formData[YoutubeVariables.YOUTUBE_URL.value]
    downloadErrorEmit = DownloadMediaFinishEmit()
    if YoutubeVariables.DOWNLOAD_TYP.value not in formData:
        logger.warning(YoutubeLogs.NO_FORMAT.value)
        downloadErrorEmit.sendEmitError(YoutubeLogs.NO_FORMAT.value)
        return False
    type = formData[YoutubeVariables.DOWNLOAD_TYP.value]
    logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {type}")
    if not youtubeURL:
        logger.warning(YoutubeLogs.NO_URL.value)
        downloadErrorEmit.sendEmitError(YoutubeLogs.NO_URL.value)
        return False
    if YoutubeVariables.URL_LIST.value in youtubeURL\
            and YoutubeVariables.URL_VIDEO.value in youtubeURL:
        logger.warning(YoutubeLogs.PLAYLIST_AND_VIDEO_HASH_IN_URL.value)
        downloadErrorEmit.sendEmitError(
            YoutubeLogs.PLAYLIST_AND_VIDEO_HASH_IN_URL.value)
        return False
    isPlaylist = YoutubeVariables.URL_LIST.value in youtubeURL \
        and YoutubeVariables.URL_VIDEO.value not in youtubeURL
    fullFilePath = downloadCorrectData(youtubeURL, type,
                                       isPlaylist)
    if not fullFilePath:
        return False
    download_data = getDataDict(fullFilePath)
    genereted_hash = genereteHash()
    hashTable[genereted_hash] = download_data
    emitDownloadFinish = DownloadMediaFinishEmit()
    emitDownloadFinish.sendEmit(genereted_hash)


def getDataDict(fullFilePath):
    splitedFilePath = fullFilePath.split("/")
    fileName = splitedFilePath[-1]
    directoryPath = "/".join(splitedFilePath[:-1])
    data_dict = {"downloadFileName": fileName,
                 "downloadDirectoryPath": directoryPath}
    return data_dict


def genereteHash():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))


@app.route("/downloadFile/<name>")
def downloadFile(name):
    downloadFileName = yt_dlp.utils.sanitize_filename(
        hashTable[name][YoutubeVariables.DOWNLOAD_FILE_NAME.value])
    downloadedFilePath = hashTable[name][YoutubeVariables.DOWNLOAD_DIRECOTRY_PATH.value]
    print(downloadFileName, downloadedFilePath)
    fullPath = os.path.join(downloadedFilePath, downloadFileName)
    logger.info(YoutubeLogs.SENDING_TO_ATTACHMENT.value)
    return send_file(fullPath, as_attachment=True)


@socketio.on("downloadFromConfigFile")
def downloadConfigPlaylist(formData):
    print(formData)
    playlistName = formData["playlistToDownload"]
    logger.info(f"Selected playlist form config {playlistName}")
    playlistURL = configParserMenager.getPlaylistUrl(playlistName)
    print(playlistURL, "test")
    fullFilePath = downloadPlaylist(playlistURL)
    if not fullFilePath:
        return False
    emitHashWithDownloadedFile(fullFilePath)


@socketio.on("addPlaylist")
def addPlalistConfig(formData):
    print(formData)
    playlistName = formData["playlistName"]
    playlistURL = formData["playlistURL"]
    print(playlistName, playlistURL)
    configParserMenager.addPlaylist(playlistName, playlistURL)
    playlistList = list(configParserMenager.getPlaylists().keys())
    socketio.emit("uploadPlalists", {"data": {"plalistList": playlistList}})


@socketio.on("deletePlaylist")
def deletePlalistConfig(formData):
    playlistName = formData["playlistToDelete"]
    configParserMenager.deletePlaylist(playlistName)
    playlistList = list(configParserMenager.getPlaylists().keys())
    socketio.emit("uploadPlalists", {"data": {"plalistList": playlistList}})


@app.route("/modify_playlist.html")
def modify_playlist_html():
    playlistList = configParserMenager.getPlaylists()
    return render_template("modify_playlist.html", playlistsNames=playlistList.keys())


@app.route("/youtube.html")
def youtube_html():
    return render_template("youtube.html")
