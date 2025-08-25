$(document).ready(function () {
    console.log("ready")
    socket.on('connect', function () {
        console.log("Connected Youtube");
        userManager = new UserManager()
        const sessionId = userManager.getSessionId()
        console.log("Mój session_id:", sessionId);
        socket.emit("userSession", {"sessionId": sessionId})

        // After refreshing the page, send getHistory with the last hash
        const lastHash = userManager.getLastPlaylistHash();
        console.log("Last playlist hash:", lastHash);
        if (lastHash) {
            socket.emit("getHistory", {
                sessionId: sessionId,
                hash: lastHash
            });
        }
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
        formData = new FormData(youtubeURL.value, downloadType, userManager.getSessionId())
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
            <td>
                ${singleMedia.title}
            </td>
            <td>
                <a class=neon-button target='_blank' href="${singleMedia.url}">url</a>
            </td>
            `
            row.innerHTML = full_row_html
        }
    })

    socket.on(PlaylistTrackFinishReceiver.emitMsg, function (response) {
        var table = document.getElementById("downloadInfo")
        var playlistTrackFinishReceiver = new PlaylistTrackFinishReceiver(response)
        var downloadStatus = document.createElement("td")
        console.log("TEEEEEEST")
        if (playlistTrackFinishReceiver.isError()){
            console.log("Failed download")
            var trakcIndex = playlistTrackFinishReceiver.getError()
            downloadStatus.innerHTML = "<div class=sucess-mark>❌</div>";
        } else {
            var trakcIndex = playlistTrackFinishReceiver.getData().index
            downloadStatus.innerHTML = "<div class=sucess-mark>✔</div>"
        }
        var row = table.rows[trakcIndex]
        var finishCell = row.insertCell()
        finishCell.appendChild(downloadStatus)
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
        <td>
            <label class=track-info>
            ${singleMedia.artist} ${singleMedia.title}
            </label>
        </td>
        <td>
            <a class=neon-button target='_blank' href="${singleMedia.url}">url</a>
        </td>
        `
        row.innerHTML = full_row_html
    })

    socket.on(HistoryInfoEmitReceiver.emitMsg, function (response) {
        var table = document.getElementById("downloadInfo");
        // Wyczyść tabelę
        table.innerHTML = "";
        console.log("HISTORY RESPONSE:", response);
        var historyInfoEmitReceiver = new HistoryInfoEmitReceiver(response);
        if (historyInfoEmitReceiver.isError()) {
            console.log(historyInfoEmitReceiver.getError());
            return;
        }
        var historyInfo = historyInfoEmitReceiver.getData();
        for (singleMedia of historyInfo.trackList) {
            var row = table.insertRow();
            var full_row_html = `
            <td>
                ${singleMedia.title}
            </td>
            <td>
                <a class=neon-button target='_blank' href="${singleMedia.url}">url</a>
            </td>
            `;
            row.innerHTML = full_row_html;
        }
    });
});