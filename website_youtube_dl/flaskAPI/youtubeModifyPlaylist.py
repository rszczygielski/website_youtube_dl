from flask import Blueprint, render_template
from flask import current_app as app
from .. import socketio
from .emits import (DownloadMediaFinishEmit,
                    UploadPlaylistToConfigEmit,
                    GetPlaylistUrlEmit)
from .youtube import generateHash, downloadTracksFromPlaylist
from .session import SessionDownloadData


youtube_playlist = Blueprint("youtube_playlist", __name__)


@youtube_playlist.route("/modify_playlist.html")
def modify_playlist_html():
    playlistList = app.configParserManager.getPlaylists()
    return render_template("modify_playlist.html", playlistsNames=playlistList.keys())


@socketio.on("downloadFromConfigFile")
def downloadConfigPlaylist(formData):
    playlistName = formData["playlistToDownload"]
    app.logger.info(f"Selected playlist form config {playlistName}")
    playlistURL = app.configParserManager.getPlaylistUrl(playlistName)
    fullFilePath = downloadTracksFromPlaylist(youtubeURL=playlistURL,
                                              videoType=None)
    if not fullFilePath:
        return False
    sessionDownloadData = SessionDownloadData(fullFilePath)
    genereted_hash = generateHash()
    app.session.addElemtoSession(genereted_hash, sessionDownloadData)
    emitDownloadFinish = DownloadMediaFinishEmit()
    emitDownloadFinish.sendEmit(genereted_hash)


@socketio.on("addPlaylist")
def addPlalistConfig(formData):
    playlistName = formData["playlistName"]
    playlistURL = formData["playlistURL"]
    app.configParserManager.addPlaylist(playlistName, playlistURL)
    playlistList = list(app.configParserManager.getPlaylists().keys())
    uploadPlaylistEmit = UploadPlaylistToConfigEmit()
    uploadPlaylistEmit.sendEmit(playlistList)


@socketio.on("deletePlaylist")
def deletePlalistConfig(formData):
    playlistName = formData["playlistToDelete"]
    app.configParserManager.deletePlaylist(playlistName)
    playlistList = list(app.configParserManager.getPlaylists().keys())
    uploadPlaylistEmit = UploadPlaylistToConfigEmit()
    uploadPlaylistEmit.sendEmit(playlistList)


@socketio.on("playlistName")
def getPlaylistConfigUrl(formData):
    playlistName = formData["playlistName"]
    playlistUrl = app.configParserManager.getPlaylistUrl(playlistName)
    getPlaylistEmit = GetPlaylistUrlEmit()
    getPlaylistEmit.sendEmit(playlistUrl)
