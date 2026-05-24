# 🎬 Flask YouTube Downloader Web UI

[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue.svg)](https://rszczygielski.github.io/website_youtube_dl/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-latest-lightgrey)](https://flask.palletsprojects.com/)

A modern, robust, and real-time web application for downloading YouTube media. Built with **Flask** and **Flask-SocketIO**, this application allows users to easily download single tracks or entire playlists, offering real-time progress tracking, automatic ID3 tagging, and ZIP archiving.

---

## 📖 Documentation

Full documentation, including API references, architecture details, and developer guides, is automatically built and hosted via GitHub Pages:

👉 **[Read the Official Documentation Here](https://rszczygielski.github.io/website_youtube_dl/)**

---

## ✨ Key Features

* **Single & Playlist Downloads:** Download individual YouTube videos, audio tracks, or entire playlists with a single click.
* **Real-Time UI Updates:** Powered by WebSockets (Socket.IO), the UI provides live progress tracking without the need to refresh the page.
* **Resilient State Machine:** Safe against browser refreshes and disconnects. The server maintains the true downloading state, ensuring the UI always reflects the actual backend process.
* **Automatic Metadata Tagging:** Audio downloads (MP3) are automatically enriched with ID3 tags (Title, Artist, Album).
* **Batch Zipping:** Playlists are automatically compressed into `.zip` archives upon completion for easy downloading.
* **Configurable Playlists:** Manage a predefined list of favorite playlists via a UI configuration manager.
* **Clean Architecture:** Built strictly adhering to OOP principles (Single Responsibility, Base Classes, Separation of Concerns).

---

## 🏗️ Architecture & Tech Stack

### Backend
* **Python 3**
* **Flask:** Core web framework.
* **Flask-SocketIO:** For bidirectional, real-time communication.
* **yt-dlp / youtube-dl:** Core engine for media extraction.
* **Mutagen (EasyID3):** For post-processing audio metadata.

### Frontend
* **JavaScript / jQuery:** Handling DOM manipulation and WebSocket listeners.
* **Socket.IO Client:** Syncing UI state with the backend.
* **Bootstrap 5:** Responsive and modern UI components.

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.8+ installed along with `ffmpeg` (required for media conversion and extraction).

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/rszczygielski/website_youtube_dl.git](https://github.com/rszczygielski/website_youtube_dl.git)
   cd website_youtube_dl