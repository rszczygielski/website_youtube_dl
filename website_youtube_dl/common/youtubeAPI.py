class SingleMedia():
    def __init__(
            self,
            file_path,
            title,
            album,
            artist,
            yt_hash,
            url,
            extension):
        self.file_path = file_path
        self.title = title
        self.album = album
        self.artist = artist
        self.yt_hash = yt_hash
        self.url = url
        self.extension = extension


class MediaFromPlaylist():
    def __init__(self, title, yt_hash):
        self.title = title
        self.yt_hash = yt_hash


class PlaylistMedia():
    def __init__(self, playlist_name, media_from_playlist_list: list):
        self.playlist_name = playlist_name
        self.media_from_playlist_list = media_from_playlist_list



class ResultOfYoutube():
    _is_error = False
    _error_info = None
    data = None

    def __init__(self, data=None) -> None:
        self.set_data(data)

    def set_error(self, error_info: str):
        self._is_error = True
        self._error_info = error_info

    def set_data(self, data):
        self._data = data

    def is_error(self):
        return self._is_error

    def get_data(self):
        if not self._is_error:
            return self._data

    def get_error_info(self):
        if self._is_error:
            return self._error_info


class FormatBase():
    def __init__(self, fileFormat):
        self.file_format = fileFormat
        self.file_suffix = fileFormat

    def get_format_type(self):
        return self.file_format

    def get_file_suffix(self):
        return self.file_suffix

    def set_file_suffix(self, fileSuffix):
        self.file_suffix = fileSuffix


class FormatMP3(FormatBase):
    def __init__(self):
        super().__init__("mp3")


class VideoFormat(FormatBase):
    def __init__(self, resolution):
        super().__init__(resolution)
        self.set_file_suffix(f"f_{resolution}p")


class Format360p(VideoFormat):
    def __init__(self):
        super().__init__("360")


class Format480p(VideoFormat):
    def __init__(self):
        super().__init__("480")


class Format720p(VideoFormat):
    def __init__(self):
        super().__init__("720")


class Format1080p(VideoFormat):
    def __init__(self):
        super().__init__("1080")


class Format2160p(VideoFormat):
    def __init__(self):
        super().__init__("2160")
