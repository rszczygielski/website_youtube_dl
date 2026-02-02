import os
from dataclasses import dataclass
from typing import Any, Type, Optional


@dataclass
class UserMessage:
    """Represents a message in user's session queue.
    
    This dataclass stores a message that will be sent to the user via Socket.IO.
    It can be unpacked like a tuple for backward compatibility.
    
    Attributes:
        emit_type (Type): The emit type class (e.g., DownloadMediaFinishEmit).
        data (Any): The data to be sent with the emit.
        is_error (bool): Whether this message represents an error. Defaults to False.
    """
    emit_type: Type
    data: Any
    is_error: bool = False

    def __iter__(self):
        """Allow unpacking like tuple for backward compatibility.
        
        Returns:
            Iterator: Iterator over (emit_type, data, is_error) tuple.
            
        Example:
            >>> message = UserMessage(emit_type=SomeEmit, data="test", is_error=False)
            >>> emit_type, data, is_error = message  # Unpacking works
        """
        return iter((self.emit_type, self.data, self.is_error))


@dataclass
class BrowserSession:
    """Represents a browser session with Socket.IO session ID and timestamp.
    
    This dataclass stores information about an active browser session, including
    the Socket.IO session ID and the last activity timestamp for timeout management.
    It can be unpacked like a tuple for backward compatibility.
    
    Attributes:
        session_id (str): The Socket.IO session ID.
        last_activity_timestamp (float): Unix timestamp of last activity.
    """
    session_id: str
    last_activity_timestamp: float

    def __iter__(self):
        """Allow unpacking like tuple for backward compatibility.
        
        Returns:
            Iterator: Iterator over (session_id, last_activity_timestamp) tuple.
            
        Example:
            >>> session = BrowserSession(session_id="abc123", last_activity_timestamp=1234567890.0)
            >>> session_id, timestamp = session  # Unpacking works
        """
        return iter((self.session_id, self.last_activity_timestamp))


class DownloadFileInfo():
    """Stores information about a downloaded file for session management.
    
    This class holds file metadata needed to serve the file to the user
    via the download endpoint. It validates that the file exists during initialization.
    
    Attributes:
        file_name (str): The name of the file.
        file_directory_path (str): The directory path where the file is stored.
        is_playlist (bool): Whether this file represents a playlist download.
    """
    file_name = None
    file_directory_path = None
    is_playlist = None

    def __init__(self, fullFilePath: str, is_playlist: bool) -> None:
        """Initialize DownloadFileInfo with file path and playlist flag.
        
        Args:
            fullFilePath (str): Full path to the downloaded file.
            is_playlist (bool): Whether this file represents a playlist download.
            
        Raises:
            FileNotFoundError: If the file at fullFilePath does not exist.
        """
        self.set_file_download_data(fullFilePath)
        self.is_playlist = is_playlist

    def set_file_download_data(self, fullFilePath):
        """Extract file name and directory path from full file path.
        
        Args:
            fullFilePath (str): Full path to the file.
            
        Raises:
            FileNotFoundError: If the file at fullFilePath does not exist.
        """
        if not os.path.isfile(fullFilePath):
            raise FileNotFoundError(
                f"File {fullFilePath} doesn't exist - something went wrong")
        splited_file_path = fullFilePath.split("/")
        self.file_name = splited_file_path[-1]
        self.file_directory_path = "/".join(splited_file_path[:-1])