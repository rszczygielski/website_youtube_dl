from flask import Blueprint, render_template
from flask import current_app as app


youtube_playlist = Blueprint("youtube_playlist", __name__)


@youtube_playlist.route("/modify_playlist.html")
def modify_playlist_html():
    playlistList = app.configParserManager.getPlaylists()
    return render_template("modify_playlist.html", playlistsNames=playlistList.keys())
