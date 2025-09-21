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
