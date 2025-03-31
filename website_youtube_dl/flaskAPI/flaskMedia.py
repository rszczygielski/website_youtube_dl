
class FlaskSingleMedia():
    def __init__(self, title: str, artist: str, url: str) -> None:
        self.title = title
        self.artist = artist
        self.url = url


class FlaskMediaFromPlaylist():
    def __init__(self, title, url):
        self.title = title
        self.url = url


class FlaskPlaylistMedia():
    def __init__(self, plyalistName: str,
                 track_list: list[FlaskMediaFromPlaylist]) -> None:
        self.playlist_name = plyalistName
        self.track_list = track_list

    @classmethod
    def init_from_playlist_media(cls, playlist_name, track_list):
        flask_single_media_list = []
        for track in track_list:
            flask_single_media_list.append(FlaskMediaFromPlaylist(track.title,
                                                                  track.yt_hash))
        return cls(playlist_name, flask_single_media_list)


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
