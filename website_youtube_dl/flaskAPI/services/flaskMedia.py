
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
    def __init__(self, playlistName: str,
                 session_hash: str,
                 track_list: list[FlaskMediaFromPlaylist]) -> None:
        self.playlist_name = playlistName
        self.session_hash = session_hash
        self.track_list = track_list

    @classmethod
    def init_from_playlist_media(cls, playlist_name, session_hash, track_list):
        flask_single_media_list = []
        for track in track_list:
            flask_single_media_list.append(FlaskMediaFromPlaylist(track.title,
                                                                  track.yt_hash))
        return cls(playlist_name, session_hash, flask_single_media_list)
