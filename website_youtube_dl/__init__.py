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
    app.configParserManager = init_configPareser()
    app.youtubeDownloder = init_youtubeDL(app.configParserManager)
    app.logger = init_logger()

    Session(app)



    from .flaskAPI.youtube import youtube
    from .flaskAPI.youtubeModifyPlaylist import youtube_playlist

    app.register_blueprint(youtube)
    app.register_blueprint(youtube_playlist)
    socketio.init_app(app, manage_session=False)
    return app


def init_logger():
    logging.basicConfig(
        format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    return logger


def init_configPareser(config=config):
    return ConfigParserManager(config)


def init_youtubeDL(configParserManager: ConfigParserManager):
    youtubeLogger = LoggerClass()

    youtubeDownloder = YoutubeDL(
        configParserManager, youtubeLogger)
    return youtubeDownloder
