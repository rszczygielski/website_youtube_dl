import os
from dataclasses import dataclass
from typing import Any, Type, Optional


@dataclass
class UserMessage:
    """Represents a message in user's session queue"""
    emit_type: Type
    data: Any
    is_error: bool = False

    def __iter__(self):
        """Allow unpacking like tuple: emit_type, data, is_error = message"""
        return iter((self.emit_type, self.data, self.is_error))


@dataclass
class BrowserSession:
    """Represents a browser session with Socket.IO session ID and timestamp"""
    session_id: str
    last_activity_timestamp: float

    def __iter__(self):
        """Allow unpacking like tuple: session_id, timestamp = session"""
        return iter((self.session_id, self.last_activity_timestamp))


class DownloadFileInfo():
    file_name = None
    file_directory_path = None
    is_playlist = None

    def __init__(self, fullFilePath: str, is_playlist: bool) -> None:
        self.set_file_download_data(fullFilePath)
        self.is_playlist = is_playlist

    def set_file_download_data(self, fullFilePath):
        if not os.path.isfile(fullFilePath):
            raise FileNotFoundError(
                f"File {fullFilePath} doesn't exist - something went wrong")
        splited_file_path = fullFilePath.split("/")
        self.file_name = splited_file_path[-1]
        self.file_directory_path = "/".join(splited_file_path[:-1])