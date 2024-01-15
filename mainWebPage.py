from flask import Flask, render_template
from common.mailManager import Mail
from common.youtubeDL import YoutubeDL
from common.metaDataManager import MetaDataManager
from common.youtubeConfigManager import ConfigParserManager
import logging
from flask_socketio import SocketIO
import common.myLogger as myLogger

config = "youtube_config.ini"
metaDataMenager = MetaDataManager()
configParserMenager = ConfigParserManager(config)
youtubeLogger = myLogger.LoggerClass()
youtubeLogger.settings(isEmit=True, emitSkip=["minicurses.py: 111", "API", " Downloading player Downloading player"])
youtubeDownloder = YoutubeDL(configParserMenager, metaDataMenager, youtubeLogger)
mail = Mail("radek.szczygielski.trash@gmail.com")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Obczaić o co chodzi, mogę wpisać dokładnie to co chce i będzie działać
socketio = SocketIO(app)

import flaskAPI.youtube
import flaskAPI.mail

@app.route("/")
@app.route("/index.html")
@app.route('/example')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    socketio.run(app=app, debug=True, host="0.0.0.0")

