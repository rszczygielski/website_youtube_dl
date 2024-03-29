from mainWebPage import app, logger, youtubeDownloder, socketio, configParserMenager
from common.youtubeDataKeys import YoutubeLogs, YoutubeVariables
from flask import flash, send_file, render_template, request
from common.emits import DownloadMediaFinishEmit, MediaInfoEmit, DownloadErrorEmit, PlaylistMediaInfoEmit
import zipfile
import os
import yt_dlp
import random
import string
from flask import send_file, render_template

hashTable = {}

class FlaskSingleMedia():
    def __init__(self, title, artist, url) -> None:
        self.title = title
        self.artist = artist
        self.url = url

def emitDownloadErrorMessage(error_msg, mediaType):
    emit_download_finish = DownloadMediaFinishEmit()
    socketio.emit(emit_download_finish.emit_msg,
                    emit_download_finish.convert_error_to_message(error_msg))
    logger.error(f"Download {mediaType} info error: {error_msg}")

def emitDownloadInfo(metaDataInfo, playlistName=None):
    emit_media_info = MediaInfoEmit()
    print(metaDataInfo)
    if not playlistName:
        socketio.emit(emit_media_info.emit_msg,
        emit_media_info.convert_data_to_message(metaDataInfo))
    else:
        socketio.emit(emit_media_info.emit_msg,
                emit_media_info.convert_playlist_data_to_message(metaDataInfo,
                                                                playlistName))

def zipAllFilesInList(direcoryPath, playlistName, listOfFilePaths):
    # do utilsa leci
    zipFileFullPath = os.path.join(direcoryPath, 
                                   playlistName)
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
        logger.error(
            f"{YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")
        return False
    mediaInfo = singleMediaInfoResult.getData()
    flaskSingleMedia = FlaskSingleMedia(mediaInfo.title,
                                        mediaInfo.artist, mediaInfo.url)
    mediaInfoEmit = MediaInfoEmit()
    mediaInfoEmit.sendEmitSingleMedia(flaskSingleMedia)
    fullPath = downloadSingleMedia(mediaInfo.url, mediaInfo.title, type)
    return fullPath


def downloadSingleMedia(singleMediaURL, singleMediaTitle, type):
    direcotryPath = configParserMenager.getSavePath()
    trackTitle = singleMediaTitle
    if type:
        singleMediaInfoResult = youtubeDownloder.downloadVideo(
            singleMediaURL, type)
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
        downloadMediaFinishEmit.send_emit_error(errorMsg)
        logger.error(
            f"{YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")
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
        downloadMediaFinishEmit.send_emit_error(errorMsg)
        logger.error(
            f"{YoutubeLogs.PLAYLIST_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")
        return False
    playlistInfo = singleMediaInfoResult.getData()
    playlistName = playlistInfo.playlistName
    playlistInfoEmit = PlaylistMediaInfoEmit()
    playlistInfoEmit.send_emit(playlistInfo, playlistName)
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
    generatedHash = ''.join(random.sample(
        string.ascii_letters + string.digits, 6))
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
    emit_download_finish = DownloadMediaFinishEmit()
    download_data = emit_download_finish.get_data_dict(fullFilePath)
    hashTable[emit_download_finish.genereted_hash] = download_data
    socketio.emit(emit_download_finish.emit_msg,
                  emit_download_finish.convert_data_to_message())

@app.route("/modify_playlist", methods=["POST", "GET"])
def modify_playlist():
    if request.method == "POST":
        playlistList = configParserMenager.getPlaylists()
        playlistName = request.form["playlistName"]
        if "AddPlaylistButton" in request.form:
            playlistURL = request.form["playlistURL"]
            if "list=" not in playlistURL:
                flash("Please enter correct URL of YouTube playlist", category="danger")
                logger.warning("URL not containing list=")
                return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
            configParserMenager.addPlaylist(playlistName, playlistURL)
            playlistList = configParserMenager.getPlaylists()
            flash(f"Playlist {playlistName} added to config file", category="success")
            logger.info(f"Config file updated with new playlist: {playlistName}")
            return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
        elif "DeletePlaylistButton" in request.form:
            if "playlistSelect" in request.form:
                playlistToRemove = request.form["playlistSelect"]
                configParserMenager.deletePlaylist(playlistToRemove)
                playlistList = configParserMenager.getPlaylists()
                flash(f"Playlist {playlistToRemove} deleted from config file", category="success")
                logger.info(f"Playlist {playlistName} deleted from config file")
                return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
            else:
                flash("Select a playlist to delete", category="danger")
                logger.info(f"None playlist was selected to deleted from config file")
                return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
        else:
            raise Exception("Undefined behaviour")


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
