import os
from ... import socketio
from ...common.youtubeLogKeys import YoutubeLogs
from flask import (
    send_file, render_template, Blueprint, request
)
from flask import current_app as app
from ..sockets.emits import (
    DownloadMediaFinishEmit
)
from ..utils.general_funcions import generate_hash
from ..handlers.youtube_download import (
    download_playlist_data, download_single_track_data)
from ..handlers.youtube_utils import (
    extract_youtube_url, extract_request_format,
    is_playlist_in_url
)
from ..handlers.youtube_emit import handle_error
from ..sockets.session_data import DownloadFileInfo

# --- Globals ---
youtube = Blueprint("youtube", __name__)


# --- Flask Routes ---


@youtube.route("/downloadFile/<name>")
def download_file(name):
    session_download_data = app.socket_manager.get_session_data_by_hash(name)
    if not session_download_data:
        app.logger.warning(f"No session data for hash: {name}")
        return "File not found", 404
    full_path = os.path.join(
        session_download_data.file_directory_path, session_download_data.file_name)
    app.logger.info(YoutubeLogs.SENDING_TO_ATTACHMENT.value)
    return send_file(full_path, as_attachment=True)


@youtube.route("/youtube.html")
def youtube_html():
    return render_template("youtube.html")


@youtube.route("/")
@youtube.route("/index.html")
@youtube.route('/example')
def index():
    return render_template('index.html')


# --- SocketIO Handlers ---


@socketio.on("FormData")
def socket_download_server(formData):
    app.logger.debug(formData)
    user_browser_id = app.socket_manager.get_user_browser_id_by_session(
        request.sid)
    app.logger.debug(
        f"{user_browser_id} <-- user_browser_id {request.sid} <-- request.sid")
    app.socket_manager.clear_user_data(user_browser_id)
    app.logger.info(f"Cleared user data: {user_browser_id}")
    youtube_url = extract_youtube_url(formData, user_browser_id)
    request_format = extract_request_format(formData, user_browser_id)

    if not youtube_url or not request_format:
        return None
    is_playlist = is_playlist_in_url(youtube_url)
    if is_playlist:
        full_file_path = download_playlist_data(
            youtube_url, request_format, user_browser_id)
    else:
        full_file_path = download_single_track_data(
            youtube_url, request_format, user_browser_id)
    if not full_file_path:
        app.logger.error("No file path returned")
        handle_error(
            error_msg=f"Failed download from {youtube_url} - try again")
        return None
    genereted_hash = generate_hash()
    # zapisz genereted_hash do sesji z filepath w klasie DownloadFileInfo TODO
    app.socket_manager.add_message_to_session_hash(
        genereted_hash,
        DownloadFileInfo(
            full_file_path, is_playlist
        )
    )
    app.socket_manager.process_emit(data=genereted_hash,
                                    emit_type=DownloadMediaFinishEmit,
                                    user_browser_id=user_browser_id)


@socketio.on("userSession")
def handle_user_session(data):
    user_browser_id = data["userBrowserId"]
    request_sid = request.sid
    app.socket_manager.add_user_session(user_browser_id, request_sid)
    app.logger.info(f"Mapping {request_sid} -> {user_browser_id}")


@socketio.on("getHistory")
def handle_get_history(data):
    user_browser_id = data.get("userBrowserId")
    user_data = app.socket_manager.get_user_messages(user_browser_id)
    app.logger.debug(f"{user_browser_id} <-- user_browser_id")

    for emit_type, data in user_data:
        emit = emit_type()
        session_id = app.socket_manager.get_session_id_by_user_browser_id(
            user_browser_id)
        emit.send_emit(data, session_id)
