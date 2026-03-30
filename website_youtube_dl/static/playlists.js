$(document).ready(function () {
    console.log("ready playlists.js");

    // Initialize the base client
    const mediaClient = new BaseMediaClient("/playlists");

    var playlistSelect = document.getElementById("playlistSelect");
    var addPlaylistButton = document.getElementById("addPlaylistButton");
    var deletePlaylistButton = document.getElementById("deletePlaylistButton");
    var playlistNameInput = document.getElementById("playlistName");
    var playlistUrlInput = document.getElementById("playlistUrl");

    // Specific listeners for Playlists namespace
    mediaClient.socket.on(UploadPlaylistsReceiver.emitMsg, function(response){
        var receiver = new UploadPlaylistsReceiver(response);
        if (receiver.isError()){
            console.log(receiver.getError());
            return;
        }
        var uploadPlaylists = receiver.getData();
        playlistSelect.innerHTML = '';

        uploadPlaylists.playlistList.forEach(function(playlist_name) {
            let option = document.createElement("option");
            option.value = playlist_name;
            option.textContent = playlist_name;
            playlistSelect.appendChild(option);
        });
    });

    mediaClient.socket.on(PlaylistUrlReceiver.emitMsg, function(response){
        var receiver = new PlaylistUrlReceiver(response);
        if (receiver.isError()){
            console.log(receiver.getError());
            return;
        }
        var playlistUrlObject = receiver.getData();
        playlistUrlInput.value = playlistUrlObject.playlistUrl;
    });

    // UI Event Listeners
    addPlaylistButton.addEventListener("click", function () {
        const playlistName = playlistNameInput.value;
        const playlistUrl = playlistUrlInput.value;

        var addPlaylist = new AddPlaylist(playlistName, playlistUrl);
        var emitAddPlaylist = new EmitAddPlaylist(mediaClient.socket);
        emitAddPlaylist.sendEmit(addPlaylist);
    });

    playlistSelect.addEventListener("click", function() {
        const playlistName = playlistSelect.value;
        playlistNameInput.value = playlistName;

        var playlistNameObj = new PlaylistName(playlistName);
        var emitPlaylistName = new EmitPlaylistName(mediaClient.socket);
        emitPlaylistName.sendEmit(playlistNameObj);
    });

    deletePlaylistButton.addEventListener("click", function () {
        const playlistToDelete = playlistSelect.value;
        var playlistNameObj = new PlaylistName(playlistToDelete);
        var emitDeletePlaylist = new EmitDeletePlaylist(mediaClient.socket);
        emitDeletePlaylist.sendEmit(playlistNameObj);
    });

    mediaClient.mainButton.addEventListener("click", function () {
        mediaClient.clearUI();
        mediaClient.setSpinnerVisibility(true);
        mediaClient.setMainButtonEnabled(false);

        var playlistToDownload = playlistSelect.value;
        var playlistNameObj = new PlaylistName(playlistToDownload);
        var emitDownloadFromConfig = new EmitDownloadFromConfigFile(mediaClient.socket);
        emitDownloadFromConfig.sendEmit(playlistNameObj);
    });
});