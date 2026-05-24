# Welcome to Website Youtube DL Wiki

Welcome to the official documentation for **Website Youtube DL**. This project is a robust, Flask-based web application designed to download media from YouTube. It leverages `yt-dlp` for core downloading mechanics and `Flask-SocketIO` for seamless, real-time communication with the client browser.

---

## 🚀 Key Features

* **Single Media & Playlists:** Download individual videos, extracted audio tracks, or batch-process entire playlists with ease.
* **Automatic ID3 Tagging:** Audio downloads are automatically converted to MP3 and tagged with appropriate metadata (Title, Artist, Album, Playlist Name, and Track Number) using `mutagen`.
* **Real-Time UI Updates:** The frontend communicates asynchronously with the backend via WebSockets, providing live progress feedback, media information, and download links without requiring page reloads.
* **Configuration Management:** Store custom save directories and frequently used YouTube playlist URLs locally in a configuration file.
* **ZIP Archiving:** Automatically bundle and compress entire downloaded playlists into `.zip` archives for easy access.

---

## 🏗️ Architecture Overview

The application is built with a strong emphasis on **Separation of Concerns**, dividing the system into distinct layers:

1.  **Common Domain (`common/`):** The engine room of the application. It contains framework-agnostic business logic, including `yt-dlp` wrappers, data models, enum keys, ID3 tagging operations, and config parsing.
2.  **API & Delivery (`flask_api/`):** The web layer connecting the backend to the user. It houses HTTP routes, Socket.IO namespaces (controllers), and the bridge services orchestrating the download flow.
3.  **Presentation (`static/` & `templates/`):** A modern, dark-themed UI built with HTML, CSS (Bootstrap), and object-oriented JavaScript.

---

## 📚 Documentation Map

Navigate through the code references to understand the internal mechanics of the project:

### Architecture & Services
* [YouTube Core Engine](code/youtube_dl.md) - The core wrapper around `yt-dlp`.
* [Downloader Service](code/downloader_service.md) - The service orchestrating single tracks, playlists, and zipping.
* [Configuration Manager](code/config.md) - Management of paths and saved playlists.

### WebSocket API
* [Namespaces (Controllers)](code/namespaces.md) - Event listeners for frontend communication.
* [Socket Manager](code/sockets.md) - Session tracking, message queuing, and connection management.
* [Media Information Handler](code/media_info.md) - Real-time emission of media metadata to the client.