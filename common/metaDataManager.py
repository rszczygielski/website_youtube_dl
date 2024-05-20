from common.youtubeDataKeys import MetaDataType
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import logging

logger = logging.getLogger(__name__)

class EasyID3SingleMedia(): # pragma: no_cover
    filePath = ""

    def __init__(self, title, album, artist,):
        self.title = title
        self.album = album
        self.artist = artist

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
        audio.save()

    @classmethod
    def initFromSingleMata(cls, singleData):
        title = singleData.title
        album = singleData.album
        artist = singleData.artist
        return cls(title, album, artist)
    
class EasyID3MediaFromPlaylist(EasyID3SingleMedia): # pragma: no_cover
    playlistName = ""
    
    def __init__(self, title, album, artist, trackNumber):
        super().__init__(title, album, artist)
        self.trackNumber = trackNumber

    @classmethod
    def initFromMediaFromPlaylist(cls, singleData):
        title = singleData.title
        album = singleData.album
        artist = singleData.artist
        trackNumber = singleData.trackNumber
        return cls(title, album, artist, trackNumber)
    
    def saveMetaData(self):
        audio = EasyID3(self.filePath)
        if self.title:
            audio[MetaDataType.TITLE.value] = self.title
        if self.album:
            audio[MetaDataType.ALBUM.value] = self.album
        if self.artist:
            audio[MetaDataType.ARTIST.value] = self.artist
        if self.playlistName:
            audio[MetaDataType.ALBUM.value] = self.playlistName
        if self.trackNumber:
            audio[MetaDataType.TRACK_NUMBER.value] = self.trackNumber
        audio.save()

    def setPlaylistName(self, playlistName):
        self.playlistName = playlistName


class MetaDataManager():

    def setMetaDataPlaylist(self, playlistName, trackList, directoryPath):
        """Method used to set Metadata for playlist

        Args:
            playlistName (str): palylist name form meta data
            trackList (list): list of dicts with trucks meta data
        """
        for trackMetaData in trackList:
            easyID3Media = EasyID3MediaFromPlaylist.initFromMediaFromPlaylist(trackMetaData)
            easyID3Media.setFilePath(directoryPath)
            easyID3Media.setPlaylistName(playlistName)
            easyID3Media.saveMetaData()
            self._showMetaDataInfo(easyID3Media.filePath)

    def setMetaDataSingleFile(self, media, directoryPath):
        if isinstance(media, EasyID3MediaFromPlaylist):
            easyID3Media = EasyID3MediaFromPlaylist.initFromMediaFromPlaylist(media)
        else:
            easyID3Media = EasyID3SingleMedia.initFromSingleMata(media)
        easyID3Media.setFilePath(directoryPath)
        easyID3Media.saveMetaData()
        self._showMetaDataInfo(easyID3Media.filePath)

    def _showMetaDataInfo(self, path):  # pragma: no_cover
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        audioInfo = MP3(path, ID3=EasyID3)
        logger.info(audioInfo.pprint())
