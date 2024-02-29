from mainWebPage import app, logger, youtubeDownloder, socketio, configParserMenager
from common.youtubeDataKeys import PlaylistInfo, MediaInfo
from flask import flash, send_file, render_template, request
from common.emits import DownloadMediaFinishEmit, MediaInfoEmit, DownloadErrorEmit
import zipfile
import os
import yt_dlp

hashTable = {}

@app.route('/test.html')
def index_test():
    return "TEST"

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
    zipFileFullPath = os.path.join(direcoryPath, playlistName)
    print(zipFileFullPath)
    with zipfile.ZipFile(f"{zipFileFullPath}.zip", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{zipFileFullPath.split('/')[-1]}.zip"

def downloadSingleInfoAndMedia(youtubeURL, type=False):
    logger.debug(f"Download single video")
    singleMediaInfoResult = youtubeDownloder.getSingleMediaInfo(youtubeURL)
    if singleMediaInfoResult.isError():
        emitDownloadErrorMessage(singleMediaInfoResult.getErrorInfo(), "single media")
        return False
    mediaInfo = singleMediaInfoResult.getData()
    emitDownloadInfo(mediaInfo)
    fullPath = downloadSingleMedia(mediaInfo.url, mediaInfo.title, type)
    return fullPath

def downloadSingleMedia(singleMediaURL, singleMediaTitle, type):
    direcotryPath = configParserMenager.getSavePath()
    trackTitle = singleMediaTitle
    if type:
        singleMediaInfoResult = youtubeDownloder.downloadVideo(singleMediaURL, type)
        trackInfo = singleMediaInfoResult.getData()
        fileName = f"{trackTitle}_{type}p.{trackInfo.extension}"
    else:
        singleMediaInfoResult = youtubeDownloder.downloadAudio(singleMediaURL)
        trackInfo = singleMediaInfoResult.getData()
        fileName = f"{trackTitle}.mp3"
    if singleMediaInfoResult.isError():
        emitDownloadErrorMessage(singleMediaInfoResult.getErrorInfo(), "single media")
        return False
    logger.info(f"Video file {MediaInfo.TITLE.value} donwloaded")
    logger.debug(f"Direcotry path: {direcotryPath}")
    return os.path.join(direcotryPath, fileName)

def downloadPlaylist(youtubeURL, type=False):
    logger.debug(f"Download playlist")
    playlistMediaInfoResult = youtubeDownloder.getPlaylistMediaInfo(youtubeURL)
    if playlistMediaInfoResult.isError():
        emitDownloadErrorMessage(playlistMediaInfoResult.getErrorInfo(), "playlist")
        return False
    playlistInfo = playlistMediaInfoResult.getData()
    playlistName = playlistInfo.playlistName
    emitDownloadInfo(playlistInfo, playlistName)
    direcotryPath = configParserMenager.getSavePath()
    filePaths = []
    for track in playlistInfo.singleMediaList:
        fullPath = downloadSingleMedia(track.url, track.title, type)
        filePaths.append(fullPath)
    zipNameFile = zipAllFilesInList(direcotryPath, playlistName, filePaths)
    logger.info(f"Playlist {playlistName} donwloaded")
    logger.debug(f"Direcotry path: {direcotryPath}")
    fullZipPath = os.path.join(direcotryPath, zipNameFile)
    return fullZipPath

@socketio.on("FormData")
def socketDownloadServer(formData):
    logger.debug(formData)
    youtubeURL = formData["youtubeURL"]
    isPlaylist = False
    error_download_emit = DownloadErrorEmit()
    if "downloadType" not in formData:
        logger.warning("Format not specified")
        socketio.emit(error_download_emit.emit_msg,
                      error_download_emit.format_not_specified)
        return False
    else:
        type = formData["downloadType"]
        logger.debug(f"Specified format {type}")
    if youtubeURL == "":
        logger.warning("Youtube URL empty")
        socketio.emit(error_download_emit.emit_msg,
                      error_download_emit.empty_url)
    elif "list=" in youtubeURL and "v=" in youtubeURL:
        logger.warning("Playlist detected and video deceted, don't want what to do")
        return
    elif "list=" in youtubeURL and "v=" not in youtubeURL:
        isPlaylist = True
    if  type == "mp3" and isPlaylist:
        fullFilePath = downloadPlaylist(youtubeURL)
    if  type != "mp3" and isPlaylist:
        fullFilePath = downloadPlaylist(youtubeURL, type)
    if  type == "mp3" and not isPlaylist:
        logger.debug(f"Download single audio")
        fullFilePath = downloadSingleInfoAndMedia(youtubeURL)
    if type != "mp3" and not isPlaylist:
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
    downloadFileName = yt_dlp.utils.sanitize_filename(hashTable[name]["downloadFileName"])
    downloadedFilePath = hashTable[name]["downloadDirectoryPath"]
    print(downloadFileName, downloadedFilePath)
    fullPath = os.path.join(downloadedFilePath, downloadFileName)
    logger.info("Sending file to download as a attachment")
    return send_file(fullPath, as_attachment=True)

@socketio.on("downloadFromConfigFile")
def downloadConfigPlaylist(empty):
    logger.info("Downloading the config playlist")
    youtubeDownloder.downoladConfigPlaylistVideo(type=720)
    flash("All config playlist has been downloaded", category="success")
    logger.info("Config playlist downloaded")

@app.route("/modify_playlist.html")
def modify_playlist_html():
    playlistList = configParserMenager.getPlaylists()
    return render_template("modify_playlist.html", playlistsNames = playlistList.keys())

@app.route("/youtube.html")
def youtube_html():
    return render_template("youtube.html")
