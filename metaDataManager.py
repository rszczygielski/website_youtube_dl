from enum import Enum
import yt_dlp
from mutagen.easyid3 import EasyID3
import mutagen.easyid3
from mutagen.mp3 import MP3

class MetaDataType(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'
    PLAYLIST_INDEX = 'playlist_index'

class MetaDataManager():

    def setMetaDataPlaylist(self, metaData, directoryPath):
        """Method used to set Metadata for playlist

        Args:
            metaData (class): Metadata
        """
        playlistName = metaData["title"]
        for trackMetaData in metaData['entries']:
            metaDataDict = self.getMetaDataDict(trackMetaData)
            path = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(metaDataDict["title"])}.mp3'
            self.saveMetaDataForPlaylist(metaDataDict, path, playlistName)
            self.showMetaDataInfo(path)

    def setMetaDataSingleFile(self, metaData, directoryPath):
        """Method used to set meta data for the single file

        Args:
            metaData (class): Metadata
        """
        metaDataDict = self.getMetaDataDict(metaData)
        path = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(metaDataDict["title"])}.mp3'
        self.saveMetaDataForSingleFile(metaDataDict, path)
        self.showMetaDataInfo(path)

    def getMetaDataDict(self, metaData):
        """Method returns metadata dict based on metadata taken form Youtube video

        Args:
            metaData (dict): Metadata dict

        Returns:
            dict: Metadata dict from YouTube
        """
        metaDataDict = {}
        for data in MetaDataType:
            if data.value in metaData:
                metaDataDict[data.value] = metaData[data.value]
        return metaDataDict

    def saveEasyID3(self, easyid3Instance): #pragma: no_cover
        easyid3Instance.save()

    def saveMetaDataForPlaylist(self, metaDataDict, path, playlistName):
        audio = mutagen.easyid3.EasyID3(path)
        for data in metaDataDict:
            if data == "playlist_index":
                audio['tracknumber'] = str(metaDataDict[data])
                continue
            elif data == "album":
                audio['album'] = playlistName
            else:
                audio[data] = metaDataDict[data]
        self.saveEasyID3(audio)

    def saveMetaDataForSingleFile(self, metaDataDict, path):
        """Method used to set Metadata

        Args:
            metaDataDict (dict): Metadata dict
            path (str): file path
        """
        audio = mutagen.easyid3.EasyID3(path)
        for data in metaDataDict:
            if data == "playlist_index":
                audio['tracknumber'] = str(metaDataDict[data])
                continue
            audio[data] = metaDataDict[data]
        self.saveEasyID3(audio)

    def showMetaDataInfo(self, path): #pragma: no_cover
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        audioInfo = MP3(path, ID3=mutagen.easyid3.EasyID3)
        print(audioInfo.pprint())