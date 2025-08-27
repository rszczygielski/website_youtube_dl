import os
from ...common.youtubeAPI import (
    SingleMedia, PlaylistMedia, ResultOfYoutube,
    FormatMP3
)
from ...common.youtubeLogKeys import YoutubeLogs
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from flask import (
    send_file, render_template, Blueprint, request
)
from flask import current_app as app
from ..sockets.emits import (
    DownloadMediaFinishEmit, SingleMediaInfoEmit, PlaylistMediaInfoEmit, PlaylistTrackFinish, HistoryEmit
)
from ..sessions.session import DownloadFileInfo
from ..services.flaskMedia import FlaskPlaylistMedia, FlaskSingleMedia, FlaskMediaFromPlaylist
from ... import socketio
from ..sockets.socket_manager import SocketManager
from ..utils.general_functions import (get_format_instance, generate_hash,
                                       get_files_from_dir, zip_all_files_in_list,
                                       generate_title_template_for_youtube_downloader)

# --- Globals ---
youtube = Blueprint("youtube", __name__)
socket_manager = SocketManager()

# --- Flask Routes ---


@youtube.route("/downloadFile/<name>")
def download_file(name):
    session_download_data = socket_manager.get_session_data_by_hash(name)
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


# --- Emit Functions ---

def send_emit_single_media_info_from_youtube(single_media_url, target_sid):
    single_media_info_result: ResultOfYoutube = app.youtube_helper.request_single_media_info(
        single_media_url)
    if single_media_info_result.is_error():
        return False
    mediaInfo: SingleMedia = single_media_info_result.get_data()
    flask_single_media = FlaskSingleMedia(
        mediaInfo.title, mediaInfo.artist, mediaInfo.url)
    socket_manager.process_emit(data=flask_single_media,
                                emit_type=SingleMediaInfoEmit,
                                user_browser_id=target_sid)
    return True


def send_emit_playlist_media(youtube_url, target_sid, session_hash):
    app.logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
    playlist_media_info_result = app.youtube_helper.request_playlist_media_info(
        youtube_url)
    if playlist_media_info_result.is_error():
        return None
    playlist_media: PlaylistMedia = playlist_media_info_result.get_data()
    playlist_name = playlist_media.playlist_name
    flask_playlist_media = FlaskPlaylistMedia.init_from_playlist_media(
        playlist_name, session_hash, playlist_media.media_from_playlist_list)
    socket_manager.process_emit(data=flask_playlist_media,
                                emit_type=PlaylistMediaInfoEmit,
                                user_browser_id=target_sid)
    return playlist_media

# --- Download Logic ---


def process_playlist_track(playlistTrack,
                           req_format,
                           target_sid,
                           playlist_media,
                           index,
                           downloaded_files):
    title = playlistTrack.title
    title_template = generate_title_template_for_youtube_downloader(
        downloaded_files, title)
    app.youtube_helper.set_title_template(title_template)
    if isinstance(req_format, FormatMP3):
        full_path = app.youtube_helper.download_audio_from_playlist(
            single_media_url=playlistTrack.yt_hash,
            req_format=req_format,
            playlist_name=playlist_media.playlist_name,
            index=str(index+1))
    else:
        full_path = app.youtube_helper.download_single_video(
            single_media_url=playlistTrack.yt_hash,
            req_format=req_format)
    if full_path is None:
        app.logger.error(f"{title} song not downloaded")
        user_browser_id = target_sid
        socket_manager.process_emit(data=index,
                                    emit_type=PlaylistTrackFinish,
                                    user_browser_id=user_browser_id)
        return None, title_template

    user_browser_id = target_sid
    socket_manager.process_emit(data=index,
                                emit_type=PlaylistTrackFinish,
                                user_browser_id=user_browser_id)
    return full_path, title_template


def download_tracks_from_playlist(youtube_url, req_format, target_sid, genereted_hash):
    playlist_media = send_emit_playlist_media(youtube_url, target_sid, genereted_hash)
    if not playlist_media:
        handle_error(error_msg=f"Failed to get data from {youtube_url}",
                     target_sid=target_sid)
        return None
    file_paths = []
    directory_path = app.config_parser_manager.get_save_path()
    downloaded_files = get_files_from_dir(directory_path)
    for index, playlistTrack in enumerate(playlist_media.media_from_playlist_list):
        full_path, title_template = process_playlist_track(playlistTrack,
                                                           req_format,
                                                           target_sid,
                                                           playlist_media,
                                                           index,
                                                           downloaded_files)
        if full_path:
            file_paths.append(full_path)
            downloaded_files.append(title_template)
            # Dodaj info o pobranym utworze do historii
            download_file_info = DownloadFileInfo(full_path, FlaskMediaFromPlaylist(
                playlistTrack.title, playlistTrack.yt_hash))
            socket_manager.add_msg_to_users_queue(
                user_browser_id=target_sid,
                hash=genereted_hash,
                session_download_data=download_file_info
            )
    zip_name_file = zip_all_files_in_list(
        directory_path, playlist_media.playlist_name, file_paths)
    app.logger.info(
        f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlist_media.playlist_name}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directory_path}")
    full_zip_path = os.path.join(directory_path, zip_name_file)
    return full_zip_path


def validate_and_prepare_download(formData):
    youtube_url = formData[MainYoutubeKeys.YOUTUBE_URL.value]
    session_id = formData.get("sessionId")
    target_sid = socket_manager.get_browser_id_by_session(session_id)
    if MainYoutubeKeys.DOWNLOAD_TYP.value not in formData:
        app.logger.warning(YoutubeLogs.NO_FORMAT.value)
        socket_manager.process_emit(data=YoutubeLogs.NO_FORMAT.value,
                                    emit_type=DownloadMediaFinishEmit,
                                    user_browser_id=target_sid)
        return None, None, None, None
    format_type = formData[MainYoutubeKeys.DOWNLOAD_TYP.value]
    app.logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {format_type}")
    request_format = get_format_instance(format_type)
    if not youtube_url:
        app.logger.warning(YoutubeLogs.NO_URL.value)
        socket_manager.process_emit(data=YoutubeLogs.NO_URL.value,
                                    emit_type=DownloadMediaFinishEmit,
                                    user_browser_id=target_sid)
        return None, None, None, None
    is_playlist = MainYoutubeKeys.URL_LIST.value in youtube_url and MainYoutubeKeys.URL_VIDEO.value not in youtube_url
    return youtube_url, request_format, is_playlist, target_sid


def download_correct_data(youtube_url, req_format, is_playlist, target_sid, genereted_hash):
    app.logger.info(f"Youtube URL: {youtube_url}")
    if is_playlist:
        return download_tracks_from_playlist(youtube_url=youtube_url,
                                             req_format=req_format,
                                             target_sid=target_sid,
                                             genereted_hash=genereted_hash)
    if not send_emit_single_media_info_from_youtube(youtube_url, target_sid):
        return None
    if isinstance(req_format, FormatMP3) and not is_playlist:
        return app.youtube_helper.download_single_audio(single_media_url=youtube_url,
                                                        req_format=req_format)
    elif not isinstance(req_format, FormatMP3) and not is_playlist:
        return app.youtube_helper.download_single_video(single_media_url=youtube_url,
                                                        req_format=req_format)
    return None


# --- SocketIO Handlers ---
@socketio.on("FormData")
def socket_download_server(formData):
    app.logger.debug(formData)
    youtube_url, request_format, is_playlist, target_sid = validate_and_prepare_download(
        formData)
    if not youtube_url:
        return None
    genereted_hash = generate_hash()
    full_file_path = download_correct_data(
        youtube_url, request_format, is_playlist, target_sid, genereted_hash)
    if not full_file_path:
        app.logger.error("No file path returned")
        handle_error(error_msg=f"Failed download from {youtube_url} - try again",
                     target_sid=target_sid)
        return None
    socket_manager.process_emit(data=genereted_hash,
                                emit_type=DownloadMediaFinishEmit,
                                user_browser_id=target_sid)


@socketio.on("userSession")
def handle_user_session(data):
    session_id = data["sessionId"]
    request_sid = request.sid
    socket_manager.add_user_session(request_sid, session_id)
    app.logger.info(f"Mapping {request_sid} -> {session_id}")


@socketio.on("getHistory")
def handle_get_history(data):
    session_id = data.get("sessionId")
    hash = data.get("hash")
    user_browser_id = socket_manager.get_browser_id_by_session(session_id)
    user_data = socket_manager.get_session_data_by_hash(hash)
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
    socket_manager.process_emit(
        data=history,
        emit_type=HistoryEmit,
        user_browser_id=user_browser_id
    )


# --- Error Handling ---


def handle_error(error_msg, target_sid):  # pragma: no_cover
    socket_manager.process_emit(data=error_msg,
                                emit_type=DownloadMediaFinishEmit,
                                user_browser_id=target_sid)
