$(document).ready(function () {
    console.log("ready youtube.js");

    // Initialize the base client with namespace and the specific button ID
    const mediaClient = new BaseMediaClient("/youtube");
    var downloadForm = document.getElementById("DownloadForm");
    var youtubeURL = document.getElementById("youtubeURL");

    downloadForm.addEventListener("submit", function (event) {
        event.preventDefault();

        mediaClient.clearUI();
        mediaClient.setSpinnerVisibility(true);
        mediaClient.setMainButtonEnabled(false);

        var downloadTypes = document.getElementsByName("qualType");
        var downloadType;
        for (var i = 0; i < downloadTypes.length; i++) {
            if (downloadTypes[i].checked == true) {
                downloadType = downloadTypes[i].value;
                break;
            }
        }

        var formData = new FormData(youtubeURL.value, downloadType);
        var emitFormData = new EmitFormData(mediaClient.socket);
        emitFormData.sendEmit(formData);

        return true;
    });

    // Specific listener only for YouTube namespace
    mediaClient.socket.on(SingleMediaEmitReceiver.emitMsg, function (response) {
        var receiver = new SingleMediaEmitReceiver(response);
        if (receiver.isError()) {
            console.log(receiver.getError());
            return;
        }

        var singleMedia = receiver.getData();
        var row = mediaClient.table.insertRow();
        row.innerHTML = `
        <td class="download-title-cell">${singleMedia.title}</td>
        <td class="url-cell">
            <a class="neon-button" target="_blank" href="${singleMedia.url}">url</a>
        </td>
        `;
    });
});