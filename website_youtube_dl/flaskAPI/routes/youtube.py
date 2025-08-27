import os
from ... import socketio
from ...common.youtubeLogKeys import YoutubeLogs
from flask import (
    send_file, render_template, Blueprint, request
)
from flask import current_app as app
from ..sockets.emits import (
    DownloadMediaFinishEmit, HistoryEmit
)
from ..utils.general_funcions import  generate_hash
from ..handlers.youtube_download import (
    download_playlist_data, download_single_track_data)
from ..handlers.youtube_utils import (
    extract_youtube_url, extract_request_format,
    extract_is_playlist, extract_target_sid
)
from ..handlers.youtube_emit import handle_error

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
    youtube_url = extract_youtube_url(formData)
    request_format = extract_request_format(formData)
    if not youtube_url or not request_format:
        return None
    is_playlist = extract_is_playlist(youtube_url)
    target_sid = extract_target_sid(formData)
    genereted_hash = generate_hash()
    if is_playlist:
        full_file_path = download_playlist_data(
            youtube_url, request_format, target_sid, genereted_hash)
    else:
        full_file_path = download_single_track_data(
            youtube_url, request_format, target_sid)
    if not full_file_path:
        app.logger.error("No file path returned")
        handle_error(error_msg=f"Failed download from {youtube_url} - try again",
                     target_sid=target_sid)
        return None
    app.socket_manager.process_emit(data=genereted_hash,
                                    emit_type=DownloadMediaFinishEmit,
                                    user_browser_id=target_sid)


@socketio.on("userSession")
def handle_user_session(data):
    session_id = data["sessionId"]
    request_sid = request.sid
    app.socket_manager.add_user_session(request_sid, session_id)
    app.logger.info(f"Mapping {request_sid} -> {session_id}")


@socketio.on("getHistory")
def handle_get_history(data):
    session_id = data.get("sessionId")
    hash = data.get("hash")
    user_browser_id = app.socket_manager.get_browser_id_by_session(session_id)
    user_data = app.socket_manager.get_session_data_by_hash(hash)
    app.logger.info(session_id, "<-- session_id")
    app.logger.info(user_browser_id, "<-- user_browser_id")
    app.logger.info(user_data, "<-- user_data")
    history = []
    for download_info in user_data:
        media = download_info.media_from_playlist
        if media:
            history.append({
                "title": getattr(media, "title", None),
                "url": getattr(media, "url", None)
            })
    app.socket_manager.process_emit(
        data=history,
        emit_type=HistoryEmit,
        user_browser_id=user_browser_id
    )


