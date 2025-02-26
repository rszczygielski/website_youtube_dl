from ..common.youtubeDL import (SingleMedia,
                                PlaylistMedia,
                                MediaFromPlaylist,
                                ResultOfYoutube)
from ..common.youtubeLogKeys import (YoutubeLogs,
                                     YoutubeVariables)
from ..common.easyID3Manager import EasyID3Manager
from flask import (send_file,
                   render_template,
                   Blueprint)
from flask import current_app as app
from .emits import (DownloadMediaFinishEmit,
                    SingleMediaInfoEmit,
                    PlaylistMediaInfoEmit,
                    PlaylistTrackFinish)
from .session import SessionDownloadData
from .flaskMedia import (
    FlaskPlaylistMedia,
    FlaskSingleMedia)
import zipfile
import os
import yt_dlp
import random
import string
from .. import socketio

youtube = Blueprint("youtube", __name__)


@socketio.on("FormData")
def socketDownloadServer(formData):
    app.logger.debug(formData)
    youtubeURL = formData[YoutubeVariables.YOUTUBE_URL.value]
    downloadErrorEmit = DownloadMediaFinishEmit()
    if YoutubeVariables.DOWNLOAD_TYP.value not in formData:
        app.logger.warning(YoutubeLogs.NO_FORMAT.value)
        downloadErrorEmit.sendEmitError(YoutubeLogs.NO_FORMAT.value)
        return False
    type = formData[YoutubeVariables.DOWNLOAD_TYP.value]
    app.logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {type}")
    if not youtubeURL:
        app.logger.warning(YoutubeLogs.NO_URL.value)
        downloadErrorEmit.sendEmitError(YoutubeLogs.NO_URL.value)
        return False
    isPlaylist = YoutubeVariables.URL_LIST.value in youtubeURL \
        and YoutubeVariables.URL_VIDEO.value not in youtubeURL
    fullFilePath = downloadCorrectData(youtubeURL, type,
                                       isPlaylist)
    if not fullFilePath:
        app.logger.error("No file path returned")
        return False
    sessionDownloadData = SessionDownloadData(fullFilePath)
    genereted_hash = generateHash()
    app.session.addElemtoSession(genereted_hash, sessionDownloadData)
    emitDownloadFinish = DownloadMediaFinishEmit()
    emitDownloadFinish.sendEmit(genereted_hash)


@youtube.route("/downloadFile/<name>")
def downloadFile(name):
    app.session.ifElemInSession(name)
    sessionDownloadData = app.session.getSessionElem(
        name)
    downloadFileName = yt_dlp.utils.sanitize_filename(
        sessionDownloadData.fileName)
    fullPath = os.path.join(
        sessionDownloadData.fileDirectoryPath, downloadFileName)
    app.logger.info(YoutubeLogs.SENDING_TO_ATTACHMENT.value)
    return send_file(fullPath, as_attachment=True)


@youtube.route("/youtube.html")
def youtube_html():
    return render_template("youtube.html")


@youtube.route("/")
@youtube.route("/index.html")
@youtube.route('/example')
def index():
    return render_template('index.html')


def downloadSingleVideo(singleMediaURL, videoType, sendFullEmit=True):
    if sendFullEmit:
        if not sendEmitSingleMediaInfoFromYoutube(singleMediaURL):
            return False
    singleMediaInfoResult = app.youtubeDownloder.downloadVideo(
        singleMediaURL, videoType)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return None
    trackInfo = singleMediaInfoResult.getData()
    directoryPath = app.configParserManager.getSavePath()
    fileName = f"{trackInfo.title}_{videoType}p.{trackInfo.extension}"
    app.logger.info(f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {fileName}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)


def downloadSingleAudio(singleMediaURL):
    if not sendEmitSingleMediaInfoFromYoutube(singleMediaURL):
        return
    singleMediaInfoResult = app.youtubeDownloder.downloadAudio(singleMediaURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    directoryPath = app.configParserManager.getSavePath()
    filePath = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(singleMedia.title)}.mp3'
    easyID3Manager = EasyID3Manager()
    easyID3Manager.setParams(filePath=filePath,
                             title=singleMedia.title,
                             album=singleMedia.album,
                             artist=singleMedia.artist,
                             ytHash=singleMedia.ytHash)
    easyID3Manager.saveMetaData()
    fileName = f"{singleMedia.title}.{YoutubeVariables.MP3.value}"
    app.logger.info(f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {fileName}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)


def downloadAudioFromPlaylist(singleMediaURL, playlistName, index):
    singleMediaInfoResult = app.youtubeDownloder.downloadAudio(singleMediaURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return None
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    directoryPath = app.configParserManager.getSavePath()
    filePath = f'{directoryPath}/{yt_dlp.utils.sanitize_filename(singleMedia.title)}.mp3'
    easyID3Manager = EasyID3Manager()
    easyID3Manager.setParams(filePath=filePath,
                             title=singleMedia.title,
                             album=playlistName,
                             artist=singleMedia.artist,
                             ytHash=singleMedia.ytHash,
                             trackNumber=index)
    easyID3Manager.saveMetaData()
    fileName = f"{singleMedia.title}.{YoutubeVariables.MP3.value}"
    app.logger.info(f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {fileName}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return os.path.join(directoryPath, fileName)


def downloadTracksFromPlaylist(youtubeURL, videoType):
    playlistMedia = sendEmitPlaylistMedia(youtubeURL)
    if not playlistMedia:
        return
    playlistTrackFinish = PlaylistTrackFinish()
    filePaths = []
    directoryPath = app.configParserManager.getSavePath()
    downloadedFiles = getFilesFromDir(directoryPath)
    playlistTrack: MediaFromPlaylist
    for index, playlistTrack in enumerate(playlistMedia.mediaFromPlaylistList):
        title = playlistTrack.title
        setTitleTemplateForYoutubeDownloader(downloadedFiles, title)
        if not videoType:
            fullPath = downloadAudioFromPlaylist(singleMediaURL=playlistTrack.ytHash,
                                                playlistName=playlistMedia.playlistName,
                                                index=str(index))
        else:
            fullPath = downloadSingleVideo(singleMediaURL=playlistTrack.ytHash,
                                           videoType=videoType,
                                           sendFullEmit=False)
        if fullPath is None:  # napisz unittesty pod to
            playlistTrackFinish.sendEmitError(index)
            continue
        playlistTrackFinish.sendEmit(index)
        filePaths.append(fullPath)
        downloadedFiles.append(title)
    zipNameFile = zipAllFilesInList(
        directoryPath, playlistMedia.playlistName, filePaths)
    app.logger.info(
        f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlistMedia.playlistName}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directoryPath}")
    fullZipPath = os.path.join(directoryPath, zipNameFile)
    return fullZipPath

def getFilesFromDir(dirPath):
    return [f.split(".")[0] for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]


def setTitleTemplateForYoutubeDownloader(downloadedFiles,
                                         title):
    # https://www.youtube.com/playlist?list=PL6uhlddQJkfiCJfEQvnqzknbxfgBiGekb test
    counter = 1
    while title in downloadedFiles:
        counter += 1
        title = f"{title} ({counter})"
    if counter > 1:
        app.youtubeDownloder.setTitleTemplateOneTime(
            f"/%(title)s ({counter})")

def sendEmitSingleMediaInfoFromYoutube(singleMediaURL):
    singleMediaInfoResult: ResultOfYoutube = app.youtubeDownloder.requestSingleMediaInfo(
        singleMediaURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return False
    mediaInfo: SingleMedia = singleMediaInfoResult.getData()
    flaskSingleMedia = FlaskSingleMedia(mediaInfo.title,
                                        mediaInfo.artist,
                                        mediaInfo.url)
    mediaInfoEmit = SingleMediaInfoEmit()
    mediaInfoEmit.sendEmit(flaskSingleMedia)
    return True

def sendEmitPlaylistMedia(youtubeURL):
    app.logger.debug(YoutubeLogs.DOWNLAOD_PLAYLIST.value)
    playlistMediaInfoResult = app.youtubeDownloder.requestPlaylistMediaInfo(
        youtubeURL)
    if playlistMediaInfoResult.isError():
        errorMsg = playlistMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return None
    playlistMedia: PlaylistMedia = playlistMediaInfoResult.getData()
    playlistName = playlistMedia.playlistName
    flaskPlaylistMedia = FlaskPlaylistMedia.initFromPlaylistMedia(playlistName,
                                                                  playlistMedia.mediaFromPlaylistList)
    playlistInfoEmit = PlaylistMediaInfoEmit()
    playlistInfoEmit.sendEmit(flaskPlaylistMedia)
    return playlistMedia


def downloadCorrectData(youtubeURL, videoType, isPlaylist):
    if videoType == YoutubeVariables.MP3.value and isPlaylist:
        fullFilePath = downloadTracksFromPlaylist(youtubeURL=youtubeURL,
                                                  videoType=None)
    elif videoType != YoutubeVariables.MP3.value and isPlaylist:
        fullFilePath = downloadTracksFromPlaylist(youtubeURL=youtubeURL,
                                                  videoType=videoType)
    elif videoType == YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleAudio(singleMediaURL=youtubeURL)
    elif videoType != YoutubeVariables.MP3.value and not isPlaylist:
        fullFilePath = downloadSingleVideo(singleMediaURL=youtubeURL,
                                           videoType=videoType)
    return fullFilePath


def zipAllFilesInList(direcoryPath, playlistName, listOfFilePaths):  # pragma: no_cover
    zipFileFullPath = os.path.join(direcoryPath,
                                   playlistName)
    with zipfile.ZipFile(f"{zipFileFullPath}.zip", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{zipFileFullPath.split('/')[-1]}.zip"


def handleError(errorMsg):  # pragma: no_cover
    downloadMediaFinishEmit = DownloadMediaFinishEmit()
    downloadMediaFinishEmit.sendEmitError(errorMsg)
    app.logger.error(
        f"{YoutubeLogs.MEDIA_INFO_DOWNLAOD_ERROR.value}: {errorMsg}")


def generateHash():
    return ''.join(random.sample(
        string.ascii_letters + string.digits, 6))
