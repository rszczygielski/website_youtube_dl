import logging.config
from flask_socketio import SocketIO
from flask_session import Session
from .common.youtubeConfigManager import ConfigParserManager
from .common.myLogger import LoggerClass
from .common.youtubeDL import YoutubeDL
from .config import Config
from .flaskAPI.session import SessionClient
from flask import Flask, session
import logging


socketio = SocketIO()


def create_app(config_class=Config, config_parser=ConfigParserManager):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config_parser_manager = init_config_pareser(config_parser)
    app.youtube_downloder = init_youtube_dl(app.config_parser_manager)
    app.logger = init_logger()

    Session(app)

    from .flaskAPI.youtube import youtube
    from .flaskAPI.youtubeModifyPlaylist import youtube_playlist

    app.register_blueprint(youtube)
    app.register_blueprint(youtube_playlist)
    socketio.init_app(app, manage_session=False)
    app.session = SessionClient(session)
    return app


def init_logger():
    logging.basicConfig(
        format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s",
        level=logging.DEBUG)
    logger_werkzeug = logging.getLogger('werkzeug')
    logger_werkzeug.setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)
    return logger


def init_config_pareser(configParser):
    config = "youtube_config.ini"
    return configParser(config)


def init_youtube_dl(config_parser_manager: ConfigParserManager):
    youtube_logger = LoggerClass()

    youtube_downloder = YoutubeDL(
        config_parser_manager, youtube_logger)
    return youtube_downloder
