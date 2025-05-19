from ..common.youtubeAPI import (SingleMedia,
                                MediaFromPlaylist,
                                PlaylistMedia,
                                ResultOfYoutube)
from ..common.youtubeLogKeys import YoutubeLogs
from ..common.youtubeOptions import YoutubeAudioOptions, YoutubeVideoOptions
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from flask import (send_file,
                   render_template,
                   Blueprint)
from flask import current_app as app
from .emits import (DownloadMediaFinishEmit,
                    SingleMediaInfoEmit,
                    PlaylistMediaInfoEmit,
                    PlaylistTrackFinish)
from .session import SessionDownloadData
from .flaskMedia import (
    FlaskPlaylistMedia,
    FlaskSingleMedia,
    FormatMP3,
    Format360p,
    Format480p,
    Format720p,
    Format1080p,
    Format2160p)
from ..common import utils
import os
import random
import string
from .. import socketio

youtube = Blueprint("youtube", __name__)


@socketio.on("FormData")
def socket_download_server(formData):
    app.logger.debug(formData)
    youtube_url = formData[MainYoutubeKeys.YOUTUBE_URL.value]
    download_error_emit = DownloadMediaFinishEmit()
    if MainYoutubeKeys.DOWNLOAD_TYP.value not in formData:
        app.logger.warning(YoutubeLogs.NO_FORMAT.value)
        download_error_emit.send_emit_error(YoutubeLogs.NO_FORMAT.value)
        return None
    format_type = formData[MainYoutubeKeys.DOWNLOAD_TYP.value]
    app.logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {format_type}")
    options_instance = get_youtube_download_options(format_type)
    if not youtube_url:
        app.logger.warning(YoutubeLogs.NO_URL.value)
        download_error_emit.send_emit_error(YoutubeLogs.NO_URL.value)
        return None
    is_playlist = MainYoutubeKeys.URL_LIST.value in youtube_url \
        and MainYoutubeKeys.URL_VIDEO.value not in youtube_url
    full_file_path = download_correct_data(youtube_url, options_instance,
                                           is_playlist)
    if not full_file_path:
        app.logger.error("No file path returned")
        handle_error(f"Failed download from {youtube_url} - try again")
        return None
    session_download_data = SessionDownloadData(full_file_path)
    genereted_hash = generate_hash()
    app.session.add_elem_to_session(genereted_hash, session_download_data)
    emit_download_finish = DownloadMediaFinishEmit()
    emit_download_finish.send_emit(genereted_hash)


@youtube.route("/downloadFile/<name>")
def download_file(name):
    app.session.if_elem_in_session(name)
    session_download_data = app.session.get_session_elem(
        name)
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


def download_tracks_from_playlist(youtube_url, options_instance):
    playlist_media = send_emit_playlist_media(youtube_url)
    if not playlist_media:
        handle_error(f"Failed to get data from {youtube_url}")
        return None
    playlist_track_finish = PlaylistTrackFinish()
    file_paths = []
    directory_path = app.config_parser_manager.get_save_path()
    playlistTrack: MediaFromPlaylist
    downloaded_files = utils.get_files_from_dir(directory_path)
    for index, playlistTrack in enumerate(playlist_media.media_from_playlist_list):
        title = playlistTrack.title
        title_template = generate_title_template_for_youtube_downloader(
            downloaded_files, title)
        app.youtube_helper.set_title_template(
            title_template)
        if isinstance(options_instance, YoutubeAudioOptions):
            full_path = app.youtube_helper.download_audio_from_playlist(
                single_media_url=playlistTrack.yt_hash,
                options_instance=options_instance,
                playlist_name=playlist_media.playlist_name,
                index=str(index+1))
        else:
            full_path = app.youtube_helper.download_single_video(
                                              single_media_url=playlistTrack.yt_hash,
                                              options_instance=options_instance)
        if full_path is None:  # napisz unittesty pod to
            app.logger.error(f"{title} song not downloaded")
            playlist_track_finish.send_emit_error(index)
            continue
        playlist_track_finish.send_emit(index)
        file_paths.append(full_path)
        downloaded_files.append(title_template)
    zip_name_file = utils.zip_all_files_in_list(
        directory_path, playlist_media.playlist_name, file_paths)
    app.logger.info(
        f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlist_media.playlist_name}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directory_path}")
    full_zip_path = os.path.join(directory_path, zip_name_file)
    return full_zip_path


def generate_title_template_for_youtube_downloader(downloaded_files,
                                                   title):
    # https://www.youtube.com/playlist?list=PL6uhlddQJkfiCJfEQvnqzknbxfgBiGekb
    # test
    counter = 1
    while title in downloaded_files:
        counter += 1
        title = f"{title} ({counter})"
    if counter > 1:
        return f"/%(title)s ({counter})"
    return "/%(title)s"


def send_emit_single_media_info_from_youtube(single_media_url):
    single_media_info_result: ResultOfYoutube = app.youtube_helper.request_single_media_info(
        single_media_url)
    if single_media_info_result.is_error():
        return False
    mediaInfo: SingleMedia = single_media_info_result.get_data()
    flask_single_media = FlaskSingleMedia(mediaInfo.title,
                                          mediaInfo.artist,
                                          mediaInfo.url)
    media_info_emit = SingleMediaInfoEmit()
    media_info_emit.send_emit(flask_single_media)
    return True


def send_emit_playlist_media(youtube_url):
    app.logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
    playlist_media_info_result = app.youtube_helper.request_playlist_media_info(
        youtube_url)
    if playlist_media_info_result.is_error():
        return None
    playlist_media: PlaylistMedia = playlist_media_info_result.get_data()
    playlist_name = playlist_media.playlist_name
    flask_playlist_media = FlaskPlaylistMedia.init_from_playlist_media(
        playlist_name, playlist_media.media_from_playlist_list)
    playlist_info_emit = PlaylistMediaInfoEmit()
    playlist_info_emit.send_emit(flask_playlist_media)
    return playlist_media


def download_correct_data(youtube_url, options_instance, is_playlist):
    app.logger.info(f"Youtube URL: {youtube_url}")
    if is_playlist:
        full_zip_path = download_tracks_from_playlist(
            youtube_url=youtube_url, options_instance=options_instance)
        return full_zip_path
    if not send_emit_single_media_info_from_youtube(youtube_url):
        return None
    if isinstance(options_instance, YoutubeAudioOptions) and not is_playlist:
        full_file_path = app.youtube_helper.download_single_audio(single_media_url=youtube_url,
                                                                  options_instance=options_instance)
    elif isinstance(options_instance, YoutubeVideoOptions) and not is_playlist:
        full_file_path = app.youtube_helper.download_single_video(single_media_url=youtube_url,
                                                                  options_instance=options_instance)
    return full_file_path


def get_format_instance(format_str):
    format_classes = {
        "mp3": FormatMP3,
        "360p": Format360p,
        "480p": Format480p,
        "720p": Format720p,
        "1080p": Format1080p,
        "2160p": Format2160p,
    }
    if format_str not in format_classes:
        app.logger.error(f"{format_str} not supported")
        format_str = "mp3"
    return format_classes.get(format_str)()

def get_youtube_download_options(format_str):
    format_instance = get_format_instance(format_str)
    if isinstance(format_instance, FormatMP3):
        options_instance = app.youtube_helper.youtube_downloder._get_audio_options()
    else:
        video_type = format_instance.get_format_type()
        options_instance = app.youtube_helper.youtube_downloder._get_video_options(video_type)
    return options_instance

def handle_error(error_msg):  # pragma: no_cover
    download_media_finish_emit = DownloadMediaFinishEmit()
    download_media_finish_emit.send_emit_error(error_msg)



def generate_hash():
    return ''.join(random.sample(
        string.ascii_letters + string.digits, 6))
