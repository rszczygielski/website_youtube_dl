# Socket.IO Namespaces

Namespaces act as the controllers for real-time WebSocket communication. They handle incoming events from the client and orchestrate the necessary backend services.

## Base Media Namespace
Provides common functionality and lifecycle management for media downloads.
::: website_youtube_dl.flask_api.sockets.namespaces.base_namespace

## YouTube Namespace
Handles isolated events specifically for downloading single tracks or videos from YouTube.
::: website_youtube_dl.flask_api.sockets.namespaces.youtube_namespace

## Playlists Namespace
Manages configuration and execution of batch playlist downloads.
::: website_youtube_dl.flask_api.sockets.namespaces.playlists_namespace