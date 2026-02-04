$(document).ready(function () {
    console.log("ready")
    var socket_is_connected = false;
    socket.on('connect', function () {
        console.log("Connected Youtube Playlists");
        userManager = new UserManager()
        const userBrowserId = userManager.getUserBrowserId()
        console.log("Mój userBrowserId:", userBrowserId);
        socket.emit("userSession", { "userBrowserId": userBrowserId })
        if (!socket_is_connected) {
            socket.emit("getHistory", {
                "userBrowserId": userBrowserId
            })
        };
        socket_is_connected = true;
    });
    socket.on('disconnect', function () {
        console.log("Disconnected Youtube Playlists");
    });
    const downloadPlaylistButton = document.getElementById("downloadPlaylist");
    const playlistSelect = document.getElementById("playlistSelect")
    const addPlaylistButton = document.getElementById("addPlaylistButton")
    const deletePlalistButton = document.getElementById("deletePlaylistButton")

    socket.on(UploadPlaylistsReceiver.emitMsg, function(response){
        var uploadPlaylistsReceiver = new UploadPlaylistsReceiver(response)
        if (uploadPlaylistsReceiver.isError()){
            console.log(uploadPlaylistsReceiver.getError())
            return
        }
        const playlistSelect = document.getElementById("playlistSelect");
        var uploadPlaylists = uploadPlaylistsReceiver.getData()
        console.log(uploadPlaylists.playlistList)

        playlistSelect.innerHTML = '';

        uploadPlaylists.playlistList.forEach(function(playlist_name) {
            let option = document.createElement("option");
            option.value = playlist_name;
            option.textContent = playlist_name;
            playlistSelect.appendChild(option);
        });
    })

    socket.on(DownloadMediaFinishReceiver.emitMsg, function (response) {
        var downloadMediaFinishReceiver = new DownloadMediaFinishReceiver(response)
        if (downloadMediaFinishReceiver.isError()){
            console.log(downloadMediaFinishReceiver.getError())
            return
        }
        var downloadSection = document.getElementById("downloadSection")
        var downloadMediaFinish = downloadMediaFinishReceiver.getData()
        console.log(downloadMediaFinish.hash)
        // Use the `download` attribute to avoid navigating away from the page
        downloadSection.innerHTML = "<br><a href=/downloadFile/" + downloadMediaFinish.hash + " download target='_blank' class='neon-button'>Download File</a>"
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

    socket.on(PlaylistUrlReceiver.emitMsg, function(response){
        console.log(response, "responsePlaylistUrlReceiver")
        var playlistUrlReceiver = new PlaylistUrlReceiver(response)
        if (playlistUrlReceiver.isError()){
            console.log(playlistUrlReceiver.getError())
            return
        }
        var playlistUrlObject = playlistUrlReceiver.getData()
        const urlInput = document.getElementById("playlistUrl")
        urlInput.value = playlistUrlObject.playlistUrl
    })

    addPlaylistButton.addEventListener("click", function (event) {
        const playlist_name = document.getElementById("playlistName").value
        const playlistUrl = document.getElementById("playlistUrl").value
        console.log(playlist_name, playlistUrl)
        var addPlaylist = new AddPlaylist(playlist_name, playlistUrl)
        var emitAddPlaylist = new EmitAddPlaylist()
        console.log(addPlaylist.playlistName, addPlaylist.playlistUrl, "addPlaylist")
        emitAddPlaylist.sendEmit(addPlaylist)
    });

    playlistSelect.addEventListener("click", function(event) {
        const playlist_name =  playlistSelect.value;
        const playlist_nameInput = document.getElementById("playlistName");
        playlist_nameInput.value = playlist_name;
        var playlist_nameObject = new PlaylistName(playlist_name)
        var emitPlaylistName = new EmitPlaylistName()
        emitPlaylistName.sendEmit(playlist_nameObject)
    });

    deletePlalistButton.addEventListener("click", function (event) {
        const playlistToDelete = playlistSelect.value
        var playlist_nameObject = new PlaylistName(playlistToDelete)
        var emitDeletePlaylist = new EmitDeletePlaylist()
        emitDeletePlaylist.sendEmit(playlist_nameObject)
    });

    downloadPlaylistButton.addEventListener("click", function (event) {
        var downloadInfo = document.getElementById("downloadInfo");
        var downloadSection = document.getElementById("downloadSection");
        downloadSection.innerHTML = ''
        downloadInfo.innerHTML = ''
        var playlistToDownload = playlistSelect.value
        console.log(playlistToDownload)
        var playlist_nameObject = new PlaylistName(playlistToDownload)
        var emitDownloadFromConfigFile = new EmitDownloadFromConfigFile()
        emitDownloadFromConfigFile.sendEmit(playlist_nameObject)
    });
});