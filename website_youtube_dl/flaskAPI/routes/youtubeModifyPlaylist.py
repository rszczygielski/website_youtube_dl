from flask import Blueprint, render_template, request
from flask import current_app as app
from ... import socketio
from ..sockets.emits import (DownloadMediaFinishEmit,
                             UploadPlaylistToConfigEmit,
                             GetPlaylistUrlEmit)
from ..handlers.youtube_download import download_tracks_from_playlist
from ...common.youtubeAPI import FormatMP3
from ..handlers.youtube_emit import send_emit_media_finish_error
from ..sockets.session_data import DownloadFileInfo
from ..utils.general_funcions import generate_hash

youtube_playlist = Blueprint("youtube_playlist", __name__)


@youtube_playlist.route("/modify_playlist.html")
def modify_playlist_html():
    playlist_list = app.config_parser_manager.get_playlists()
    print(f"playlist_list: {playlist_list}")
    playlists_names = list(playlist_list.keys())
    app.logger.debug(f"Rendering modify_playlist.html with {len(playlists_names)} playlists: {playlists_names}")
    return render_template(
        "modify_playlist.html",
        playlists_names=playlists_names)


@socketio.on("downloadFromConfigFile")
def download_config_playlist(formData):
    playlist_name = formData["playlistToDownload"]
    app.logger.info(f"Selected playlist form config {playlist_name}")
    user_browser_id = app.socket_manager.get_user_browser_id_by_session(
        request.sid)
    playlist_url = app.config_parser_manager.get_playlist_url(playlist_name)
    full_file_path = download_tracks_from_playlist(youtube_url=playlist_url,
                                                   req_format=FormatMP3(),
                                                   user_browser_id=user_browser_id)
    if not full_file_path:
        app.logger.error("No file path returned")
        send_emit_media_finish_error(
            error_msg=f"Failed download from {playlist_url} - try again",
            user_browser_id=user_browser_id)
        return None
    genereted_hash = generate_hash()
    app.socket_manager.add_message_to_session_hash(
        genereted_hash,
        DownloadFileInfo(
            full_file_path, True
        )
    )
    app.socket_manager.process_emit(data=genereted_hash,
                                    emit_type=DownloadMediaFinishEmit,
                                    user_browser_id=user_browser_id)


@socketio.on("addPlaylist")
def add_plalist_config(formData):
    print(f"formData: {formData}")
    playlist_name = formData["playlistName"]
    playlist_url = formData["playlistURL"]
    result = app.config_parser_manager.add_playlist(
        playlist_name, playlist_url)
    user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)
    upload_playlist_emit = UploadPlaylistToConfigEmit()
    if result:
        app.logger.info(f"Added playlist {playlist_name} to config")
    else:
        upload_playlist_emit.send_emit_error(
            f"Failed to add playlist {playlist_name} to config", user_browser_id)
        app.logger.warning(f"Failed to add playlist {playlist_name} to config")
        return
    app.logger.debug(f"Playlist URL: {playlist_url}")
    app.logger.debug(f"Playlist name: {playlist_name}")
    playlist_list = list(app.config_parser_manager.get_playlists().keys())
    upload_playlist_emit.send_emit(playlist_list, user_browser_id)


@socketio.on("deletePlaylist")
def delete_plalist_config(formData):
    playlist_name = formData["playlistToDelete"]
    user_browser_id = app.socket_manager.get_user_browser_id_by_session(
        request.sid)
    upload_playlist_emit = UploadPlaylistToConfigEmit()
    result = app.config_parser_manager.delete_playlist(playlist_name)
    if result:
        app.logger.info(f"Deleted playlist {playlist_name} from config")
    else:
        upload_playlist_emit.send_emit_error(
            f"Failed to delete playlist {playlist_name} from config", user_browser_id)
        app.logger.warning(
            f"Failed to delete playlist {playlist_name} from config")
        return
    app.logger.debug(f"Playlist name: {playlist_name}")
    playlist_list = list(app.config_parser_manager.get_playlists().keys())
    upload_playlist_emit.send_emit(playlist_list, user_browser_id)


@socketio.on("playlistName")
def get_playlist_config_url(formData):
    playlist_name = formData["playlistName"]
    playlist_url = app.config_parser_manager.get_playlist_url(playlist_name)
    get_playlist_emit = GetPlaylistUrlEmit()
    user_browser_id = app.socket_manager.get_user_browser_id_by_session(
        request.sid)
    get_playlist_emit.send_emit(playlist_url, user_browser_id)
