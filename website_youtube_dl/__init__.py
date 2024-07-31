from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_session import Session
from .common.youtubeConfigManager import ConfigParserManager
from .common.myLogger import LoggerClass
from .common.youtubeDL import YoutubeDL
from .config import Config
import logging

config = "youtube_config.ini"
socketio = SocketIO()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    Session(app)

    @app.route("/")
    @app.route("/index.html")
    @app.route('/example')
    def index():
        return render_template('index.html')

    from .flaskAPI.youtube import youtube

    app.register_blueprint(youtube)
    socketio.init_app(app, manage_session=False)
    return app

def init_logger():
    logging.basicConfig(
    format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    return logger


def init_configPareser(config=config):
    return ConfigParserManager(config)

def init_youtubeDL(configParserMenager:ConfigParserManager):
    youtubeLogger = LoggerClass()
    youtubeLogger.settings(isEmit=True, emitSkip=[
                        "minicurses.py: 111", "API",
                        " Downloading player Downloading player"])
    youtubeDownloder = YoutubeDL(
        configParserMenager, youtubeLogger)
    return youtubeDownloder


