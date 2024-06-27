from flask import Flask, render_template, Blueprint
from common.mailManager import Mail
from common.youtubeDL import YoutubeDL
from common.metaDataManager import EasyID3Manager
from common.youtubeConfigManager import ConfigParserManager
import logging
from flask_socketio import SocketIO
import common.myLogger as myLogger
from flask_session import Session

config = "youtube_config.ini"
configParserMenager = ConfigParserManager(config)
youtubeLogger = myLogger.LoggerClass()
youtubeLogger.settings(isEmit=True, emitSkip=[
                       "minicurses.py: 111", "API", " Downloading player Downloading player"])
youtubeDownloder = YoutubeDL(
    configParserMenager, youtubeLogger)
mail = Mail("radek.szczygielski.trash@gmail.com")
logging.basicConfig(
    format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
socketio = SocketIO(app, manage_session=False)
Session(app)

import flaskAPI.youtube
import flaskAPI.mail


@app.route("/")
@app.route("/index.html")
@app.route('/example')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    socketio.run(app=app, debug=True, host="0.0.0.0")