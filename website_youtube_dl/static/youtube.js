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

class MessageManager{
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

class PlaylistMediaEmitReceiver extends MessageManager {
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

class SingleMediaEmitReceiver extends MessageManager {
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
        this.ytURL = "youtubeURL"
        this.downloadType = "downloadType"
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


$(document).ready(function () {
    console.log("ready")
    socket.on('connect', function () {
        console.log("Connected Youtube");
    });
    socket.on('disconnect', function () {
        console.log("Disconnected Youtube");
    });
    var downloadForm = document.getElementById("DownloadForm");
    downloadForm.addEventListener("submit", function (event) {
        event.preventDefault();
        // allLogs = "";
        var traks_urls_table = document.getElementById("downloadInfo");
        traks_urls_table.innerHTML = "";
        var download_file_button = document.getElementById("downloadSection");
        download_file_button.innerHTML = "";
        var youtubeURL = document.getElementById("youtubeURL");
        var downloadTypes = document.getElementsByName("qualType");
        for (var i = 0; i < downloadTypes.length; i++) {
            if (downloadTypes[i].checked == true) {
                var downloadType = downloadTypes[i].value;
                console.log(downloadType)
                break;
            }
        }
        formData = new FormData(youtubeURL.value, downloadType)
        emitFormData = new EmitFormData()
        emitFormData.sendEmit(formData)
        return true
    })

    socket.on("downloadMediaFinish", function (response) {
        console.log("TEST_SOCKET")
        if ("error" in response) {
            console.log("Error", response["error"])
        }
        else {
            var downloadSection = document.getElementById("downloadSection")
            var fileHash = response["data"]["HASH"]
            console.log(fileHash)
            downloadSection.innerHTML = "<br><a href=/downloadFile/" + fileHash + " class='neon-button'>Download File</a>"
        }
    })


    socket.on(PlaylistMediaEmitReceiver.emitMsg, function (response) {
        // console.log("InProgress", response["data"])
        var table = document.getElementById("downloadInfo")
        var playlistMediaEmitReceiver = new PlaylistMediaEmitReceiver(response)
        console.log(playlistMediaEmitReceiver)
        if (playlistMediaEmitReceiver.isError()){
            console.log(playlistMediaEmitReceiver.getError())
            return
        }
        var playlistMedia = playlistMediaEmitReceiver.getData()
        console.log(playlistMedia.trackList)
        for (singleMedia of playlistMedia.trackList) {
            var row = table.insertRow()
            var full_row_html = `
            <td class=row-download-info>
                <label class=trak-info>
                    ${singleMedia.title}
                </label>
                <a class=neon-button target='_blank' href="${singleMedia.url}">url</a>
            </td>
            <br>
            `
            row.innerHTML = full_row_html
        }
    })

    socket.on(SingleMediaEmitReceiver.emitMsg, function (response) {
        var table = document.getElementById("downloadInfo")
        var singleMediaEmitReceiver = new SingleMediaEmitReceiver(response)
        console.log(singleMediaEmitReceiver)
        if (singleMediaEmitReceiver.isError()){
            console.log(singleMediaEmitReceiver.getError())
            return
        }
        var singleMedia = singleMediaEmitReceiver.getData()
        var row = table.insertRow()
        var full_row_html = `
        <td class=row-download-info>
            <label class=trak-info>
            ${singleMedia.artist} ${singleMedia.title}
            </label>
            <a class=neon-button target='_blank' href="${singleMedia.url}">url</a>
        </td>
        <br>
        `
        row.innerHTML = full_row_html
    })
});