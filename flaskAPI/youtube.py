from mainWebPage import app, logger, youtubeDownloder, socketio, configParserMenager
from common.youtubeDataKeys import PlaylistInfo, MediaInfo
import zipfile
import os
import random
import string
import yt_dlp
from flask import flash, send_file, render_template

hashTable = {}

@app.route('/test.html')
def index_test():
    return "TEST"

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
        socketio.emit("downloadMediaFinish", {"error": singleMediaInfoResult.getErrorInfo()})
        logger.error(f"Download media info error: {singleMediaInfoResult.getErrorInfo()}")
        return False
    mediaInfo = singleMediaInfoResult.getData()
    mediaInfoDict = {
        PlaylistInfo.TITLE.value: mediaInfo.title ,PlaylistInfo.ALBUM.value: mediaInfo.album ,
        PlaylistInfo.ARTIST.value: mediaInfo.artist ,PlaylistInfo.YOUTUBE_HASH.value: mediaInfo.ytHash ,
        PlaylistInfo.URL.value: mediaInfo.url
    }
    socketio.emit("mediaInfo", {"data": [mediaInfoDict]})
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
        socketio.emit("downloadMediaFinish", {"error": trackInfo})
        logger.error(f"Download media error: {trackInfo}")
        return False
    logger.info(f"Video file {MediaInfo.TITLE.value} donwloaded")
    logger.debug(f"Direcotry path: {direcotryPath}")
    return os.path.join(direcotryPath, fileName)

def downloadPlaylist(youtubeURL, type=False):
    logger.debug(f"Download playlist")
    singleMediaInfoResult = youtubeDownloder.getPlaylistMediaInfo(youtubeURL)
    if singleMediaInfoResult.isError():
        socketio.emit("downloadMediaFinish", {"error": singleMediaInfoResult.getErrorInfo()})
        logger.error(f"Download playlist info error: {singleMediaInfoResult.getErrorInfo()}")
        return False
    playlistTrackList = []
    playlistInfo = singleMediaInfoResult.getData()
    playlistName = playlistInfo.playlistName
    for track in playlistInfo.singleMediaList:
        trackInfoDict = {
            PlaylistInfo.TITLE.value: track.title, PlaylistInfo.ALBUM.value: track.album ,
            PlaylistInfo.ARTIST.value: track.artist ,PlaylistInfo.YOUTUBE_HASH.value: track.ytHash ,
            PlaylistInfo.URL.value: track.url, PlaylistInfo.PLAYLIST_INDEX.value: track.playlistIndex,
            PlaylistInfo.PLAYLIST_NAME.value: playlistName
        }
        playlistTrackList.append(trackInfoDict)
    socketio.emit("mediaInfo", {"data": playlistTrackList})
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

def emitHashWithDownloadedFile(fullFilePath):
    splitedFilePath = fullFilePath.split("/")
    fileName = splitedFilePath[-1]
    direcotryPath = "/".join(splitedFilePath[:-1])
    hash = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    hashTable[hash] = {"downloadFileName": fileName, "downloadDirectoryPath": direcotryPath}
    socketio.emit("downloadMediaFinish", {"data": {"HASH": hash}})

@socketio.on("FormData")
def socketDownloadServer(formData):
    logger.debug(formData)
    youtubeURL = formData["youtubeURL"]
    isPlaylist = False
    if "downloadType" not in formData:
        logger.warning("Format not specified")
        socketio.emit("downloadError", "Format not specified")
        return False
    else:
        type = formData["downloadType"]
        logger.debug(f"Specified format {type}")
    if youtubeURL == "":
        logger.warning("Youtube URL empty")
        socketio.emit("downloadError", "Youtube URL empty")
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
    emitHashWithDownloadedFile(fullFilePath)

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
