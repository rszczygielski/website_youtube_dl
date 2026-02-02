import os
from flask import current_app as app
from ...common.youtubeAPI import FormatMP3
from ...common.youtubeLogKeys import YoutubeLogs
from ..sockets.emits import PlaylistTrackFinish
from ..utils.general_funcions import get_files_from_dir, zip_all_files_in_list, generate_title_template_for_youtube_downloader
from ..handlers.youtube_emit import send_emit_playlist_media, send_emit_media_finish_error, send_emit_single_media_info_from_youtube



def process_playlist_track(playlistTrack,
                           req_format,
                           user_browser_id,
                           playlist_media,
                           index,
                           downloaded_files):
    title = playlistTrack.title
    title_template = generate_title_template_for_youtube_downloader(
        downloaded_files, title)
    app.youtube_helper.set_title_template(title_template)
    if isinstance(req_format, FormatMP3):
        app.logger.debug(f"Downloading audio for track: {title}")
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
        app.socket_manager.process_emit_error(error_msg=index, # zrobić unittest pod to
                                             emit_type=PlaylistTrackFinish,
                                             user_browser_id=user_browser_id)
        return None, title_template

    app.socket_manager.process_emit(data=index,
                                    emit_type=PlaylistTrackFinish,
                                    user_browser_id=user_browser_id)
    return full_path, title_template


def download_tracks_from_playlist(youtube_url, req_format, user_browser_id):
    playlist_media = send_emit_playlist_media(
        youtube_url, user_browser_id)
    if not playlist_media:
        send_emit_media_finish_error(error_msg=f"Failed to get data from {youtube_url}",
                                     user_browser_id=user_browser_id)
        return None
    file_paths = []
    directory_path = app.config_parser_manager.get_save_path()
    downloaded_files = get_files_from_dir(directory_path)
    for index, playlistTrack in enumerate(playlist_media.media_from_playlist_list):
        full_path, title_template = process_playlist_track(playlistTrack,
                                                           req_format,
                                                           user_browser_id,
                                                           playlist_media,
                                                           index,
                                                           downloaded_files)
        if full_path:
            file_paths.append(full_path)
            downloaded_files.append(title_template)
    zip_name_file = zip_all_files_in_list(
        directory_path, playlist_media.playlist_name, file_paths)
    app.logger.info(
        f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlist_media.playlist_name}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directory_path}")
    full_zip_path = os.path.join(directory_path, zip_name_file)
    return full_zip_path


def download_playlist_data(youtube_url, req_format, user_browser_id):
    app.logger.info(f"Youtube URL: {youtube_url} (playlist)")
    return download_tracks_from_playlist(youtube_url=youtube_url,
                                         req_format=req_format,
                                         user_browser_id=user_browser_id)


def download_single_track_data(youtube_url,
                               req_format,
                               user_browser_id):
    app.logger.info(f"Youtube URL: {youtube_url} (single track)")
    if not send_emit_single_media_info_from_youtube(youtube_url, user_browser_id):
        app.logger.error("Failed to send emit for single media info")
        return None
    if isinstance(req_format, FormatMP3):
        return app.youtube_helper.download_single_audio(single_media_url=youtube_url,
                                                        req_format=req_format)
    else:
        return app.youtube_helper.download_single_video(single_media_url=youtube_url,
                                                        req_format=req_format)
