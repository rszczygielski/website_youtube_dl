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

    socket.on(UploadPlaylistsReceiver.emitMsg, function(response){
        var uploadPlaylistsReceiver = new UploadPlaylistsReceiver(response)
        if (uploadPlaylistsReceiver.isError()){
            console.log(uploadPlaylistsReceiver.getError())
            return
        }
        const playlistSelect = document.getElementById("playlistSelect");
        var uploadPlaylists = uploadPlaylistsReceiver.getData()
        console.log(uploadPlaylists.playlistsNames)

        playlistSelect.innerHTML = '';

        uploadPlaylists.playlistList.forEach(function(playlistName) {
            let option = document.createElement("option");
            option.value = playlistName;
            option.textContent = playlistName;
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
        downloadSection.innerHTML = "<br><a href=/downloadFile/" + downloadMediaFinish.hash + " class='neon-button'>Download File</a>"
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
        var playlistUrlReceiver = new PlaylistUrlReceiver(response)
        if (playlistUrlReceiver.isError()){
            console.log(playlistUrlReceiver.getError())
            return
        }
        var playlistUrlObject = playlistUrlReceiver.getData()
        const urlInput = document.getElementById("playlistURL")
        urlInput.value = playlistUrlObject.playlistUrl
    })

    addPlaylistButton.addEventListener("click", function (event) {
        const playlistName = document.getElementById("playlistName").value
        const playlistURL = document.getElementById("playlistURL").value
        console.log(playlistName, playlistURL)
        var addPlaylist = new AddPlaylist(playlistName, playlistURL)
        var emitAddPlaylist = new EmitAddPlaylist()
        emitAddPlaylist.sendEmit(addPlaylist)
    });

    playlistSelect.addEventListener("click", function(event) {
        const playlistName =  playlistSelect.value;
        const playlistNameInput = document.getElementById("playlistName");
        playlistNameInput.value = playlistName;
        var playlistNameObject = new PlaylistName(playlistName)
        var emitPlaylistName = new EmitPlaylistName()
        emitPlaylistName.sendEmit(playlistNameObject)
    });

    deletePlalistButton.addEventListener("click", function (event) {
        const playlistToDelete = playlistSelect.value
        var playlistNameObject = new PlaylistName(playlistToDelete)
        var emitDeletePlaylist = new EmitDeletePlaylist()
        emitDeletePlaylist.sendEmit(playlistNameObject)
    });

    downloadPlaylistButton.addEventListener("click", function (event) {
        const downloadInfo = document.getElementById("downloadInfo");
        const downloadSection = document.getElementById("downloadSection");
        downloadSection.innerHTML = ''
        downloadInfo.innerHTML = ''
        const playlistToDownload = playlistSelect.value

        var playlistNameObject = new PlaylistName(playlistToDownload)
        var emitDownloadFromConfigFile = new EmitDownloadFromConfigFile()
        emitDownloadFromConfigFile.sendEmit(playlistNameObject)
    });
});