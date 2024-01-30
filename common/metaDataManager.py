from common.youtubeDataKeys import MetaDataType
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import logging

logger = logging.getLogger(__name__)

class EasyID3SingleMedia():
    filePath = ""
    playlistName = ""

    def __init__(self, title, album, artist, trackNumber):
        self.title = title
        self.album = album
        self.artist = artist
        self.trackNumber = trackNumber

    def setPlaylistName(self, playlistName):
        self.playlistName = playlistName

    def setFilePath(self, directoryPath):
        self.filePath = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(self.title)}.mp3'

    def isPlaylist(self):
        if not self.playlistName:
            return False
        else:
            return True

    def replaceNoneValues(self, *args):
        valuesList = []
        for value in args:
            if value == None:
                valuesList.append("")
                continue
            valuesList.append(value)
        return valuesList

    @classmethod
    def initFromMatadata(cls, metaData):
        title = album = artist = playlistIndex = ""
        if MetaDataType.TITLE.value in metaData:
            title = yt_dlp.utils.sanitize_filename(metaData[MetaDataType.TITLE.value])
        if MetaDataType.ALBUM.value in metaData:
            album = metaData[MetaDataType.ALBUM.value]
        if MetaDataType.ARTIST.value in metaData:
            artist = metaData[MetaDataType.ARTIST.value]
        if MetaDataType.PLAYLIST_INDEX.value in metaData:
            playlistIndex = metaData[MetaDataType.PLAYLIST_INDEX.value]
        return cls(title, album, artist, playlistIndex)

class MetaDataManager():

    def setMetaDataPlaylist(self, playlistName, trackList, directoryPath):
        """Method used to set Metadata for playlist

        Args:
            playlistName (str): palylist name form meta data
            trackList (list): list of dicts with trucks meta data
        """
        for trackMetaData in trackList:
            easyID3Media = EasyID3SingleMedia.initFromMatadata(trackMetaData)
            easyID3Media.setFilePath(directoryPath)
            easyID3Media.setPlaylistName(playlistName)
            self._saveMetaData(easyID3Media)
            self._showMetaDataInfo(easyID3Media.filePath)

    def setMetaDataSingleFile(self, easyID3Media, directoryPath):
        easyID3Media.setFilePath(directoryPath)
        self._saveMetaData(easyID3Media)
        self._showMetaDataInfo(easyID3Media.filePath)

    def _saveEasyID3(self, easyid3Instance): #pragma: no_cover
        easyid3Instance.save()

    def _saveMetaData(self, easyID3Media:EasyID3SingleMedia):
        print(easyID3Media.filePath)
        audio = EasyID3(easyID3Media.filePath)
        if easyID3Media.title:
            audio[MetaDataType.TITLE.value] = easyID3Media.title
        if easyID3Media.isPlaylist():
            if easyID3Media.playlistName:
                audio[MetaDataType.ALBUM.value] = easyID3Media.playlistName
        else:
            if easyID3Media.album:
                audio[MetaDataType.ALBUM.value] = easyID3Media.album
        if easyID3Media.artist:
            audio[MetaDataType.ARTIST.value] = easyID3Media.artist
        if easyID3Media.trackNumber:
            audio[MetaDataType.TRACK_NUMBER.value] = easyID3Media.trackNumber
        self._saveEasyID3(audio)

    def _showMetaDataInfo(self, path): #pragma: no_cover
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        audioInfo = MP3(path, ID3=EasyID3)
        logger.info(audioInfo.pprint())