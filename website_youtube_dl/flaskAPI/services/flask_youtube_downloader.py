import os
from flask import current_app as app
from ...common.youtubeAPI import FormatMP3
from ...common.youtubeLogKeys import YoutubeLogs
from ..utils.general_funcions import zip_all_files_in_list, generate_title_template_for_youtube_downloader

class FlaskYoutubeDownloader:
    """
    Service responsible exclusively for physically downloading and compressing files.
    Operates on a per-file basis, leaving orchestration to the caller.
    """

    def process_playlist_track(self, playlistTrack, req_format, playlist_name, index, downloaded_files):
        """
        Downloads a single track from a playlist.

        Args:
            playlistTrack: Object representing a single track.
            req_format: Requested download format (e.g., FormatMP3).
            playlist_name (str): Name of the playlist (for metadata/folder naming).
            index (int): Track's position in the playlist.
            downloaded_files (list): Existing file templates to prevent overwriting.

        Returns:
            tuple: (full_path, title_template). full_path is None if download fails.
        """
        title = playlistTrack.title
        title_template = generate_title_template_for_youtube_downloader(downloaded_files, title)
        app.youtube_helper.set_title_template(title_template)

        full_path = None
        if isinstance(req_format, FormatMP3):
            app.logger.debug(f"Downloading audio for track: {title}")
            full_path = app.youtube_helper.download_audio_from_playlist(
                single_media_url=playlistTrack.yt_hash,
                req_format=req_format,
                playlist_name=playlist_name,
                index=str(index+1)
            )
        else:
            full_path = app.youtube_helper.download_single_video(
                single_media_url=playlistTrack.yt_hash,
                req_format=req_format
            )

        return full_path, title_template

    def zip_downloaded_playlist(self, directory_path, playlist_name, file_paths):
        """
        Compresses a list of downloaded files into a ZIP archive.

        Args:
            directory_path (str): The directory where files are saved.
            playlist_name (str): Name of the playlist (used for the zip filename).
            file_paths (list): List of absolute paths to the downloaded files.

        Returns:
            str: The full absolute path to the generated zip file.
        """
        zip_name_file = zip_all_files_in_list(directory_path, playlist_name, file_paths)
        app.logger.info(f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlist_name}")
        full_zip_path = os.path.join(directory_path, zip_name_file)

        return full_zip_path

    def download_single_track_data(self, youtube_url, req_format):
        """Downloads a single video or audio track."""
        app.logger.info(f"Youtube URL: {youtube_url} (single track)")

        if isinstance(req_format, FormatMP3):
            return app.youtube_helper.download_single_audio(
                single_media_url=youtube_url, req_format=req_format
            )
        else:
            return app.youtube_helper.download_single_video(
                single_media_url=youtube_url, req_format=req_format
            )