from common.youtubeDataKeys import MetaDataType
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import logging

logger = logging.getLogger(__name__)

class EasyID3Manager(): # pragma: no_cover
    
    def __init__(self, title=None, album=None,
                 artist=None, trackNumber=None,
                 playlistName=None):
        self.title = title
        self.album = album
        self.artist = artist
        self.playlistName = playlistName
        self.trackNumber = trackNumber

    
    def setFilePath(self, directoryPath):
        self.filePath = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(self.title)}.mp3'


    def saveMetaData(self):
        audio = EasyID3(self.filePath)
        if self.title:
            audio[MetaDataType.TITLE.value] = self.title
        if self.album:
            audio[MetaDataType.ALBUM.value] = self.album
        if self.artist:
            audio[MetaDataType.ARTIST.value] = self.artist
        if self.playlistName:
            audio[MetaDataType.PLAYLIST_NAME.value] = self.playlistName
        if self.trackNumber:
            audio[MetaDataType.TRACK_NUMBER.value] = self.trackNumber
        audio.save()

    def setPlaylistName(self, playlistName):
        self.playlistName = playlistName
    
    
    def _showMetaDataInfo(self, path):  # pragma: no_cover
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        audioInfo = MP3(path, ID3=EasyID3)
        logger.info(audioInfo.pprint())
