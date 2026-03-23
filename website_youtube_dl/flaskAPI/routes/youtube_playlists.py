from flask import Blueprint, render_template, request
from flask import current_app as app

from ..sockets.base_namespace import BaseMediaNamespace
from ..sockets.emits import (
    UploadPlaylistToConfigEmit,
    GetPlaylistUrlEmit
)
from ...common.youtubeAPI import FormatMP3

# --- Blueprints for standard HTTP routes ---
youtube_playlist = Blueprint("youtube_playlist", __name__)

@youtube_playlist.route("/modify_playlist.html")
def modify_playlist_html():
    """Render the playlist management interface.

    Retrieves existing playlists from the configuration and passes their names
    to the template for rendering.

    Returns:
        str: Rendered HTML template for playlist modification.
    """
    playlist_list = app.config_parser_manager.get_playlists()
    playlists_names = list(playlist_list.keys())
    app.logger.debug(f"Rendering modify_playlist.html with {len(playlists_names)} playlists")
    return render_template(
        "modify_playlist.html",
        playlists_names=playlists_names
    )

# --- SocketIO Namespace Class ---
class PlaylistsNamespace(BaseMediaNamespace):
    """Socket.IO Namespace handler for /playlists.

    This class manages real-time communication for playlist configuration,
    including adding, deleting, and downloading tracks from pre-configured
    YouTube playlists.
    """

    def on_downloadFromConfigFile(self, formData):
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

    def on_addPlaylist(self, formData):
        """Add a new playlist entry to the application configuration.

        Args:
            formData (dict): Contains 'playlistName' and 'playlistURL'.
        """
        playlist_name = formData["playlistName"]
        playlist_url = formData["playlistURL"]
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)

        result = app.config_parser_manager.add_playlist(playlist_name, playlist_url)

        if result:
            app.logger.info(f"Added playlist {playlist_name} to config")
            playlist_list = list(app.config_parser_manager.get_playlists().keys())
            app.socket_manager.process_emit(
                data=playlist_list,
                emit_type=UploadPlaylistToConfigEmit,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )
        else:
            app.logger.warning(f"Failed to add playlist {playlist_name} to config")
            app.socket_manager.process_emit_error(
                error_msg=f"Failed to add playlist {playlist_name} to config",
                emit_type=UploadPlaylistToConfigEmit,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )

    def on_deletePlaylist(self, formData):
        """Remove a playlist entry from the application configuration.

        Args:
            formData (dict): Contains 'playlistToDelete' key with the name.
        """
        playlist_name = formData["playlistToDelete"]
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)

        result = app.config_parser_manager.delete_playlist(playlist_name)

        if result:
            app.logger.info(f"Deleted playlist {playlist_name} from config")
            playlist_list = list(app.config_parser_manager.get_playlists().keys())
            app.socket_manager.process_emit(
                data=playlist_list,
                emit_type=UploadPlaylistToConfigEmit,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )
        else:
            app.logger.warning(f"Failed to delete playlist {playlist_name}")
            app.socket_manager.process_emit_error(
                error_msg=f"Failed to delete playlist {playlist_name}",
                emit_type=UploadPlaylistToConfigEmit,
                user_browser_id=user_browser_id,
                namespace=self.namespace
            )

    def on_playlistName(self, formData):
        """Retrieve the URL of a specific playlist by its name.

        Args:
            formData (dict): Contains 'playlistName'.
        """
        playlist_name = formData["playlistName"]
        playlist_url = app.config_parser_manager.get_playlist_url(playlist_name)
        user_browser_id = app.socket_manager.get_user_browser_id_by_session(request.sid)

        app.socket_manager.process_emit(
            data=playlist_url,
            emit_type=GetPlaylistUrlEmit,
            user_browser_id=user_browser_id,
            namespace=self.namespace
        )