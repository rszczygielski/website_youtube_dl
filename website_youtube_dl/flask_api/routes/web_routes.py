from flask import Blueprint
from .web_views import IndexView, YoutubeView, ModifyPlaylistView, DownloadFileView

# 1. Create the main Blueprint for the web interface
web_bp = Blueprint("web", __name__)

# 2. Register routes directly to the Blueprint at the module level
index_view = IndexView.as_view("index")
web_bp.add_url_rule("/", view_func=index_view)
web_bp.add_url_rule("/index.html", view_func=index_view)

# Routes for YouTube
web_bp.add_url_rule("/youtube.html", view_func=YoutubeView.as_view("youtube"))

# Routes for Playlists
web_bp.add_url_rule("/modify_playlist.html", view_func=ModifyPlaylistView.as_view("modify_playlist"))

# File download route
web_bp.add_url_rule("/downloadFile/<name>", view_func=DownloadFileView.as_view("download_file"))