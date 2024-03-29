$(document).ready(function () {
    const socket = io();
    console.log("ready")
    socket.on('connect', function () {
        console.log("Connected Playlists");
    });
    const downloadPlaylistButton = document.getElementById("downloadPlaylist");
    const playlistSelect = document.getElementById("playlistSelect")
    const addPlaylistButton = document.getElementById("addPlaylistButton")
    const deletePlalistButton = document.getElementById("deletePlaylistButton")

    socket.on("uploadPlalists", function(response){
        const playlistSelect = document.getElementById("playlistSelect");
        const playlistsNames = response["data"]["plalistList"]
        console.log(playlistsNames)

        playlistSelect.innerHTML = '';

        playlistsNames.forEach(function(playlistName) {
            let option = document.createElement("option");
            option.value = playlistName;
            option.textContent = playlistName;
            playlistSelect.appendChild(option);
        });
    })

    socket.on("downloadMediaFinish", function (response) {
        if ("error" in response) {
            console.log("Error", response["error"])
        }
        else {
            const downloadSection = document.getElementById("downloadSection")
            const fileHash = response["data"]["HASH"]
            console.log(fileHash)
            downloadSection.innerHTML = "<br><a href=/downloadFile/" + fileHash + " class='neon-button'>Download File</a>"
        }
    })

    socket.on("mediaInfo", function (response) {
        console.log("InProgress", response["data"])
        for (var i = 0; i < response["data"].length; i++) {
            var table = document.getElementById("downloadInfo")
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

    addPlaylistButton.addEventListener("click", function (event) {
        const playlistName = document.getElementById("playlistName").value
        const playlistURL = document.getElementById("playlistURL").value
        console.log(playlistName, playlistURL)
        socket.emit("addPlaylist", {
            "playlistName": playlistName,
            "playlistURL": playlistURL
        })
    });

    deletePlalistButton.addEventListener("click", function (event) {
        const playlistToDelete = playlistSelect.value
        socket.emit("deletePlaylist", { "playlistToDelete": playlistToDelete })
    });

    downloadPlaylistButton.addEventListener("click", function (event) {
        const downloadInfo = document.getElementById("downloadInfo");
        const downloadSection = document.getElementById("downloadSection");
        downloadSection.innerHTML = ''
        downloadInfo.innerHTML = ''
        const playlistToDownload = playlistSelect.value
        socket.emit("downloadFromConfigFile", {"playlistToDownload": playlistToDownload })
    });
});