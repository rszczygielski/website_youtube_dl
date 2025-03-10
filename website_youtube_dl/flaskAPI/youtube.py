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
    FlaskSingleMedia,
    FormatType)
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
    formatType = formData[YoutubeVariables.DOWNLOAD_TYP.value]
    app.logger.debug(f"{YoutubeLogs.SPECIFIED_FORMAT.value} {formatType}")
    fromatType = FormatType().initFromForm(formatType)
    if not youtubeURL:
        app.logger.warning(YoutubeLogs.NO_URL.value)
        downloadErrorEmit.sendEmitError(YoutubeLogs.NO_URL.value)
        return False
    isPlaylist = YoutubeVariables.URL_LIST.value in youtubeURL \
        and YoutubeVariables.URL_VIDEO.value not in youtubeURL
    fullFilePath = downloadCorrectData(youtubeURL, fromatType,
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
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    directoryPath = app.configParserManager.getSavePath()
    app.logger.info(
        f"{YoutubeLogs.VIDEO_DOWNLOADED.value}: {singleMedia.file_name}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return singleMedia.file_name


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
    singleMedia.file_name = str(singleMedia.file_name).replace(".webm", ".mp3")
    easyID3Manager = EasyID3Manager()
    easyID3Manager.setParams(filePath=singleMedia.file_name,
                             title=singleMedia.title,
                             album=singleMedia.album,
                             artist=singleMedia.artist,
                             ytHash=singleMedia.ytHash)
    easyID3Manager.saveMetaData()
    app.logger.info(
        f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return singleMedia.file_name


def downloadAudioFromPlaylist(singleMediaURL, playlistName, index):
    singleMediaInfoResult = app.youtubeDownloder.downloadAudio(singleMediaURL)
    if singleMediaInfoResult.isError():
        errorMsg = singleMediaInfoResult.getErrorInfo()
        handleError(errorMsg)
        return None
    singleMedia: SingleMedia = singleMediaInfoResult.getData()
    directoryPath = app.configParserManager.getSavePath()
    singleMedia.file_name = str(singleMedia.file_name).replace(".webm", ".mp3")
    easyID3Manager = EasyID3Manager()
    easyID3Manager.setParams(filePath=singleMedia.file_name,
                             title=singleMedia.title,
                             album=playlistName,
                             artist=singleMedia.artist,
                             ytHash=singleMedia.ytHash,
                             trackNumber=index)
    easyID3Manager.saveMetaData()
    app.logger.info(
        f"{YoutubeLogs.AUDIO_DOWNLOADED.value}: {singleMedia.file_name}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH.value}: {directoryPath}")
    return singleMedia.file_name


def downloadTracksFromPlaylist(youtubeURL, formatType):
    playlistMedia = sendEmitPlaylistMedia(youtubeURL)
    if not playlistMedia:
        return
    playlistTrackFinish = PlaylistTrackFinish()
    filePaths = []
    directoryPath = app.configParserManager.getSavePath()
    playlistTrack: MediaFromPlaylist
    downloadedFiles = getFilesFromDir(directoryPath)
    for index, playlistTrack in enumerate(playlistMedia.mediaFromPlaylistList):
        title = playlistTrack.title
        titleTemplate = generateTitleTemplateForYoutubeDownloader(downloadedFiles,
                                                                  title)
        app.youtubeDownloder.setTitleTemplateOneTime(
            titleTemplate)

        if formatType.mp3:
            fullPath = downloadAudioFromPlaylist(singleMediaURL=playlistTrack.ytHash,
                                                 playlistName=playlistMedia.playlistName,
                                                 index=str(index))
        else:
            videoType = formatType.get_selected_format()
            fullPath = downloadSingleVideo(singleMediaURL=playlistTrack.ytHash,
                                           videoType=videoType,
                                           sendFullEmit=False)
        if fullPath is None:  # napisz unittesty pod to
            playlistTrackFinish.sendEmitError(index)
            continue
        playlistTrackFinish.sendEmit(index)
        filePaths.append(fullPath)
        downloadedFiles.append(titleTemplate)
    zipNameFile = zipAllFilesInList(
        directoryPath, playlistMedia.playlistName, filePaths)
    app.logger.info(
        f"{YoutubeLogs.PLAYLIST_DOWNLAODED.value}: {playlistMedia.playlistName}")
    app.logger.debug(f"{YoutubeLogs.DIRECTORY_PATH}: {directoryPath}")
    fullZipPath = os.path.join(directoryPath, zipNameFile)
    return fullZipPath


def getFilesFromDir(dirPath):
    return [f.split(".")[0] for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]


def generateTitleTemplateForYoutubeDownloader(downloadedFiles,
                                              title):
    # https://www.youtube.com/playlist?list=PL6uhlddQJkfiCJfEQvnqzknbxfgBiGekb test
    counter = 1
    app.logger.info(downloadedFiles)
    while title in downloadedFiles:
        counter += 1
        title = f"{title} ({counter})"
    if counter > 1:
        return f"/%(title)s ({counter})"
    return "/%(title)s"


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


def downloadCorrectData(youtubeURL, fromatType, isPlaylist):
    if isPlaylist:
        fullFilePath = downloadTracksFromPlaylist(youtubeURL=youtubeURL,
                                                  fromatType=fromatType)
    elif fromatType.mp3 and not isPlaylist:
        fullFilePath = downloadSingleAudio(singleMediaURL=youtubeURL)
    elif not fromatType.mp3 and not isPlaylist:
        videoType = fromatType.get_selected_format()
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
