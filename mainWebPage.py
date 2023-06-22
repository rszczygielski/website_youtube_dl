from flask import Flask, flash, render_template, request
import flask
from mailManager import Mail
from youtubeDL import YoutubeDL
from metaDataManager import MetaDataManager
from configParserManager import ConfigParserManager
import yt_dlp
import os

# MetaDataManager literówka poprawić

config = "youtube_config.ini"
metaDataMenager = MetaDataManager()
configParserMenager = ConfigParserManager(config)
youtubeDownloder = YoutubeDL(configParserMenager, metaDataMenager)
mail = Mail("radek.szczygielski.trash@gmail.com")

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Obczaić o co chodzi, mogę wpisać dokładnie to co chce i będzie działać

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
            return render_template("mail.html")
        if len(messageText) == 0:
            flash("Wrong empty massage", category="danger")
            return render_template("mail.html")
        mail.sendMailFromHTML(senderInput, "Automatic mail from flask", messageText)
        flash("Mail was sucessfuly was send", category="success")
    return render_template("mail.html")

@app.route("/mail.html")
def mail_html():
    mail.initialize()
    return render_template("mail.html")

@app.route("/downloadToServer", methods=["POST", "GET"])
def downloadToServer():
    if request.method == "POST":
        youtubeURL = request.form["youtubeURL"]
        if "qualType" not in request.form:
            flash("Please enter type", category="danger")
            return render_template("youtube.html")
        else:
            type = request.form["qualType"]
        if youtubeURL == "":
            flash("Please enter YouTube URL", category="danger")
            return render_template("youtube.html")
        elif "list=" in youtubeURL and "v=" in youtubeURL:
            flash("You entered URL with playlist hash - only single video has been downloaded",
            category="danger")
        direcotryPath = youtubeDownloder.savePath
        if type == "mp3":
            metaData = youtubeDownloder.downloadAudio(youtubeURL)
            if metaData:
                fileName = f'{metaData["title"]}.mp3'
                flash("Downloaded audio file", category="success")
            else:
                flash("File not downloaded", category="danger")
                return render_template("youtube.html")
        else:
            metaData = youtubeDownloder.downloadVideo(youtubeURL, type)
            if metaData:
                fileName = f'{metaData["title"]}_{type}p.{metaData["ext"]}'
                flash("Downloaded video file", category="success")
            else:
                flash("File not downloaded", category="danger")
                return render_template("youtube.html")
        return render_template("downloadPage.html", downloadFileName=fileName, downloadDirectoryPath=direcotryPath)

@app.route("/downloadFile", methods=["POST", "GET"])
def downloadFile():
    fileName = yt_dlp.utils.sanitize_filename(request.form["fileName"])
    directoryPath = request.form["directoryPath"]
    fullPath = os.path.join(directoryPath, fileName)
    print(fullPath)
    return flask.send_file(fullPath, as_attachment=True)

@app.route("/downloadConfigPlaylist", methods=["POST", "GET"])
def downloadConfigPlaylist():
    youtubeDownloder.downoladConfigPlaylistVideo(type=720)
    flash("All config playlist has been downloaded", category="success")
    return render_template("youtube.html")

# @app.route("/add_playlist_page", methods=["POST", "GET"])
# def add_playlist_page():
#     return render_template("add_playlist.html")

@app.route("/modify_playlist", methods=["POST", "GET"])
def modify_playlist():
    if request.method == "POST":
        playlistList = configParserMenager.getPlaylists()
        if "AddPlaylistButton" in request.form:
            playlistName = request.form["playlistName"]
            playlistURL = request.form["playlistURL"]
            if "list=" not in playlistURL:
                flash("Please enter correct URL of YouTube playlist", category="danger")
                return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
            configParserMenager.addPlaylist(playlistName, playlistURL)
            playlistList = configParserMenager.getPlaylists()
            flash(f"Playlist {playlistName} added to config file", category="success")
            return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
        elif "DeletePlaylistButton" in request.form:
            if "playlistSelect" in request.form:
                playlistToRemove = request.form["playlistSelect"]
                configParserMenager.deletePlaylist(playlistToRemove)
                playlistList = configParserMenager.getPlaylists()
                flash(f"Playlist {playlistToRemove} deleted from config file", category="success")
                return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
            else:
                flash("Select a playlist to delete", category="danger")
                return render_template("modify_playlist.html", playlistsNames = playlistList.keys())
        else:
            raise Exception("Undefined behaviour")

@app.route("/modify_playlist.html")
def modify_playlist_html():
    playlistList = configParserMenager.getPlaylists()
    print(playlistList.keys())
    return render_template("modify_playlist.html", playlistsNames = playlistList.keys())

@app.route("/youtube.html")
def youtube_html():
    return render_template("youtube.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

# https://www.w3schools.com/tags/tag_select.asp