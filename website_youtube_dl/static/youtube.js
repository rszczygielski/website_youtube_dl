$(document).ready(function () {
    console.log("ready")
    socket.on('connect', function () {
        console.log("Connected Youtube");
        userManager = new UserManager()
        const userBrowserId = userManager.getUserBrowserId()
        console.log("Mój userBrowserId:", userBrowserId);
        socket.emit("userSession", {"userBrowserId": userBrowserId})
        socket.emit("getHistory", {
                "userBrowserId": userBrowserId
            });
        });
    socket.on('disconnect', function () {
        console.log("Disconnected Youtube");
    });
    var downloadForm = document.getElementById("DownloadForm");
    downloadForm.addEventListener("submit", function (event) {
        event.preventDefault();
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

    socket.on(PlaylistMediaEmitReceiver.emitMsg, function (response) {
        var table = document.getElementById("downloadInfo")
        var playlistMediaEmitReceiver = new PlaylistMediaEmitReceiver(response)
        if (playlistMediaEmitReceiver.isError()){
            console.log(playlistMediaEmitReceiver.getError())
            return
        }
        var playlistMedia = playlistMediaEmitReceiver.getData()
        console.log(playlistMedia.trackList)
        console.log(playlistMedia.sessionHash)
        // save last playlist hash
        userManager.setLastPlaylistHash(playlistMedia.sessionHash);

        for (singleMedia of playlistMedia.trackList) {
            var row = table.insertRow()
            var full_row_html = `
            <td class="download-title-cell">${singleMedia.title}</td>
            <td class="url-cell"><a class="neon-button" target="_blank" href="${singleMedia.url}">url</a></td>
            <td class="status-cell"></td>
            `
            row.innerHTML = full_row_html
        }
    })

    socket.on(PlaylistTrackFinishReceiver.emitMsg, function (response) {
        var table = document.getElementById("downloadInfo")
        var playlistTrackFinishReceiver = new PlaylistTrackFinishReceiver(response)
        var downloadStatus = document.createElement("td")
        if (playlistTrackFinishReceiver.isError()){
            console.log("Failed download")
            trakcIndex = playlistTrackFinishReceiver.getError()
            markHtml = "<div class=sucess-mark>❌</div>";
        } else {
            trakcIndex = playlistTrackFinishReceiver.getData().index
            markHtml = "<div class=sucess-mark>✔</div>"
        }
        var row = table.rows[trakcIndex]
        var statusCell = row.querySelector('.status-cell');
        if (statusCell) {
            statusCell.innerHTML = markHtml;
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
        <td class="download-title-cell">${singleMedia.title}</td>
        <td class="url-cell">
            <a class=neon-button target='_blank' href="${singleMedia.url}">url</a>
        </td>
        `
        row.innerHTML = full_row_html
    })
});