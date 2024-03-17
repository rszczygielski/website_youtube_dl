from mainWebPage import app, logger, youtubeDownloder, socketio, configParserMenager
from common.emits import DownloadMediaFinishEmit, MediaInfoEmit, DownloadErrorEmit
from common.youtubeDataKeys import YoutubeLogs, YoutubeVariables
import zipfile
import os
import random
import string
import yt_dlp
from flask import flash, send_file, render_template

hashTable = {}


def zipAllFilesInList(direcoryPath, playlistName, listOfFilePaths):
    # do utilsa leci
    zipFileFullPath = os.path.join(direcoryPath, playlistName)
    print(zipFileFullPath)
    with zipfile.ZipFile(f"{zipFileFullPath}.zip", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{zipFileFullPath.split('/')[-1]}.zip"


def downloadSingleInfoAndMedia(youtubeURL, type=False):
    logger.debug(YoutubeLogs.DOWNLOAD_SINGLE_VIDEO.value)
    singleMediaInfoResult = youtubeDownloder.getSingleMediaInfo(youtubeURL)
    if singleMediaInfoResult.isError():
        downloadMediaFinishEmit = DownloadMediaFinishEmit()
        errorMsg = singleMediaInfoResult.getErrorInfo()
        downloadMediaFinishEmit.sendEmitError(errorMsg)
        logger.error(f"{YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")
        return False
    mediaInfo = singleMediaInfoResult.getData()
    mediaInfoEmit = MediaInfoEmit()
    mediaInfoEmit.sendEmitSingleMedia(mediaInfo)
    fullPath = downloadSingleMedia(mediaInfo.url, mediaInfo.title, type)
    return fullPath


def downloadSingleMedia(singleMediaURL, singleMediaTitle, type):
    direcotryPath = configParserMenager.getSavePath()
    trackTitle = singleMediaTitle
    if type:
        singleMediaInfoResult = youtubeDownloder.downloadVideo(singleMediaURL, type)
        trackInfo = singleMediaInfoResult.getData()
        print(trackInfo)
        fileName = f"{trackTitle}_{type}p.{trackInfo.extension}"
    else:
        singleMediaInfoResult = youtubeDownloder.downloadAudio(singleMediaURL)
        trackInfo = singleMediaInfoResult.getData()
        fileName = f"{trackTitle}.{YoutubeVariables.MP3.value}"
    if singleMediaInfoResult.isError():
        downloadMediaFinishEmit = DownloadMediaFinishEmit()
        errorMsg = singleMediaInfoResult.getErrorInfo()
        downloadMediaFinishEmit.sendEmitError(errorMsg)
        logger.error(f"{YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")
        return False
    logger.info(f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {fileName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {direcotryPath}")
    return os.path.join(direcotryPath, fileName)


def downloadPlaylist(youtubeURL, type=False):
    logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
    singleMediaInfoResult = youtubeDownloder.getPlaylistMediaInfo(youtubeURL)
    if singleMediaInfoResult.isError():
        downloadMediaFinishEmit = DownloadMediaFinishEmit()
        errorMsg = singleMediaInfoResult.getErrorInfo()
        downloadMediaFinishEmit.sendEmitError(errorMsg)
        logger.error(f"{YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")
        return False
    playlistInfo = singleMediaInfoResult.getData()
    playlistName = playlistInfo.playlistName
    mediaInfoEmit = MediaInfoEmit()
    mediaInfoEmit.sendEmitPlaylist(playlistInfo)
    direcotryPath = configParserMenager.getSavePath()
    filePaths = []
    for track in playlistInfo.singleMediaList:
        fullPath = downloadSingleMedia(track.url, track.title, type)
        filePaths.append(fullPath)
    zipNameFile = zipAllFilesInList(direcotryPath, playlistName, filePaths)
    logger.info(f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlistName}")
    logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {direcotryPath}")
    fullZipPath = os.path.join(direcotryPath, zipNameFile)
    return fullZipPath


def emitHashWithDownloadedFile(fullFilePath):
    splitedFilePath = fullFilePath.split("/")
    fileName = splitedFilePath[-1]
    direcotryPath = "/".join(splitedFilePath[:-1])
    generatedHash = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    hashTable[generatedHash] = {YoutubeVariables.DOWNLOAD_FILE_NAME.value: fileName,
                       YoutubeVariables.DOWNLOAD_DIRECOTRY_PATH.value: direcotryPath}
    downloadMediaFinishEmit = DownloadMediaFinishEmit()
    downloadMediaFinishEmit.sendEmitWithData(generatedHash)


@socketio.on("FormData")
def socketDownloadServer(formData):
    logger.debug(formData)
    youtubeURL = formData[YoutubeVariables.YOUTUBE_URL.value]
    isPlaylist = False
    downloadErrorEmit = DownloadErrorEmit()
    if YoutubeVariables.DOWNLOAD_TYP.value not in formData:
        logger.warning(YoutubeLogs.NO_FORMAT.value)
        downloadErrorEmit.sendEmitFormatNotSpecified()
        return False
    else:
        type = formData[YoutubeVariables.DOWNLOAD_TYP.value]
        logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {type}")
    if youtubeURL == "":
        logger.warning(YoutubeLogs.NO_URL.value)
        downloadErrorEmit.sendEmitNoURL()
    elif YoutubeVariables.URL_LIST.value in youtubeURL and YoutubeVariables.URL_VIDEO.value in youtubeURL:
        logger.warning(YoutubeLogs.PLAYLIST_AND_VIDEO_HASH_IN_URL.value)
        return
    elif YoutubeVariables.URL_LIST.value in youtubeURL and YoutubeVariables.URL_VIDEO.value not in youtubeURL:
        isPlaylist = True
    if type == YoutubeVariables.MP3.value and isPlaylist:
        fullFilePath = downloadPlaylist(youtubeURL)
    if type != YoutubeVariables.MP3.value and isPlaylist:
        fullFilePath = downloadPlaylist(youtubeURL, type)
    if type == YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleInfoAndMedia(youtubeURL)
    if type != YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleInfoAndMedia(youtubeURL, type)
    if not fullFilePath:
        return False
    emitHashWithDownloadedFile(fullFilePath)


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
def downloadConfigPlaylist(empty):
    youtubeDownloder.downoladConfigPlaylistVideo(type=720)
    flash(YoutubeLogs.FLASH_CONFIG_PALYLIST.value, category="success")
    logger.info(YoutubeLogs.PLAYLIST_DOWNLAODED_CONFIG.value)


@app.route("/modify_playlist.html")
def modify_playlist_html():
    playlistList = configParserMenager.getPlaylists()
    return render_template("modify_playlist.html", playlistsNames=playlistList.keys())


@app.route("/youtube.html")
def youtube_html():
    return render_template("youtube.html")
