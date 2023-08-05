from flask import Flask, flash, render_template, request
import flask
from mailManager import Mail
from youtubeDL import YoutubeDL
from metaDataManager import MetaDataManager
from configParserManager import ConfigParserManager
import yt_dlp
import os
import logging
from flask_socketio import SocketIO
import myLogger

# MetaDataManager literówka poprawić

config = "youtube_config.ini"
metaDataMenager = MetaDataManager()
configParserMenager = ConfigParserManager(config)
youtubeLogger = myLogger.LoggerClass()
youtubeLogger.settings(isEmit=True, emitSkip=["minicurses.py: 111"])
youtubeDownloder = YoutubeDL(configParserMenager, metaDataMenager, youtubeLogger)
mail = Mail("radek.szczygielski.trash@gmail.com")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

@socketio.on("FormData")
def socketDownloadServer(formData):
    logger.debug(formData)
    youtubeURL = formData["youtubeURL"]
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
        logger.warning("Playlist detected, not supported to download playlist")
    direcotryPath = youtubeDownloder.savePath
    if type == "mp3":
        metaData = youtubeDownloder.downloadAudio(youtubeURL)
        print(str(metaData))
        if isinstance(metaData, dict):
            fileName = f'{metaData["title"]}.mp3'
            logger.info("Audio file donwloaded")
        else:
            logger.warning("File not found - wrong url")
            socketio.emit("downloadError", "File not found - wrong url")
    else:
        metaData = youtubeDownloder.downloadVideo(youtubeURL, type)
        print(str(metaData))
        if isinstance(metaData, dict):
            fileName = f'{metaData["title"]}_{type}p.{metaData["ext"]}'
            logger.info(f"Video file {metaData['title']} donwloaded")
        else:
            logger.warning("File not found - wrong url")
            socketio.emit("downloadError", "File not found - wrong url")
    socketio.emit("downloadSucessful", {"downloadFileName": fileName, "downloadDirectoryPath": direcotryPath})


@app.route("/downloadFile", methods=["POST", "GET"])
def downloadFile():
    fileName = yt_dlp.utils.sanitize_filename(request.form["fileName"])
    directoryPath = request.form["directoryPath"]
    fullPath = os.path.join(directoryPath, fileName)
    logger.info("Sending file to download as a attachment")
    return flask.send_file(fullPath, as_attachment=True)

@app.route("/downloadConfigPlaylist", methods=["POST", "GET"])
def downloadConfigPlaylist():
    logger.info("Downloading the config playlist")
    youtubeDownloder.downoladConfigPlaylistVideo(type=720)
    flash("All config playlist has been downloaded", category="success")
    logger.info("Config playlist downloaded")
    return render_template("youtube.html")

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

