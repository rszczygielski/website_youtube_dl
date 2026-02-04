from .youtubeDataKeys import MetaDataType
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import logging
import os

logger = logging.getLogger(__name__)


class EasyID3Manager():  # pragma: no_cover
    """Manager for EasyID3 metadata operations on MP3 files.
    
    This class provides functionality to read and write ID3 metadata tags
    to MP3 audio files using the mutagen library. It supports common metadata
    fields like title, album, artist, track number, and playlist information.
    
    Attributes:
        file_path (str): Path to the MP3 file being managed.
        title (str): Title metadata of the audio file.
        album (str): Album metadata of the audio file.
        artist (str): Artist metadata of the audio file.
        playlist_name (str): Name of the playlist this track belongs to.
        track_number (str): Track number in the playlist or album.
        website (str): Website URL or YouTube hash stored in metadata.
    """

    def __init__(self):
        """Initialize EasyID3Manager with empty metadata fields."""
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
        """Set metadata parameters for the audio file.
        
        Args:
            filePath (str): Path to the MP3 file.
            title (str, optional): Title of the track. Defaults to None.
            album (str, optional): Album name. Defaults to None.
            artist (str, optional): Artist name. Defaults to None.
            yt_hash (str, optional): YouTube hash or URL. Defaults to None.
            track_number (str, optional): Track number. Defaults to None.
            playlist_name (str, optional): Playlist name. Defaults to None.
            
        Note:
            Logs a warning if the file path does not exist, but does not
            raise an exception. The file must exist when save_meta_data()
            is called.
        """
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
        """Save metadata to the MP3 file.
        
        Writes all set metadata fields (title, album, artist, yt_hash,
        track_number) to the ID3 tags of the MP3 file.
        
        Raises:
            FileNotFoundError: If file_path is None or the file does not exist.
        """
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
        """Read metadata from the MP3 file.
        
        Reads all available ID3 metadata tags from the MP3 file and
        populates the corresponding instance attributes. Only reads tags
        that exist in the file.
        
        Note:
            Requires file_path to be set and the file to exist.
        """
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
        """Display formatted metadata information for debugging.
        
        Args:
            path (str): Path to the MP3 file to display metadata for.
        """
        audio_info = MP3(path, i_d3=EasyID3)
        logger.info(audio_info.pprint())
