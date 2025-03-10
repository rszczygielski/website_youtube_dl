import re


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
                 trackList: list[FlaskMediaFromPlaylist]) -> None:
        self.playlistName = plyalistName
        self.trackList = trackList

    @classmethod
    def initFromPlaylistMedia(cls, playlistName, trackList):
        flaskSingleMediaList = []
        for track in trackList:
            flaskSingleMediaList.append(FlaskMediaFromPlaylist(track.title,
                                                               track.ytHash))
        return cls(playlistName, flaskSingleMediaList)


class FormatType:
    def __init__(self):
        self.mp3 = False
        self.f_360p = False
        self.f_480p = False
        self.f_720p = False
        self.f_1080p = False
        self.f_2160p = False

    def get_selected_format(self):
        if self.mp3:
            return "mp3"
        for format_name, is_selected in vars(self).items():
            if is_selected:
                return "".join(re.findall("\d", format_name))
        return None

    @classmethod
    def initFromForm(cls, data_format):
        instance = cls()

        if data_format == "mp3":
            setattr(instance, "mp3", True)
            return instance

        attribute_name = f"f_{data_format}p"

        if not hasattr(instance, attribute_name):
            raise ValueError(
                f"Attribute: {attribute_name} not found, enter correct data format")

        setattr(instance, attribute_name, True)
        return instance
