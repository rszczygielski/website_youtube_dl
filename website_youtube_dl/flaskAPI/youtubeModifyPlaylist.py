from flask import Blueprint, render_template
from flask import current_app as app
from .. import socketio
from .emits import (DownloadMediaFinishEmit,
                    UploadPlaylistToConfigEmit,
                    GetPlaylistUrlEmit)
from .youtube import generate_hash, download_tracks_from_playlist
from .session import SessionDownloadData


youtube_playlist = Blueprint("youtube_playlist", __name__)


@youtube_playlist.route("/modify_playlist.html")
def modify_playlist_html():
    playlist_list = app.config_parser_manager.get_playlists()
    return render_template(
        "modify_playlist.html",
        playlists_names=playlist_list.keys())


@socketio.on("downloadFromConfigFile")
def download_config_playlist(formData):
    playlist_name = formData["playlistToDownload"]
    app.logger.info(f"Selected playlist form config {playlist_name}")
    playlist_url = app.config_parser_manager.get_playlist_url(playlist_name)
    full_file_path = download_tracks_from_playlist(youtube_url=playlist_url,
                                                   video_type=None)
    if not full_file_path:
        return False
    session_download_data = SessionDownloadData(full_file_path)
    genereted_hash = generate_hash()
    app.session.add_elem_to_session(genereted_hash, session_download_data)
    emit_download_finish = DownloadMediaFinishEmit()
    emit_download_finish.send_emit(genereted_hash)


@socketio.on("addPlaylist")
def add_plalist_config(formData):
    playlist_name = formData["playlistName"]
    playlist_url = formData["playlistURL"]
    result = app.config_parser_manager.add_playlist(playlist_name, playlist_url)
    upload_playlist_emit = UploadPlaylistToConfigEmit()
    if result:
        app.logger.info(f"Added playlist {playlist_name} to config")
    else:
        upload_playlist_emit.send_emit_error(
            f"Failed to add playlist {playlist_name} to config")
        app.logger.warning(f"Failed to add playlist {playlist_name} to config")
        return False
    app.logger.debug(f"Playlist URL: {playlist_url}")
    app.logger.debug(f"Playlist name: {playlist_name}")
    playlist_list = list(app.config_parser_manager.get_playlists().keys())
    upload_playlist_emit.send_emit(playlist_list)


@socketio.on("deletePlaylist")
def delete_plalist_config(formData):
    playlist_name = formData["playlistToDelete"]
    upload_playlist_emit = UploadPlaylistToConfigEmit()
    result = app.config_parser_manager.deletePlaylist(playlist_name)
    if result:
        app.logger.info(f"Deleted playlist {playlist_name} from config")
    else:
        upload_playlist_emit.send_emit_error(
            f"Failed to delete playlist {playlist_name} from config")
        app.logger.warning(f"Failed to delete playlist {playlist_name} from config")
        return False
    app.logger.debug(f"Playlist name: {playlist_name}")
    playlist_list = list(app.config_parser_manager.get_playlists().keys())
    upload_playlist_emit.send_emit(playlist_list)


@socketio.on("playlistName")
def get_playlist_config_url(formData):
    playlist_name = formData["playlistName"]
    playlist_url = app.config_parser_manager.get_playlist_url(playlist_name)
    get_playlist_emit = GetPlaylistUrlEmit()
    get_playlist_emit.send_emit(playlist_url)
