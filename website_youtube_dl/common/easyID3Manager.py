from .youtubeDataKeys import MetaDataType
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import logging
import os

logger = logging.getLogger(__name__)


class EasyID3Manager():  # pragma: no_cover

    def __init__(self):
        self.file_path = None
        self.title = None
        self.album = None
        self.artist = None
        self.playlist_name = None
        self.track_number = None
        self.website = None

    def set_params(self, filePath,
                   title=None,
                   album=None,
                   artist=None,
                   yt_hash=None,
                   track_number=None,
                   playlist_name=None):
        if not os.path.isfile(filePath):
            logger.warning(
                f"File {filePath} doesn't exist - provide correct file path")
        self.file_path = filePath
        self.title = title
        self.album = album
        self.artist = artist
        self.yt_hash = yt_hash
        self.track_number = track_number
        self.playlist_name = playlist_name

    def save_meta_data(self):
        if self.file_path is None:
            raise FileNotFoundError(
                f"File {self.file_path} doesn't exist - provide correct file path")
        audio = EasyID3(self.file_path)
        if self.title:
            audio[MetaDataType.TITLE.value] = self.title
        if self.album:
            audio[MetaDataType.ALBUM.value] = self.album
        if self.artist:
            audio[MetaDataType.ARTIST.value] = self.artist
        if self.yt_hash:
            audio[MetaDataType.WEBSITE.value] = self.yt_hash
        if self.track_number:
            audio[MetaDataType.TRACK_NUMBER.value] = self.track_number
        audio.save()

    def read_meta_data(self):
        audio = EasyID3(self.file_path)
        if MetaDataType.TITLE.value in audio:
            self.title = audio[MetaDataType.TITLE.value]
        if MetaDataType.ALBUM.value in audio:
            self.album = audio[MetaDataType.ALBUM.value]
        if MetaDataType.ARTIST.value in audio:
            self.artist = audio[MetaDataType.ARTIST.value]
        if MetaDataType.WEBSITE.value in audio:
            self.yt_hash = audio[MetaDataType.WEBSITE.value]
        if MetaDataType.TRACK_NUMBER.value in audio:
            self.track_number = audio[MetaDataType.TRACK_NUMBER.value]
        if MetaDataType.PLAYLIST_NAME.value in audio:
            self.playlist_name = audio[MetaDataType.PLAYLIST_NAME.value]

    def _show_meta_data_info(self, path):  # pragma: no_cover
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        audio_info = MP3(path, i_d3=EasyID3)
        logger.info(audio_info.pprint())
