import logging
import os
from flask import Flask
from flask_socketio import SocketIO
from platformdirs import user_config_dir

from .common.youtubeConfigManager import ConfigParserManager
from .config import Config
from .flaskAPI.services.youtubeHelper import YoutubeHelper
from .flaskAPI.sockets.socket_manager import SocketManager

# Global SocketIO instance
socketio = SocketIO()

def create_app(config_class=Config, config_parser=ConfigParserManager,
               config_dir=None, logger_config=None):
    """Application factory for the YouTube Downloader Web application.

    Initializes Flask app, configures logging, managers, and registers
    both Blueprints and Socket.IO namespaces.

    Args:
        config_class (Type[Config]): Configuration class for Flask.
        config_parser (Type[ConfigParserManager]): Class for config file management.
        config_dir (str, optional): Directory path for config file.
        logger_config (dict, optional): Custom logging configuration.

    Returns:
        Flask: The initialized Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize core managers and attach them to the app context
    app.config_parser_manager = init_config_pareser(config_parser, config_dir)
    app.youtube_helper = YoutubeHelper(app.config_parser_manager)
    app.logger = init_logger(logger_config)
    app.socket_manager = SocketManager()

    # Local imports to avoid circular dependencies during initialization
    from .flaskAPI.routes.youtube import youtube, YoutubeNamespace
    from .flaskAPI.routes.youtube_playlists import youtube_playlist, PlaylistsNamespace

    # Register Flask Blueprints for HTTP routes
    app.register_blueprint(youtube)
    app.register_blueprint(youtube_playlist)

    # Initialize Socket.IO with the app
    socketio.init_app(app, manage_session=False)

    # Register Socket.IO Namespaces (replaces @socketio.on decorators)
    socketio.on_namespace(YoutubeNamespace('/youtube'))
    socketio.on_namespace(PlaylistsNamespace('/playlists'))

    return app

def init_logger(logger_config=None):
    """Configure and initialize the application logger.

    Args:
        logger_config (dict, optional): Dictionary containing logging config.

    Returns:
        logging.Logger: Configured logger instance.
    """
    if logger_config:
        logging.config.dictConfig(logger_config)
    else:
        logging.basicConfig(
            format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s",
            level=logging.DEBUG)

    # Suppress verbose werkzeug logs
    logger_werkzeug = logging.getLogger('werkzeug')
    logger_werkzeug.setLevel(logging.ERROR)

    logger = logging.getLogger(__name__)
    return logger

def init_config_pareser(configParser, config_dir=None):
    """Initialize the configuration parser with a specific file path.

    Args:
        configParser (Type[ConfigParserManager]): The parser class to instantiate.
        config_dir (str, optional): Target directory for the config file.

    Returns:
        ConfigParserManager: An instance of the configuration manager.
    """
    if config_dir is None:
        config_dir = user_config_dir("youtube_dl_web")

    config_file_path = os.path.join(config_dir, "config.ini")
    return configParser(config_file_path)