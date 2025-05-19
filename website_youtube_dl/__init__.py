import logging.config
from flask_socketio import SocketIO
from flask_session import Session
from .common.youtubeConfigManager import BaseConfigParser
from .config import Config
from .flaskAPI.session import SessionClient
from flask import Flask, session
from .flaskAPI.youtubeHelper import YoutubeHelper
import logging
from platformdirs import site_config_dir
import os


socketio = SocketIO()


def create_app(config_class=Config, config_parser=BaseConfigParser):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config_parser_manager = init_config_pareser(config_parser)
    app.youtube_helper = YoutubeHelper(app.config_parser_manager)
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
    config_dir = site_config_dir("youtube_dl_web")
    config_file_path = os.path.join(config_dir, "config.ini")
    return configParser(config_file_path)
