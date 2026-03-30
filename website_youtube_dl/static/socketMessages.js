// ==========================================
// DATA MODELS
// Classes representing data structures sent via WebSockets
// ==========================================

/** * Represents a single media track downloaded from YouTube.
 */
class SingleMedia {
    constructor(title, artist, url) {
        this.title = title;
        this.artist = artist;
        this.url = url;
    }
}

/** * Represents a single media track that is part of a playlist.
 */
class SingleMediaFromPlaylist {
    constructor(title, url) {
        this.title = title;
        this.url = url;
    }
}

/** * Represents an entire playlist containing a collection of tracks.
 */
class PlaylistMedia {
    constructor(playlistName, trackList) {
        this.playlistName = playlistName;
        this.trackList = trackList;
    }
}

/** * Contains the generated hash for the finalized, zipped download file.
 */
class DownloadMediaFinish {
    constructor(hash) {
        this.hash = hash;
    }
}

/** * Contains the form data required to initiate a download.
 */
class FormData {
    constructor(youtubeURL, downloadType, sessionId) {
        this.youtubeURL = youtubeURL;
        this.downloadType = downloadType;
        this.sessionId = sessionId;
    }
}

/** * Contains the data needed to add a new playlist to the configuration.
 */
class AddPlaylist {
    constructor(playlistName, playlistUrl) {
        this.playlistName = playlistName;
        this.playlistUrl = playlistUrl;
    }
}

/** * Wraps the name of a specific playlist.
 */
class PlaylistName {
    constructor(playlistName) {
        this.playlistName = playlistName;
    }
}

/** * Contains a list of all available playlists from the configuration.
 */
class UploadPlaylists {
    constructor(playlistList) {
        this.playlistList = playlistList;
    }
}

/** * Wraps the URL associated with a specific playlist.
 */
class PlaylistUrl {
    constructor(playlistUrl) {
        this.playlistUrl = playlistUrl;
    }
}

/** * Represents the index of a track in the UI table (e.g., to mark it as downloaded).
 */
class PlaylistIndex {
    constructor(index) {
        this.index = index;
    }
}

/** * Contains the data required to request cancellation of an ongoing download.
 */
class CancelDownload {
    constructor(userBrowserId) {
        this.userBrowserId = userBrowserId;
    }
}

// ==========================================
// RECEIVERS
// Classes for receiving and processing events from the server (Socket.IO)
// ==========================================

/** * Base class for handling incoming WebSocket messages.
 */
class BaseReceiver {
    constructor(requestJson) {
        this.requestJson = requestJson;
    }

    /** * Checks if the received message contains an error.
     * @returns {boolean} True if an error is present, false otherwise.
     */
    isError() {
        return "error" in this.requestJson;
    }

    /** * Retrieves the error message from the payload.
     * @returns {string|undefined} The error message.
     */
    getError() {
        if ("error" in this.requestJson) {
            return this.requestJson["error"];
        }
    }

    /** * Virtual method to convert raw message data into structured objects.
     * Must be overridden by subclasses.
     * @param {Object} data - The raw data from the server.
     */
    convertMessageToData(data) {}

    /** * Returns the processed data from the message payload.
     * @returns {Object|undefined} The converted data object.
     */
    getData() {
        if ("data" in this.requestJson) {
            return this.convertMessageToData(this.requestJson["data"]);
        }
    }
}

class PlaylistMediaEmitReceiver extends BaseReceiver {
    static emitMsg = "playlistMediaInfo";

    constructor(requestJson) {
        super(requestJson);
    }

    convertMessageToData(data) {
        var playlistName = data["playlistName"];
        var trackList = data["trackList"];

        var singleMediaArr = [];
        for (var track of trackList) {
            console.log(track);
            singleMediaArr.push(new SingleMediaFromPlaylist(track["title"], track["url"]));
        }
        return new PlaylistMedia(playlistName, singleMediaArr);
    }
}

class SingleMediaEmitReceiver extends BaseReceiver {
    static emitMsg = "mediaInfo";

    constructor(requestJson) {
        super(requestJson);
    }

    convertMessageToData(data) {
        return new SingleMedia(data["title"], data["artist"], data["webpage_url"]);
    }
}

class DownloadMediaFinishReceiver extends BaseReceiver {
    static emitMsg = "downloadMediaFinish";

    constructor(requestJson) {
        super(requestJson);
    }

    convertMessageToData(data) {
        return new DownloadMediaFinish(data["HASH"]);
    }
}

class UploadPlaylistsReceiver extends BaseReceiver {
    static emitMsg = "uploadPlaylists";

    constructor(requestJson) {
        super(requestJson);
    }

    convertMessageToData(data) {
        return new UploadPlaylists(data["playlistList"]);
    }
}

class PlaylistUrlReceiver extends BaseReceiver {
    static emitMsg = "playlistUrl";

    constructor(requestJson) {
        super(requestJson);
    }

    convertMessageToData(data) {
        return new PlaylistUrl(data["playlistUrl"]);
    }
}

class PlaylistTrackFinishReceiver extends BaseReceiver {
    static emitMsg = "playlistTrackFinish";

    constructor(requestJson) {
        super(requestJson);
    }

    convertMessageToData(data) {
        return new PlaylistIndex(data["index"]);
    }
}

// ==========================================
// EMITTERS
// Classes for formatting and sending events to the server (Socket.IO)
// ==========================================

/** * Base class for emitting messages via Socket.IO.
 */
class BaseEmit {
    constructor(emitMsg, socket) {
        this.emitMsg = emitMsg;
        this.socket = socket;
    }

    /** * Virtual method to prepare the payload.
     * Must be overridden by subclasses.
     * @param {Object} data - The data to be converted.
     */
    convert_data_to_message(data) {}

    /** * Formats the data and emits the event to the server.
     * @param {Object} data - The data object to send.
     */
    sendEmit(data) {
        var convertedData = this.convert_data_to_message(data);
        this.socket.emit(this.emitMsg, convertedData);
    }
}

class EmitFormData extends BaseEmit {
    constructor(socket) {
        super("FormData", socket);
    }

    /** * @param {FormData} formData
     */
    convert_data_to_message(formData) {
        return {
            "youtubeURL": formData.youtubeURL,
            "downloadType": formData.downloadType,
            "sessionId": formData.sessionId
        };
    }
}

class EmitAddPlaylist extends BaseEmit {
    constructor(socket) {
        super("addPlaylist", socket);
    }

    /** * @param {AddPlaylist} addPlaylist
     */
    convert_data_to_message(addPlaylist) {
        return {
            "playlistName": addPlaylist.playlistName,
            "playlistURL": addPlaylist.playlistUrl
        };
    }
}

class EmitDeletePlaylist extends BaseEmit {
    constructor(socket) {
        super("deletePlaylist", socket);
    }

    /** * @param {PlaylistName} playlistName
     */
    convert_data_to_message(playlistName) {
        return {
            "playlistToDelete": playlistName.playlistName
        };
    }
}

class EmitPlaylistName extends BaseEmit {
    constructor(socket) {
        super("playlistName", socket);
    }

    /** * @param {PlaylistName} playlistName
     */
    convert_data_to_message(playlistName) {
        return {
            "playlistName": playlistName.playlistName
        };
    }
}

class EmitDownloadFromConfigFile extends BaseEmit {
    constructor(socket) {
        super("downloadFromConfigFile", socket);
    }

    /** * @param {PlaylistName} playlistName
     */
    convert_data_to_message(playlistName) {
        return {
            "playlistToDownload": playlistName.playlistName
        };
    }
}

class EmitCancelDownload extends BaseEmit {
    constructor(socket) {
        super("cancelDownload", socket);
    }

    /** * @param {CancelDownload} cancelData
     */
    convert_data_to_message(cancelData) {
        return {
            "userBrowserId": cancelData.userBrowserId
        };
    }
}