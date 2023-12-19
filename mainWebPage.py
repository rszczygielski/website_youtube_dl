from flask import Flask, flash, render_template, request
import flask
from mailManager import Mail
from youtubeDL import YoutubeDL
from metaDataManager import MetaDataManager
from configParserManager import ConfigParserManager
from youtubeDataKeys import PlaylistInfo, MediaInfo
import yt_dlp
import os
import logging
from flask_socketio import SocketIO
import myLogger
import random
import string
import zipfile

# MetaDataManager literówka poprawić

config = "youtube_config.ini"
metaDataMenager = MetaDataManager()
configParserMenager = ConfigParserManager(config)
youtubeLogger = myLogger.LoggerClass()
youtubeLogger.settings(isEmit=True, emitSkip=["minicurses.py: 111", "API", " Downloading player Downloading player"])
youtubeDownloder = YoutubeDL(configParserMenager, metaDataMenager, youtubeLogger)
mail = Mail("radek.szczygielski.trash@gmail.com")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

hashTable = {}

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Obczaić o co chodzi, mogę wpisać dokładnie to co chce i będzie działać
socketio = SocketIO(app)

# app.route jest po to aby wywołać funkcję pod tym adresem w przeglądarce
@app.route("/")
@app.route("/index.html")
@app.route('/example')
def index():
    # render_remplate daje mi odpowiedź na requesta z przeglądarki w postaci pliku HTML
    return render_template('index.html')

@app.route("/sendMail", methods=['POST'])
def sendMail():
    if request.method == "POST":
        senderInput = request.form["senderInput"]
        messageText = request.form["messageText"]
        if len(senderInput) == 0 or "@" not in senderInput:
            flash("Wrong mail adress", category="danger")
            logger.warning("No email adress or email adress not contains @")
            return render_template("mail.html")
        if len(messageText) == 0:
            flash("Wrong empty massage", category="danger")
            logger.warning("Message text empty")
            return render_template("mail.html")
        mail.sendMailFromHTML(senderInput, "Automatic mail from flask", messageText)
        flash("Mail was sucessfuly was send", category="success")
        logger.info("Email successfully sent")
    return render_template("mail.html")

@app.route("/mail.html")
def mail_html():
    mail.initialize()
    return render_template("mail.html")

def zipAllFilesInList(direcoryPath, playlistName, listOfFilePaths):
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
    direcotryPath = youtubeDownloder.savePath
    trackTitle = singleMediaTitle
    if type:
        trackInfo = youtubeDownloder.downloadVideo(singleMediaURL, type)
        fileName = f"{trackTitle}_{type}p.{trackInfo[MediaInfo.EXTENSION.value]}"
    else:
        trackInfo = youtubeDownloder.downloadAudio(singleMediaURL)
        fileName = f"{trackTitle}.mp3"
    if isinstance(trackInfo, str):
        socketio.emit("downloadMediaFinish", {"error": trackInfo})
        logger.error(f"Download media error: {trackInfo}")
        return False
    logger.info(f"Video file {MediaInfo.TITLE.value} donwloaded")
    logger.debug(f"Direcotry path: {direcotryPath}")
    return os.path.join(direcotryPath, fileName)

def downloadPlaylist(youtubeURL, type=False):
    logger.debug(f"Download playlist")
    playlistInfo = youtubeDownloder.getPlaylistMediaInfo(youtubeURL)
    if isinstance(playlistInfo, str):
        socketio.emit("downloadMediaFinish", {"error": playlistInfo})
        logger.error(f"Download playlist info error: {playlistInfo}")
        return False
    playlistTrackList = []
    playlistName = playlistInfo[0].playlist_name
    for track in playlistInfo:
        trackInfoDict = {
            PlaylistInfo.TITLE.value: track.title ,PlaylistInfo.ALBUM.value: track.album ,
            PlaylistInfo.ARTIST.value: track.artist ,PlaylistInfo.YOUTUBE_HASH.value: track.ytHash ,
            PlaylistInfo.URL.value: track.url, PlaylistInfo.PLAYLIST_INDEX.value: track.playlistIndex,
            PlaylistInfo.PLAYLIST_NAME.value: playlistName
        }
        playlistTrackList.append(trackInfoDict)
    socketio.emit("mediaInfo", {"data": playlistTrackList})
    direcotryPath = youtubeDownloder.savePath
    # playlistName = playlistInfo[0]['playlist_name']
    filePaths = []
    for track in playlistInfo:
        # fullPath = downloadSingleMedia(track[MediaInfo.URL.value], track[MediaInfo.TITLE.value], type)
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
        fullFilePath = downloadSingleInfoAndMedia(youtubeURL, type)
    if type != "mp3" and not isPlaylist:
        fullFilePath = downloadSingleInfoAndMedia(youtubeURL, type)
    if not fullFilePath:
        return False
    emitHashWithDownloadedFile(fullFilePath)

@app.route("/downloadFile/<name>")
def downloadFile(name):
    print(name)
    downloadFileName = yt_dlp.utils.sanitize_filename(hashTable[name]["downloadFileName"])
    downloadedFilePath = hashTable[name]["downloadDirectoryPath"]
    print(downloadFileName, downloadedFilePath)
    fullPath = os.path.join(downloadedFilePath, downloadFileName)
    logger.info("Sending file to download as a attachment")
    return flask.send_file(fullPath, as_attachment=True)

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

if __name__ == "__main__":
    socketio.run(app=app, debug=True, host="0.0.0.0")

