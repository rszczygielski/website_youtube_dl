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

class FlaskMediaFromPlaylist():
    def __init__(self, title, url):
        self.title = title
        self.url = url

class FlaskPlaylistMedia():  # pragma: no_cover
    def __init__(self, plyalistName: str, trackList: List[FlaskMediaFromPlaylist]) -> None:
        self.playlistName = plyalistName
        self.trackList = trackList

    @classmethod
    def initFromPlaylistMedia(cls, playlistName, trackList):
        flaskSingleMediaList = []
        for track in trackList:
            flaskSingleMediaList.append(FlaskMediaFromPlaylist(track.title,
                                                                track.ytHash))
        return cls(playlistName, flaskSingleMediaList)

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
    # if YoutubeVariables.URL_LIST.value in youtubeURL\
    #         and YoutubeVariables.URL_VIDEO.value in youtubeURL:
    #     logger.warning(YoutubeLogs.PLAYLIST_AND_VIDEO_HASH_IN_URL.value)
    #     downloadErrorEmit.sendEmitError(
    #         YoutubeLogs.PLAYLIST_AND_VIDEO_HASH_IN_URL.value)
    #     return False
    isPlaylist = YoutubeVariables.URL_LIST.value in youtubeURL \
        and YoutubeVariables.URL_VIDEO.value not in youtubeURL
    fullFilePath = downloadCorrectData(youtubeURL, type,
                                       isPlaylist)
    if not fullFilePath:
        return False
    download_data = getDataDict(fullFilePath)
    genereted_hash = generateHash()
    hashTable[genereted_hash] = download_data
    emitDownloadFinish = DownloadMediaFinishEmit()
    emitDownloadFinish.sendEmit(genereted_hash)

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

def downloadCorrectData(youtubeURL, type, isPlaylist):
    if  type == YoutubeVariables.MP3.value and isPlaylist:
        fullFilePath = downloadTracksFromPlaylistAudio(youtubeURL)
    elif type != YoutubeVariables.MP3.value and isPlaylist:
        fullFilePath = downloadTracksFromPlaylistVideo(youtubeURL, type)
    elif type == YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleAudio(youtubeURL)
    elif type != YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleVideo(youtubeURL, type)
    return fullFilePath

def downloadSingleVideo(singleMediaURL, type):
    if not requestSingleUrlInfo(singleMediaURL):
        return
    singleMediaInfoResult = youtubeDownloder.downloadVideo(
            singleMediaURL, type)
    trackInfo = singleMediaInfoResult.getData()
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    directoryPath = configParserMenager.getSavePath()
    fileName = f"{trackInfo.title}_{type}p.{trackInfo.extension}"
    logger.info(f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)

def downloadSingleAudio(singleMediaURL):
    if not requestSingleUrlInfo(singleMediaURL):
        return
    singleMediaInfoResult = youtubeDownloder.downloadAudio(singleMediaURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    directoryPath = configParserMenager.getSavePath()
    filePath = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(singleMedia.title)}.mp3'
    easyID3Manager = EasyID3Manager(fileFullPath=filePath)
    easyID3Manager.setParams(title=singleMedia.title, album=singleMedia.album,
                            artist=singleMedia.artist)
    easyID3Manager.saveMetaData()
    fileName = f"{singleMedia.title}.{YoutubeVariables.MP3.value}"
    logger.info(f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)

def downloadAudioFromPlaylist(singleMediaURL, playlistName, index):
    directoryPath = configParserMenager.getSavePath()
    singleMediaInfoResult = youtubeDownloder.downloadAudio(singleMediaURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    filePath = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(singleMedia.title)}.mp3'
    easyID3Manager = EasyID3Manager(fileFullPath=filePath)
    easyID3Manager.setParams(title=singleMedia.title, album=singleMedia.album,
                            artist=singleMedia.artist, playlistName=playlistName,
                            trackNumber=index)
    easyID3Manager.saveMetaData()
    fileName = f"{singleMedia.title}.{YoutubeVariables.MP3.value}"
    logger.info(f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    # dorobić emint
    return os.path.join(directoryPath, fileName)

def downloadTracksFromPlaylistVideo(youtubeURL, type):
    playlistMedia = requestYoutubePlaylistUrlInfo(youtubeURL)
    if not playlistMedia:
        return
    filePaths = []
    playlistTrack: MediaFromPlaylist
    for playlistTrack in playlistMedia.mediaFromPlaylistList:
        fullPath = downloadSingleVideo(singleMediaURL=playlistTrack.ytHash,
                                       type=type)
        filePaths.append(fullPath)
    directoryPath = configParserMenager.getSavePath()
    zipNameFile = zipAllFilesInList(directoryPath, playlistMedia.playlistName, filePaths)
    logger.info(f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlistMedia.playlistName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directoryPath}")
    fullZipPath = os.path.join(directoryPath, zipNameFile)
    return fullZipPath

def downloadTracksFromPlaylistAudio(youtubeURL):
    playlistMedia = requestYoutubePlaylistUrlInfo(youtubeURL)
    if not playlistMedia:
        return
    filePaths = []
    playlistTrack: FlaskMediaFromPlaylist
    for index, playlistTrack in enumerate(playlistMedia.mediaFromPlaylistList):
        fullPath = downloadAudioFromPlaylist(singleMediaURL=playlistTrack.ytHash,
                                  playlistName=playlistMedia.playlistName,
                                  index=str(index))
        filePaths.append(fullPath)
    directoryPath = configParserMenager.getSavePath()
    zipNameFile = zipAllFilesInList(directoryPath, playlistMedia.playlistName, filePaths)
    logger.info(f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlistMedia.playlistName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directoryPath}")
    fullZipPath = os.path.join(directoryPath, zipNameFile)
    return fullZipPath

def requestSingleUrlInfo(singleMediaURL):
    singleMediaInfoResult = youtubeDownloder.requestSingleMediaInfo(singleMediaURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    mediaInfo = singleMediaInfoResult.getData()
    flaskSingleMedia = FlaskSingleMedia(mediaInfo.title,
                                        mediaInfo.artist,
                                        mediaInfo.url)
    mediaInfoEmit = SingleMediaInfoEmit()
    mediaInfoEmit.sendEmit(flaskSingleMedia)
    return True

def requestYoutubePlaylistUrlInfo(youtubeURL):
    logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
    playlistMediaInfoResult = youtubeDownloder.requestPlaylistMediaInfo(
        youtubeURL)
    if playlistMediaInfoResult.isError():
        errorMsg = playlistMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return None
    playlistMedia: PlaylistMedia = playlistMediaInfoResult.getData()
    playlistName = playlistMedia.playlistName
    flaskPlaylistMedia = FlaskPlaylistMedia.initFromPlaylistMedia(playlistName,
                                            playlistMedia.mediaFromPlaylistList)
    playlistInfoEmit = PlaylistMediaInfoEmit()
    playlistInfoEmit.sendEmit(flaskPlaylistMedia)
    return playlistMedia

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

def generateHash():
    return ''.join(random.sample(
        string.ascii_letters + string.digits, 6))

def getDataDict(fullFilePath):
    splitedFilePath = fullFilePath.split("/")
    fileName = splitedFilePath[-1]
    directoryPath = "/".join(splitedFilePath[:-1])
    data_dict = {"downloadFileName": fileName,
                 "downloadDirectoryPath": directoryPath}
    return data_dict

