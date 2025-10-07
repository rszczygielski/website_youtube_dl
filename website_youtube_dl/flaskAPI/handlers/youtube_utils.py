from flask import current_app as app
from .youtube_emit import send_emit_media_finish_error
from website_youtube_dl.common.youtubeDataKeys import MainYoutubeKeys
from ...common.youtubeLogKeys import YoutubeLogs
from ..utils.general_funcions import get_format_instance


def extract_youtube_url(formData, user_browser_id):
    youtube_url = formData.get(MainYoutubeKeys.YOUTUBE_URL.value)
    if not youtube_url:
        app.logger.warning(YoutubeLogs.NO_URL.value)
        send_emit_media_finish_error(YoutubeLogs.NO_URL.value, user_browser_id)

        return None
    return youtube_url


def extract_request_format(formData, user_browser_id):
    if MainYoutubeKeys.DOWNLOAD_TYP.value not in formData:
        app.logger.warning(YoutubeLogs.NO_FORMAT.value)
        send_emit_media_finish_error(
            YoutubeLogs.NO_FORMAT.value, user_browser_id)
        return None
    format_type = formData[MainYoutubeKeys.DOWNLOAD_TYP.value]
    app.logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {format_type}")
    request_format = get_format_instance(format_type)
    return request_format


def is_playlist_in_url(youtube_url):
    if not youtube_url:
        return None
    return MainYoutubeKeys.URL_LIST.value in youtube_url and MainYoutubeKeys.URL_VIDEO.value not in youtube_url
