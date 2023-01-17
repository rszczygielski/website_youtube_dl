from flask import Flask, flash, render_template, request, send_file
from mailManager import MailManager
from youtubeDL import YoutubeDL, AudioYoutube
import os

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
    print("Send mail")
    if request.method == "POST":
        senderInput = request.form["senderInput"]
        messageText = request.form["messageText"]
        if len(senderInput) == 0 or "@" not in senderInput:
            flash("Wrong mail adress", category="danger")
            return render_template("mail.html")
        if len(messageText) == 0:
            flash("Wrong empty massage", category="danger")
            return render_template("mail.html")
        mailManager = MailManager("radek.szczygielski.trash@gmail.com")
        mailManager.sendMailFromHTML("Automatic mail from flask", f"Otrzymałem maile: {senderInput}<br> O treści: {messageText}""")
        flash("Mail was sucessfuly was send", category="success")
    return render_template("mail.html")

@app.route("/mail.html")
def mail():
    return render_template("mail.html")

@app.route("/downloadYoutube", methods=["POST", "GET"])
def downloadYoutube():
    if request.method == "POST":
        youtubeURL = request.form["youtubeURL"]
        if "qualType" not in request.form:
            flash("Please enter type", category="danger")
            return render_template("youtube.html")
        else:
            type = request.form["qualType"]
        config = "youtube_config.ini"
        if youtubeURL == "":
            flash("Please enter YouTube URL", category="danger")
            return render_template("youtube.html")
        youtubeDownloder = AudioYoutube(config)
        direcotryPath = youtubeDownloder.savePath
        if type == "mp3":
            metaData = youtubeDownloder.downloadAudio(youtubeURL)
            fileName = f'{metaData["title"]}.mp3'
            flash("Downloaded audio file", category="success")
        else:
            metaData = youtubeDownloder.downloadVideo(youtubeURL, type)
            print(youtubeDownloder.ydl_video_opts)
            # print(metaData)
            # print(metaData["ext"])
            fileName = f'{metaData["title"]}_{type}p.{metaData["ext"]}'
            flash("Downloaded video file", category="success")
        return render_template("downloadPage.html", downloadFileName=fileName, downloadDirectoryPath=direcotryPath)

@app.route("/downloadFile", methods=["POST", "GET"])
def downloadFile():
    fileName = request.form["fileName"]
    directoryPath = request.form["directoryPath"]
    fullPath = os.path.join(directoryPath, fileName)
    return send_file(fullPath, as_attachment=True)

@app.route("/youtube.html")
def youtube():
    return render_template("youtube.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")