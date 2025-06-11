
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
