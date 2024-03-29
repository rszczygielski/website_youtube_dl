from mainWebPage import socketio
from abc import ABC
from common.youtubeDataKeys import PlaylistInfo
# from flaskAPI.youtube import FlaskSingleMedia


class SendEmitBase(ABC):
    _emitType = ""
    _emitDataStr = "data"
    _emitError = "error"

    def sendEmitSucces(self, emitData):
        socketio.emit(self._emitType, {self._emitDataStr: emitData})
    
    def sendSimpleEmit(self, emitMsg):
        socketio.emit(self._emitType, emitMsg)
    
    def sendEmitError(self, emitErrorMsg):
        socketio.emit(self._emitType, {self._emitError: emitErrorMsg})


class DownloadMediaFinishEmit(SendEmitBase):
    _emitType = "downloadMediaFinish"
    _hashStr = "HASH"

    def sendEmitWithData(self, generatedHash):
        emitData = {self._hashStr: generatedHash}
        self.sendEmitSucces(emitData)


class MediaInfoEmit(SendEmitBase):
    _emitType = "mediaInfo"

    def getPlaylistData(self, playlistInfo:PlaylistInfo):
        playlistTrackList = []
        playlistName = playlistInfo.playlistName
        for track in playlistInfo.singleMediaList:
            trackInfoDict = {
                PlaylistInfo.TITLE.value: track.title, PlaylistInfo.ALBUM.value: track.album,
                PlaylistInfo.ARTIST.value: track.artist, PlaylistInfo.YOUTUBE_HASH.value: track.ytHash,
                PlaylistInfo.URL.value: track.url, PlaylistInfo.PLAYLIST_INDEX.value: track.playlistIndex,
                PlaylistInfo.PLAYLIST_NAME.value: playlistName
            }
            playlistTrackList.append(trackInfoDict)
        return playlistTrackList

    def getSingleMediaData(self, mediaInfo):
        mediaInfoDict = {
            PlaylistInfo.TITLE.value: mediaInfo.title,
            PlaylistInfo.ARTIST.value: mediaInfo.artist,
            PlaylistInfo.URL.value: mediaInfo.url
        }
        return [mediaInfoDict]

    def sendEmitSingleMedia(self, mediaInfo):
        mediaInfoData = self.getSingleMediaData(mediaInfo)
        self.sendEmitSucces(mediaInfoData)

    def sendEmitPlaylist(self, playlistInfo):
        palylistData = self.getPlaylistData(playlistInfo)
        self.sendEmitSucces(palylistData)


class DownloadErrorEmit(SendEmitBase):
    _emitType = "downloadError"
    _noFormat = "Format not specified"
    _noURL =  "Youtube URL empty"

    def sendEmitFormatNotSpecified(self):
        self.sendSimpleEmit(self._noFormat)
    
    def sendEmitNoURL(self):
        self.sendSimpleEmit(self._noURL)
