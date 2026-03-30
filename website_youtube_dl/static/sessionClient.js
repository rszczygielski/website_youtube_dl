/**
 * Base class handling shared UI and Socket.IO logic for media downloads.
 */
class BaseMediaClient {
    constructor(namespace) {
        this.socket = io(namespace);
        this.userManager = new UserManager();
        this.socket_is_connected = false;

        // DOM Elements
        this.mainButton = document.getElementById("DownloadButton");
        this.cancelButton = document.getElementById("cancelDownloadButton");
        this.loadingSpinner = document.getElementById("loadingSpinner");
        this.downloadLinkContainer = document.getElementById("downloadLinkContainer");
        this.table = document.getElementById("downloadInfo");

        this._initConnection();
        this._initCancelButton();
        this._initCommonSocketListeners();
    }

    _initConnection() {
        this.socket.on('connect', () => {
            const userBrowserId = this.userManager.getUserBrowserId();
            this.socket.emit("userSession", { "userBrowserId": userBrowserId });

            if (!this.socket_is_connected) {
                this.socket.emit("getHistory", { "userBrowserId": userBrowserId }, (response) => {
                    if (response && response.hasHistory) {
                        console.log("History found, showing spinner...");
                        this.setSpinnerVisibility(true);
                        this.setMainButtonEnabled(false);
                    } else {
                        console.log("No history to replay.");
                    }
                });
            }
            this.socket_is_connected = true;
        });
    }

    _initCancelButton() {
        if (this.cancelButton) {
            this.cancelButton.addEventListener("click", () => {
                console.log("Cancelling download...");

                var cancelData = new CancelDownload(this.userManager.getUserBrowserId());
                var emitCancel = new EmitCancelDownload(this.socket);
                emitCancel.sendEmit(cancelData);

                this.setSpinnerVisibility(false);
                this.setMainButtonEnabled(true);

                if (this.downloadLinkContainer) {
                    this.downloadLinkContainer.innerHTML = "<br><span style='color: red;' class='neon-text'>Download cancelled by user.</span>";
                }
            });
        }
    }

    _initCommonSocketListeners() {
        // Download finish
        this.socket.on(DownloadMediaFinishReceiver.emitMsg, (response) => {
            var receiver = new DownloadMediaFinishReceiver(response);
            this.setSpinnerVisibility(false);
            this.setMainButtonEnabled(true);

            if (receiver.isError()) {
                console.log(receiver.getError());
                return;
            }

            var data = receiver.getData();
            if (this.downloadLinkContainer) {
                this.downloadLinkContainer.innerHTML = `<br><a href=/downloadFile/${data.hash} download target='_blank' class='neon-button'>Download File</a>`;
            }
        });

        // Playlist media info
        this.socket.on(PlaylistMediaEmitReceiver.emitMsg, (response) => {
            var receiver = new PlaylistMediaEmitReceiver(response);
            if (receiver.isError()) {
                console.log(receiver.getError());
                return;
            }

            var playlistMedia = receiver.getData();
            this.userManager.setLastPlaylistHash(playlistMedia.sessionHash);

            for (let singleMedia of playlistMedia.trackList) {
                var row = this.table.insertRow();
                row.innerHTML = `
                <td class="download-title-cell">${singleMedia.title}</td>
                <td class="url-cell"><a class="neon-button" target="_blank" href="${singleMedia.url}">url</a></td>
                <td class="status-cell"></td>
                `;
            }
        });

        // Playlist track finish
        this.socket.on(PlaylistTrackFinishReceiver.emitMsg, (response) => {
            var receiver = new PlaylistTrackFinishReceiver(response);
            var markHtml, trackIndex;

            if (receiver.isError()) {
                console.log("Failed download");
                trackIndex = receiver.getError();
                markHtml = "<div class=sucess-mark>❌</div>";
            } else {
                trackIndex = receiver.getData().index;
                markHtml = "<div class=sucess-mark>✔</div>";
            }

            var row = this.table.rows[trackIndex];
            var statusCell = row.querySelector('.status-cell');
            if (statusCell) {
                statusCell.innerHTML = markHtml;
            }
        });
    }

    setSpinnerVisibility(isVisible) {
        if (!this.loadingSpinner) return;
        if (isVisible) {
            this.loadingSpinner.classList.remove("d-none");
        } else {
            this.loadingSpinner.classList.add("d-none");
        }
    }

    setMainButtonEnabled(isEnabled) {
        if (!this.mainButton) return;
        this.mainButton.disabled = !isEnabled;
        if (isEnabled) {
            this.mainButton.classList.remove("disabled");
        } else {
            this.mainButton.classList.add("disabled");
        }
    }

    clearUI() {
        if (this.table) this.table.innerHTML = "";
        if (this.downloadLinkContainer) this.downloadLinkContainer.innerHTML = "";
    }
}

class UserManager {
    constructor() {
        this.STORAGE_KEY = "session_id";
        this.HASH_KEY = "last_playlist_hash";
        this.userBrowserId = this.loadOrCreateSession();
    }

    generateUserBrowserId() {
        return (
            Math.random().toString(36).substring(2, 15) +
            Math.random().toString(36).substring(2, 15)
        );
    }

    loadOrCreateSession() {
        let existingId = localStorage.getItem(this.STORAGE_KEY);
        if (existingId) {
            return existingId;
        } else {
            const newId = this.generateUserBrowserId();
            localStorage.setItem(this.STORAGE_KEY, newId);
            return newId;
        }
    }

    getUserBrowserId() {
        return this.userBrowserId;
    }

    setLastPlaylistHash(hash) {
        localStorage.setItem(this.HASH_KEY, hash);
    }

    getLastPlaylistHash() {
        return localStorage.getItem(this.HASH_KEY);
    }

    clearLastPlaylistHash() {
        localStorage.removeItem(this.HASH_KEY);
    }

    clearSession() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.userBrowserId = this.loadOrCreateSession();
    }
}
