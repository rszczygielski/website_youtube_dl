import yt_dlp
import configparser
import argparse
import sys
from enum import Enum, auto
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class MetaDataType(Enum):
    TITLE = 'title'
    ALBUM = 'album'
    ARTIST = 'artist'
    PLAYLIST_INDEX = 'playlist_index'

class YoutubeDL():
    def __init__(self, configFilePath):
        config = configparser.ConfigParser()
        config.read(configFilePath)
        self.savePath = config["global"]["path"]
        self.playlistList = []
        for key in config["playlists"]:  
            self.playlistList.append(config["playlists"][key])
        self.ydl_video_opts = {
        # 'download_archive': 'downloaded_songs.txt',
        'addmetadata': True,
        }
    
    def downloadFile(self, youtubeURL:str, youtubeOptions:dict):
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
        print("#" * 50)
        print(self.ydl_video_opts["outtmpl"])
        return self.downloadFile(youtubeURL, self.ydl_video_opts)

    def downoladConfigPlaylistVideo(self, type):
        """Method used to download all playlists added to cofig file - type video
        """
        self.setVideoOptions(type)
        for playlistURL in self.playlistList:
            playlistHash = playlistURL[playlistURL.index("=") + 1:]
            self.downloadFile(playlistHash, self.ydl_video_opts)

    def terminalDoubleHashedLinkVideo(self, videoHash, playlistHash, type):
        userResponse = input("""
        Playlist link detected. 
        If you want to download single video/audio press 's'
        If you want to download whole playlist press 'p'
        """)
        if userResponse == "s":
            hashToDownload = videoHash
        elif userResponse == "p":
            hashToDownload = playlistHash
        else:
            raise ValueError("Please enter 's' for single video or 'p' for playlist")
        self.downloadVideo(hashToDownload, type)
    
    @staticmethod
    def getVideoHash(link):
        """Class method which initialize the class from HTTP link string

        Args:
            link (str): HTTP link

        Returns:
            class: instance of ExaminateURL class
        """
        if link == None:
            return None, None
        onlyHashesInLink = link.split("?")[1]
        numberOfEqualSign = link.count("=")
        if numberOfEqualSign > 2:
            splitedHashes = onlyHashesInLink.split("=")
            videoHash = splitedHashes[1][:splitedHashes[1].index("&")]
            playlistHash = splitedHashes[2][:splitedHashes[2].index("&")]
            return videoHash, playlistHash
        elif numberOfEqualSign == 2:
            splitedHashes = onlyHashesInLink.split("=")
            videoHash = splitedHashes[1][:splitedHashes[1].index("&")]
            playlistHash = splitedHashes[2]
            return videoHash, playlistHash
        elif numberOfEqualSign == 1:
            if "list=" in onlyHashesInLink:
                playlistHash = onlyHashesInLink[5:]
                return None, playlistHash
            else:
                videoHash = onlyHashesInLink[2:]
                return videoHash, None
    
class AudioYoutube(YoutubeDL):
    def __init__(self, configFilePath):
        super().__init__(configFilePath)
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
    
    def downloadAudio(self, youtubeURL:str):
        """Method uded to download audio type from Youtube, convert metadata 
        into mp3 format used mutagen.easyid3

        Args:
            youtubeURL (str): YouTube URL
        """
        metaData = self.downloadFile(youtubeURL, self.ydl_audio_opts)
        self.setMetaDataSingleFile(metaData)
        return metaData

    def downloadAudioPlaylist(self, youtubeURL:str):
        metaData = self.downloadFile(youtubeURL, self.ydl_audio_opts)
        self.setMetaDataPlaylist(metaData)
        return metaData

    def downoladConfigPlaylistAudio(self):
        """Method used to dowload all playlists added to cofig file - type audio
        """
        for playlistURL in self.playlistList:
            playlistHash = playlistURL[playlistURL.index("=") + 1:]
            metaData = self.downloadFile(playlistHash, self.ydl_audio_opts)
            self.setMetaDataPlaylist(metaData)

    def setMetaDataSingleFile(self, metaData):
        """Method used to set meta data for the single file

        Args:
            metaData (class): Metadata
        """
        metaDataDict = self.getMetaDataDict(metaData)
        path = f'{self.savePath}/{metaDataDict["title"]}.mp3'
        self.saveMetaData(metaDataDict, path)
        self.showMetaDataInfo(path)
    
    def showMetaDataInfo(self, path):
        """Method used to show Metadata info

        Args:
            path (str): file path
        """
        audioInfo = MP3(path, ID3=EasyID3)
        print(audioInfo.pprint())
    
    def saveMetaData(self, metaDataDict, path):
        """Method used to set Metadata

        Args:
            metaDataDict (dict): Metadata dict  
            path (str): file path
        """
        audio = EasyID3(path)
        for data in metaDataDict:
            if data == "playlist_index":
                audio['tracknumber'] = str(metaDataDict[data])
                continue
            audio[data] = metaDataDict[data]
        audio.save()

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
    
    def setMetaDataPlaylist(self, metaData):
        """Method used to set Metadata for playlist

        Args:
            metaData (class): Metadata
        """
        playlistName = metaData["title"]
        for trackMetaData in metaData['entries']:
            metaDataDict = self.getMetaDataDict(trackMetaData)
            path = f'{self.savePath}/{metaDataDict["title"]}.mp3'
            self.saveMetaData(metaDataDict, path)
            audio = EasyID3(path)
            audio['album'] = playlistName
            audio.save()
            self.showMetaDataInfo(path)
    
    def downloadDoubleHashedLinkAudio(self, videoHash, playlistHash):
        userResponse = input("""
        Playlist link detected. 
        If you want to download single video/audio press 's'
        If you want to download whole playlist press 'p'
        """)
        if userResponse == "s":
            hashToDownload = videoHash
            self.downloadAudio(hashToDownload)
        elif userResponse == "p":
            hashToDownload = playlistHash
            self.downloadAudioPlaylist(hashToDownload)
        else:
            raise ValueError("Please enter 's' for single video or 'p' for playlist")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Program downloads mp3 form given youtube URL")
    parser.add_argument("-l", metavar="link", dest="link",
    help="Link to the youtube video")
    parser.add_argument("-t", metavar="type", dest="type", choices=['360','480', '720', '1080', '4k', 'mp3'], default="1080",
    help="Select downolad type --> ['360', '720', '1080', '2160', 'mp3'], default: 1080")
    parser.add_argument("-c", metavar="config", dest= "config", default="youtube_config.ini",
    help="Path to the config file --> default youtube_config.ini")
    args = parser.parse_args()
    link = args.link
    type = args.type
    config= args.config
    videoHash, playlistHash = AudioYoutube.getVideoHash(link)
    terminalUser = AudioYoutube(config)
    if type == "mp3":
        if link == None:
            terminalUser.downoladConfigPlaylistAudio()
        elif videoHash and playlistHash:
            terminalUser.downloadDoubleHashedLinkAudio(videoHash, playlistHash)
        elif videoHash and playlistHash == None:
            terminalUser.downloadAudio(videoHash)
        elif videoHash == None and playlistHash:
            terminalUser.downloadAudioPlaylist(playlistHash)
    else:
        if link == None:
            terminalUser.downoladConfigPlaylistVideo(type)
        elif videoHash and playlistHash:
            terminalUser.terminalDoubleHashedLinkVideo(videoHash, playlistHash, type)
        else:
            terminalUser.downloadVideo(link, type)

    # do weba no-playlist argument i po błedzie
    # https://github.com/yt-dlp/yt-dlp#video-selection
