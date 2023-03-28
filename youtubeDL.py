import yt_dlp
import configparser
import os
import argparse
from enum import Enum
# from mutagen.easyid3 import EasyID3
import mutagen.easyid3
from mutagen.mp3 import MP3

class MetaDataType(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'
    PLAYLIST_INDEX = 'playlist_index'

class MetaData():
    def __init__(self, directoryPath):
        self.directoryPath = directoryPath

    def setMetaDataPlaylist(self, metaData):
        """Method used to set Metadata for playlist

        Args:
            metaData (class): Metadata
        """
        playlistName = metaData["title"]
        for trackMetaData in metaData['entries']:
            metaDataDict = self.getMetaDataDict(trackMetaData)
            path = f'{self.directoryPath}/{yt_dlp.utils.sanitize_filename(metaDataDict["title"])}.mp3'
            self.saveMetaDataForPlaylist(metaDataDict, path, playlistName)
            self.showMetaDataInfo(path)

    def setMetaDataSingleFile(self, metaData):
        """Method used to set meta data for the single file

        Args:
            metaData (class): Metadata
        """
        metaDataDict = self.getMetaDataDict(metaData)
        path = f'{self.directoryPath}/{yt_dlp.utils.sanitize_filename(metaDataDict["title"])}.mp3'
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

class YoutubeDL(MetaData):
    def __init__(self, configFilePath):
        self.configFilePath = configFilePath
        self.config = configparser.ConfigParser()
        self.config.read(self.configFilePath)
        self.savePath = self.config["global"]["path"]
        super().__init__(self.savePath)
        self.ydl_video_opts = {
        "format": "bestvideo+bestaudio",
        # 'download_archive': 'downloaded_songs.txt',
        'addmetadata': True,
        }
        self.ydl_audio_opts = {
        "format": "bestvideo+bestaudio",
        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
        # 'download_archive': 'downloaded_songs.txt',
        'addmetadata': True,
        'outtmpl':  self.savePath + '/%(title)s.%(ext)s',
        }

    def downloadFile(self, youtubeURL:str, youtubeOptions:dict): #pragma: no_cover
        """Method used to download youtube media based on URL

        Args:
            youtubeURL (str): YouTube URL
            youtubeOptions (dict): YouTube options dict form init

        Returns:
            class: meta data form youtube
        """
        with yt_dlp.YoutubeDL(youtubeOptions) as ydl:
            return ydl.extract_info(youtubeURL)

    def setVideoOptions(self, type):
        self.ydl_video_opts['format'] = f'bestvideo[height={type}][ext=mp4]+bestaudio/bestvideo+bestaudio'
        if type == "2160":
            self.ydl_video_opts['outtmpl'] = self.savePath + '/%(title)s' + f'_4k' + '.%(ext)s'
        else:
            self.ydl_video_opts['outtmpl'] = self.savePath + '/%(title)s' + f'_{type}p' + '.%(ext)s'

    def downloadVideo(self, youtubeURL:str, type:str):
        """Method uded to download video type from YouTube

        Args:
            youtubeURL (str): YouTube URL
        """
        self.setVideoOptions(type)
        videoHash = self.getVideoHash(youtubeURL)
        return self.downloadFile(videoHash, self.ydl_video_opts)

    def downloadVideoPlaylist(self, youtubeURL:str, type:str):
        self.setVideoOptions(type)
        playlistHash = self.getPlaylistHash(youtubeURL)
        return self.downloadFile(playlistHash, self.ydl_video_opts)

    def downloadAudio(self, youtubeURL:str):
        """Method uded to download audio type from Youtube, convert metadata
        into mp3 format used mutagen.easyid3

        Args:
            youtubeURL (str): YouTube URL
        """
        videoHash = self.getVideoHash(youtubeURL)
        metaData = self.downloadFile(videoHash, self.ydl_audio_opts)
        self.setMetaDataSingleFile(metaData)
        return metaData

    def downloadAudioPlaylist(self, youtubeURL:str):
        playlistHash = self.getPlaylistHash(youtubeURL)
        metaData = self.downloadFile(playlistHash, self.ydl_audio_opts)
        self.setMetaDataPlaylist(metaData)
        return metaData

    def getPlaylistsFromConfig(self):
        playlistList = []
        config = configparser.ConfigParser()
        config.read(self.configFilePath)
        for key in config["playlists"]:
            playlistList.append(config["playlists"][key])
        return playlistList

    def downoladConfigPlaylistVideo(self, type):
        """Method used to download all playlists added to cofig file - type video
        """
        playlistList = self.getPlaylistsFromConfig()
        self.setVideoOptions(type)
        for playlistURL in playlistList:
            self.downloadVideoPlaylist(playlistURL, type)

    def downoladConfigPlaylistAudio(self):
        """Method used to dowload all playlists added to cofig file - type audio
        """
        playlistList = self.getPlaylistsFromConfig()
        for playlistURL in playlistList:
            self.downloadAudioPlaylist(playlistURL)

    def getVideoHash(self, url):
        onlyHashesInLink = url.split("?")[1]
        numberOfEqualSign = url.count("=")
        splitedHashes = onlyHashesInLink.split("=")
        if numberOfEqualSign == 1:
            if "list=" in onlyHashesInLink:
                raise ValueError("This is playlist")
            else:
                videoHash = onlyHashesInLink[2:]
                return videoHash
        elif numberOfEqualSign > 2:
            videoHash = splitedHashes[1][:splitedHashes[1].index("&")]
            return videoHash
        elif numberOfEqualSign == 2:
            videoHash = splitedHashes[1][:splitedHashes[1].index("&")]
            return videoHash

    def getPlaylistHash(self, url):
        onlyHashesInLink = url.split("?")[1]
        numberOfEqualSign = url.count("=")
        splitedHashes = onlyHashesInLink.split("=")
        if numberOfEqualSign == 1:
            if "list=" in onlyHashesInLink:
                playlistHash = onlyHashesInLink[5:]
                return playlistHash
            else:
                raise ValueError("This is not a playlist")
        elif numberOfEqualSign > 2:
            playlistHash = splitedHashes[2][:splitedHashes[2].index("&")]
            return playlistHash
        elif numberOfEqualSign == 2:
            playlistHash = splitedHashes[2]
            return playlistHash

    def addPlaylistToConfig(self, playlistName, playlistURL):
        self.config["playlists"][playlistName] = playlistURL
        with open(self.configFilePath, 'w') as configfile:
            self.config.write(configfile)

class TerminalUsage(YoutubeDL):
    def __init__(self, configFilePath) -> None:
        super().__init__(configFilePath)

    def isPlaylist(self, url):
        if url == None:
            return False
        elif "list=" in url:
            return True
        else:
            return False

    def ifDoubleHash(self, url):
        if url == None:
            return False
        elif "list=" in url and "v=" in url:
            return True
        else:
            return False

    def downloadDoubleHashedLinkVideo(self, url, type):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press 's'
        If you want to download whole playlist press 'p'
        """)
        if userResponse == "s":
            self.downloadVideo(url, type)
        elif userResponse == "p":
            self.downloadVideoPlaylist(url, type)
        else:
            raise ValueError("Please enter 's' for single video or 'p' for playlist")

    def downloadDoubleHashedLinkAudio(self, url):
        userResponse = input("""
        Playlist url detected.
        If you want to download single video/audio press 's'
        If you want to download whole playlist press 'p'
        """)
        if userResponse == "s":
            self.downloadAudio(url)
        elif userResponse == "p":
            self.downloadAudioPlaylist(url)
        else:
            raise ValueError("Please enter 's' for single video or 'p' for playlist")

    def downloadTerminal(self, url, type):
        if url == None and type == "mp3":
            self.downoladConfigPlaylistAudio()
            return
        elif url == None and type != "mp3":
            self.downoladConfigPlaylistVideo(type)
            return
        isPlaylist = self.isPlaylist(url)
        isDouble = self.ifDoubleHash(url)
        if isPlaylist and isDouble:
            if type == "mp3":
                self.downloadDoubleHashedLinkAudio(url)
            else:
                self.downloadDoubleHashedLinkVideo(url, type)
        elif isPlaylist and not isDouble:
            if type == "mp3":
                self.downloadAudioPlaylist(url)
            else:
                self.downloadVideoPlaylist(url, type)
        else:
            if type == "mp3":
                self.downloadAudio(url)
            else:
                self.downloadVideo(url, type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Program downloads mp3 form given youtube URL")
    parser.add_argument("-u", metavar="url", dest="url",
    help="Link to the youtube video")
    parser.add_argument("-t", metavar="type", dest="type", choices=['360','480', '720', '1080', '4k', 'mp3'], default="1080",
    help="Select downolad type --> ['360', '720', '1080', '2160', 'mp3'], default: 1080")
    parser.add_argument("-c", metavar="config", dest= "config", default="youtube_config.ini",
    help="Path to the config file --> default youtube_config.ini")
    args = parser.parse_args()
    url = args.url
    type = args.type
    config= args.config
    terminalUser = TerminalUsage(config)
    terminalUser.downloadTerminal(url, type)

    # do weba no-playlist argument i po błedzie
    # https://github.com/yt-dlp/yt-dlp#video-selection

