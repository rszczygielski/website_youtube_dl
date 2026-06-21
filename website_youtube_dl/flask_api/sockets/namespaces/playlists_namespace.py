from flask import Blueprint, render_template, request
from flask import current_app as app
from website_youtube_dl.common.youtube_api import FormatMP3
from .base_namespace import MediaBaseNamespace
from ..emits import (
    UploadPlaylistToConfigEmit,
    GetPlaylistUrlEmit
)


# --- SocketIO Namespace Class ---
class PlaylistsNamespace(MediaBaseNamespace):
    """Socket.IO Namespace handler for /playlists.

    This class manages real-time communication for playlist configuration,
    including adding, deleting, and downloading tracks from pre-configured
    YouTube playlists.
    """

    def on_downloadFromConfigFile(self, formData: dict) -> None:
        """Handle download requests for a playlist stored in the config file.

        Args:
            formData (dict): Contains 'playlistToDownload' key with the playlist name.
        """
        playlist_name = formData["playlistToDownload"]
        app.logger.info(f"Selected playlist from config: {playlist_name}")

        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)
        if not user_browser_id:
            return

        playlist_url = app.config_parser_manager.get_playlist_url(playlist_name)

        self._handle_playlist_download(
            youtube_url=playlist_url,
            request_format=FormatMP3(),
            user_browser_id=user_browser_id
        )

    def on_addPlaylist(self, formData: dict) -> None:
        """Add a new playlist entry to the application configuration.

        Args:
            formData (dict): Contains 'playlistName' and 'playlistURL'.
        """
        playlist_name = formData["playlistName"]
        playlist_url = formData["playlistURL"]
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)

        if not user_browser_id:
            return

        socket_ctx = app.socket_manager.get_context(user_browser_id, self.namespace)
        result = app.config_parser_manager.add_playlist(playlist_name, playlist_url)

        if result:
            app.logger.info(f"Added playlist {playlist_name} to config")
            playlist_list = list(app.config_parser_manager.get_playlists().keys())
            socket_ctx.emit(
                data=playlist_list,
                emit_type=UploadPlaylistToConfigEmit
            )
        else:
            app.logger.warning(f"Failed to add playlist {playlist_name} to config")
            socket_ctx.emit_error(
                error_msg=f"Failed to add playlist {playlist_name} to config",
                emit_type=UploadPlaylistToConfigEmit,
                add_to_queue=False
            )

    def on_deletePlaylist(self, formData: dict) -> None:
        """Remove a playlist entry from the application configuration.

        Args:
            formData (dict): Contains 'playlistToDelete' key with the name.
        """
        playlist_name = formData["playlistToDelete"]
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)

        if not user_browser_id:
            return

        socket_ctx = app.socket_manager.get_context(user_browser_id, self.namespace)
        result = app.config_parser_manager.delete_playlist(playlist_name)

        if result:
            app.logger.info(f"Deleted playlist {playlist_name} from config")
            playlist_list = list(app.config_parser_manager.get_playlists().keys())
            socket_ctx.emit(
                data=playlist_list,
                emit_type=UploadPlaylistToConfigEmit,
                add_to_queue=False
            )
        else:
            app.logger.warning(f"Failed to delete playlist {playlist_name}")
            socket_ctx.emit_error(
                error_msg=f"Failed to delete playlist {playlist_name}",
                emit_type=UploadPlaylistToConfigEmit
            )

    def on_playlistName(self, formData: dict) -> None:
        """Retrieve the URL of a specific playlist by its name.

        Args:
            formData (dict): Contains 'playlistName'.
        """
        playlist_name = formData["playlistName"]
        playlist_url = app.config_parser_manager.get_playlist_url(playlist_name)
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)

        if not user_browser_id:
            return

        socket_ctx = app.socket_manager.get_context(user_browser_id, self.namespace)

        socket_ctx.emit(
            data=playlist_url,
            emit_type=GetPlaylistUrlEmit,
            add_to_queue=False
        )