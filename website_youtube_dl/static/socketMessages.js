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
    constructor(playlistName, trackList){
        this.playlistName = playlistName;
        this.trackList = trackList;
    }
}

class FlaskResultHash{
    constructor(hash) {
        this.hash = hash
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

class PlaylistMediaEmitReceiver extends BaseReceiver {
    static emitMsg = "playlistMediaInfo"

    constructor(requestJson){
        super(requestJson)
    }

    convertMessageToData(data) {
        var playlistName = data["playlist_name"]
        var trackList = data["trackList"]
        var singleMediaArr = []
        console.log(trackList)
        console.log(typeof(trackList))
        console.log(Array.isArray(trackList))
        for (var track of trackList) {
            console.log(track)
            singleMediaArr.push(new SingleMediaFromPlaylist(track["title"],
                                            track["url"]))
        }
        return new PlaylistMedia(playlistName, singleMediaArr)
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


class FormData{

    constructor(youtubeURL, downloadType){
        this.youtubeURL = youtubeURL
        this.downloadType = downloadType
    }
}

class BaseEmit {

    constructor(emitMsg){
        this.emitMsg = emitMsg
    }

    convertDataToMessage(){
    }

    sendEmit(data){
        var convertedData = this.convertDataToMessage(data)
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
    convertDataToMessage(formData){
        return {
            "youtubeURL": formData.youtubeURL,
            "downloadType": formData.downloadType
        }
    }
}
