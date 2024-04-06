class SingleMedia {
    constructor(title, artist, url) {
        this.title = title;
        this.artist = artist;
        this.url = url;
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

class PlaylistMessageConverter {

    convertMessageToData(requestJson) {
        var trackList = requestJson["data"]
        var playlistName = trackList[0]["playlist_name"]
        var singleMediaArr = []
        for (var i = 0; i < trackList.length; i++) {
            track = trackList[i]
            singleMediaArr.push(SingleMedia(track.title,
                                            track.artist,
                                            track.url))
        return PlaylistMedia(playlistName, singleMediaArr)
       }
    }
}
// class MessageManager{

// }

$(document).ready(function () {
    var socket = io();
    console.log("ready")
    socket.on('connect', function () {
        console.log("Connected Youtube");
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
        socket.emit("FormData", {
            "youtubeURL": youtubeURL.value,
            "downloadType": downloadType
        });
        return true
    })

    socket.on("downloadMediaFinish", function (response) {
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

    

    socket.on("playlistMediaInfo", function (response) {
        console.log("InProgress", response["data"])
        var table = document.getElementById("downloadInfo")
        for (var i = 0; i < response["data"].length; i++) {
            var row = table.insertRow()
            var cell = row.insertCell()
            var cell2 = row.insertCell()
            var cell3 = row.insertCell()
            cell.innerHTML = response["data"][i]["artist"]
            cell2.innerHTML = response["data"][i]["title"]
            console.log(response["data"][i]["artist"])
            console.log(response["data"][i]["title"])
            cell3.innerHTML = "<a class=neon-button target='_blank' href=" + response["data"][i]["original_url"] + ">" + "url</a>"
        }
    })
});