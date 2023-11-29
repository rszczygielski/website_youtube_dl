from flask import Flask, flash, render_template, request
import flask
from mailManager import Mail
from youtubeDL import YoutubeDL
from metaDataManager import MetaDataManager
from configParserManager import ConfigParserManager
from youtubeDataKeys import PlaylistInfo
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

def downloadSingleAudio(youtubeURL):
    metaData = youtubeDownloder.downloadAudio(youtubeURL)
    if isinstance(metaData, dict):
        fileName = f'{metaData["title"]}.mp3'
        logger.info("Audio file donwloaded")
    else:
        logger.warning("File not found - wrong url")
        socketio.emit("downloadError", "File not found - wrong url")
        return
    return fileName

def downloadSingleVideo(youtubeURL, type):
    metaData = youtubeDownloder.downloadVideo(youtubeURL, type)
    logger.debug(type)
    if isinstance(metaData, dict):
        fileName = f'{metaData["title"]}_{type}.{metaData["ext"]}'
        logger.info(f"Video file {metaData['title']} donwloaded")
    else:
        logger.warning("File not found - wrong url")
        socketio.emit("downloadError", "File not found - wrong url")
    return fileName

def zipAllFilesInList(fileNameWithPath, listOfFilePaths):
    with zipfile.ZipFile(f"{fileNameWithPath}.zip", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{fileNameWithPath.split('/')[-1]}.zip"

def downloadPlaylistAudio(youtubeURL):
    metaData = youtubeDownloder.downloadAudioPlaylist(youtubeURL)
    savePath = youtubeDownloder.savePath
    filePaths = []
    for trackMetaData in metaData['entries']:
        trackTitle = trackMetaData["title"]
        filePath = os.path.join(savePath, f"{trackTitle}.mp3")
        filePaths.append(filePath)
    playlistNamePath = os.path.join(savePath, metaData["title"])
    zipNameFile = zipAllFilesInList(playlistNamePath, filePaths)
    logger.debug(f"Ziped file {zipNameFile}")
    return zipNameFile

def downloadPlaylistVideo(youtubeURL, type):
    metaData = youtubeDownloder.downloadVideoPlaylist(youtubeURL, type)
    savePath = youtubeDownloder.savePath
    filePaths = []
    for trackMetaData in metaData['entries']:
        trackTitle = trackMetaData["title"]
        fileFormat = trackMetaData["ext"]
        filePath = os.path.join(savePath, f"{trackTitle}_{type}p.{fileFormat}")
        filePaths.append(filePath)
    playlistNamePath = os.path.join(savePath, metaData["title"])
    zipNameFile = zipAllFilesInList(playlistNamePath, filePaths)
    logger.debug(f"Ziped file {zipNameFile}")
    return zipNameFile

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
        fileName = downloadPlaylistAudio(youtubeURL)
    if  type != "mp3" and isPlaylist:
        playlistInfo = youtubeDownloder.getPlaylistMediaInfo(youtubeURL)
        if isinstance(playlistInfo, str):
            socketio.emit("downloadMediaFinish", {"error": playlistInfo})
            return False
        socketio.emit("mediaInfo", {"data": playlistInfo})
        filePaths = []
        direcotryPath = youtubeDownloder.savePath
        print(playlistInfo)
        for track in playlistInfo:
            trackInfo = youtubeDownloder.downloadVideo(track[PlaylistInfo.URL.value], type)
            if isinstance(trackInfo, str):
                logger.error(f"Failed download: {trackInfo} for {track}")
                continue
            trackTitle = track["title"]
            filePath = os.path.join(direcotryPath, f"{trackTitle}_{type}p.mp4")
            filePaths.append(filePath)
        fileName = f'{playlistInfo[0]["playlist_name"]}.zip'
        zipNameFile = zipAllFilesInList(direcotryPath, filePaths)
        logger.info(f"Playlist {playlistInfo[0]['playlist_name']} donwloaded")
        logger.debug(f"Direcotry path: {direcotryPath}")
        hash = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        hashTable[hash] = {"downloadFileName": zipNameFile, "downloadDirectoryPath": direcotryPath}
        socketio.emit("downloadMediaFinish", {"data": {"HASH": hash}})
    if  type == "mp3" and not isPlaylist:
        logger.debug(f"Download single audio")
        fileName = downloadSingleAudio(youtubeURL)
    if type != "mp3" and not isPlaylist:
        logger.debug(f"Download single video")
        mediaInfo = youtubeDownloder.getSingleMediaInfo(youtubeURL)
        if isinstance(mediaInfo, str):
            socketio.emit("downloadMediaFinish", {"error": mediaInfo})
            return False
        socketio.emit("mediaInfo", {"data": mediaInfo})
        metaData = youtubeDownloder.downloadVideo(youtubeURL, type)
        if isinstance(metaData, str):
            socketio.emit("downloadMediaFinish", {"error": mediaInfo})
            return False
        fileName = f'{metaData["title"]}_{type}p.{metaData["ext"]}'
        logger.info(f"Video file {metaData['title']} donwloaded")
        direcotryPath = youtubeDownloder.savePath
        logger.debug(f"Direcotry path: {direcotryPath}")
        hash = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        hashTable[hash] = {"downloadFileName": fileName, "downloadDirectoryPath": direcotryPath}
        socketio.emit("downloadMediaFinish", {"data": {"HASH": hash}})
    # socketio.emit("downloadSucessful", {"HASH": hash})

@app.route("/downloadFile/<name>")
def downloadFile(name):
    print(name)
    downloadFileName = yt_dlp.utils.sanitize_filename(hashTable[name]["downloadFileName"])
    downloadedFilePath = hashTable[name]["downloadDirectoryPath"]
    print(downloadFileName, downloadedFilePath)
    fullPath = os.path.join(downloadedFilePath, downloadFileName)
    logger.info("Sending file to download as a attachment")
    return flask.send_file(fullPath, as_attachment=True)

@app.route("/downloadConfigPlaylist", methods=["POST", "GET"])
def downloadConfigPlaylist():
    logger.info("Downloading the config playlist")
    youtubeDownloder.downoladConfigPlaylistVideo(type=720)
    flash("All config playlist has been downloaded", category="success")
    logger.info("Config playlist downloaded")
    return render_template("youtube.html")

@socketio.on("downloadFromConfigFile")
def downloadConfigPlaylist(empty):
    logger.info("Downloading the config playlist")
    youtubeDownloder.downoladConfigPlaylistVideo(type=720)
    flash("All config playlist has been downloaded", category="success")
    logger.info("Config playlist downloaded")

@app.route("/modify_playlist", methods=["POST", "GET"])
def modify_playlist():
    if request.method == "POST":
        playlistList = configParserMenager.getPlaylists()
        if "AddPlaylistButton" in request.form:
            playlistName = request.form["playlistName"]
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

@app.route("/modify_playlist.html")
def modify_playlist_html():
    playlistList = configParserMenager.getPlaylists()
    return render_template("modify_playlist.html", playlistsNames = playlistList.keys())

@app.route("/youtube.html")
def youtube_html():
    return render_template("youtube.html")

@socketio.on("my event")
def handle_my_event_test(data):
    socketio.emit("test", {"key1": "value1"})
    logger.debug(data)

if __name__ == "__main__":
    socketio.run(app=app, debug=True, host="0.0.0.0")

