$(document).ready(function () {
    var socket = io();
    var configPlaylist = document.getElementById("downloadConfigPlaylist");
    configPlaylist.addEventListener("submit", function (event){
        event.preventDefault();
        console.log("TEST TEST TEST")
        socket.emit("downloadFromConfigFile", "")
    })
});