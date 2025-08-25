var socket = io()

class SingleMedia {
    constructor(title, artist, url) {
        this.title = title;
        this.artist = artist;
        this.url = url;
    }
}

class SingleMediaFromPlaylist {
    constructor(title, url) {
        this.title = title;
        this.url = url
    }
}

class PlaylistMedia {
    constructor(playlistName, sessionHash, trackList){
        this.playlistName = playlistName;
        this.sessionHash = sessionHash;
        this.trackList = trackList;
    }
}

class DownloadMediaFinish{
    constructor(hash) {
        this.hash = hash
    }
}

class FormData{

    constructor(youtubeURL, downloadType, sessionId){
        this.youtubeURL = youtubeURL
        this.downloadType = downloadType
        this.sessionId = sessionId
    }
}

class AddPlaylist{

    constructor(playlistName, playlist_url){
        this.playlistName = playlistName
        this.playlist_url = playlist_url
    }
}

class PlaylistName{
    constructor(playlistName){
        this.playlistName = playlistName
    }
}

class UploadPlaylists{
    constructor(playlistList){
        this.playlistList = playlistList
    }
}

class PlaylistUrl{
    constructor(playlistUrl) {
        this.playlistUrl = playlistUrl
    }
}

class PlaylistIndex{
    constructor(index){
        this.index = index
    }
}

class HistoryInfo {
    constructor(trackList) {
        this.trackList = trackList;
    }
}

class BaseReceiver{
    constructor (requestJson){
        this.requestJson = requestJson;
    }

    isError(){
        if ("error" in this.requestJson){
            return true
        }
        return false
    }

    getError(){
        if ("error" in this.requestJson){
            return this.requestJson["error"]
        }
    }

    convertMessageToData(){
    }

    getData(){
        if ("data" in this.requestJson){
            return this.convertMessageToData(this.requestJson["data"])
        }
    }
}

class HistoryInfoEmitReceiver extends BaseReceiver {
    static emitMsg = "historyInfo";

    constructor(requestJson) {
        super(requestJson);
    }

    convertMessageToData(data) {
        // data to lista obiektów {title, url}
        var singleMediaArr = [];
        for (var track of data) {
            singleMediaArr.push(new SingleMediaFromPlaylist(track["title"], track["url"]));
        }
        return new HistoryInfo(singleMediaArr);
    }
}

class PlaylistMediaEmitReceiver extends BaseReceiver {
    static emitMsg = "playlistMediaInfo"

    constructor(requestJson){
        super(requestJson)
    }

    convertMessageToData(data) {
        var playlistName = data["playlistName"]
        var trackList = data["trackList"]
        var sessionHash = data["sessionHash"]


        var singleMediaArr = []
        for (var track of trackList) {
            console.log(track)
            singleMediaArr.push(new SingleMediaFromPlaylist(track["title"],
                                            track["url"]))
        }
        return new PlaylistMedia(playlistName, sessionHash, singleMediaArr)
    }
}

class SingleMediaEmitReceiver extends BaseReceiver {
    static emitMsg = "mediaInfo"

    constructor(requestJson){
        super(requestJson)
    }

    convertMessageToData(data) {
        console.log(data)
        return new SingleMedia(data["title"],
                           data["artist"],
                           data["webpage_url"])
    }
}

class DownloadMediaFinishReceiver extends BaseReceiver {
    static emitMsg = "downloadMediaFinish"

    constructor(requestJson){
        super(requestJson)
    }

    convertMessageToData(data) {
        var hash = data["HASH"]
        return new DownloadMediaFinish(hash)
    }
}

class UploadPlaylistsReceiver extends BaseReceiver {
    static emitMsg = "uploadPlaylists"

    constructor(requestJson){
        super(requestJson)
    }

    convertMessageToData(data) {
        var playlistList = data["playlistList"]
        return new UploadPlaylists(playlistList)
    }
}

class PlaylistUrlReceiver extends BaseReceiver {
    static emitMsg = "playlistUrl"

    constructor(requestJson){
        super(requestJson)
    }

    convertMessageToData(data) {
        var playlistUrl = data["playlistUrl"]
        return new PlaylistUrl(playlistUrl)
    }
}

class PlaylistTrackFinishReceiver extends BaseReceiver {
    static emitMsg = "playlistTrackFinish"

    constructor(requestJson){
        super(requestJson)
    }

    convertMessageToData(data) {
        var index = data["index"]
        return new PlaylistIndex(index)
    }
}

class BaseEmit {

    constructor(emitMsg){
        this.emitMsg = emitMsg
    }

    convert_data_to_message(){
    }

    sendEmit(data){
        var convertedData = this.convert_data_to_message(data)
        socket.emit(this.emitMsg, convertedData)
    }
}

class EmitFormData extends BaseEmit {

    constructor(){
        var emitMsg = "FormData"
        super(emitMsg)
        this.emitMsg = emitMsg

    }

    /**
     * @param {FormData} data
     */
    convert_data_to_message(formData){
        return {
            "youtubeURL": formData.youtubeURL,
            "downloadType": formData.downloadType,
            "sessionId": formData.sessionId
        }
    }
}


class EmitAddPlaylist extends BaseEmit {

    constructor(){
        var emitMsg = "addPlaylist"
        super(emitMsg)
        this.emitMsg = emitMsg
    }

    /**
     * @param {AddPlaylist} data
     */
    convert_data_to_message(addPlaylist){
        return {
            "playlistName": addPlaylist.playlistName,
            "playlistURL": addPlaylist.playlistURL
        }
    }
}


class EmitDeletePlaylist extends BaseEmit {

    constructor(){
        var emitMsg = "deletePlaylist"
        super(emitMsg)
        this.emitMsg = emitMsg
    }

    /**
     * @param {PlaylistName} data
     */
    convert_data_to_message(playlistName){
        return {
            "playlistToDelete": playlistName.playlistName
        }
    }
}


class EmitPlaylistName extends BaseEmit {

    constructor(){
        var emitMsg = "playlistName"
        super(emitMsg)
        this.emitMsg = emitMsg
    }

    /**
     * @param {PlaylistName} data
     */
    convert_data_to_message(playlistName){
        return {
            "playlistName": playlistName.playlistName
        }
    }
}


class EmitDownloadFromConfigFile extends BaseEmit {

    constructor(){
        var emitMsg = "downloadFromConfigFile"
        super(emitMsg)
        this.emitMsg = emitMsg
    }

    /**
     * @param {PlaylistName} data
     */
    convert_data_to_message(playlistName){
        return {
            "playlistToDownload": playlistName.playlistName
        }
    }
}