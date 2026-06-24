import string
import random
from typing import Dict, Optional
from ..sockets.session_data import DownloadFileInfo

class DownloadRegistry:
    """Encapsulates hash generation, uniqueness validation, and file metadata storage.

    This registry acts as an in-memory database mapping unique 6-character
    alphanumeric hashes to their corresponding download file metadata.

    Attributes:
        _registry (Dict[str, DownloadFileInfo]): Internal dictionary storing the mapped files.
    """

    def __init__(self) -> None:
        """Initializes an empty download registry."""
        self._registry: Dict[str, DownloadFileInfo] = {}

    def register_file(self, file_info: DownloadFileInfo) -> str:
        """Generates a guaranteed unique hash and registers the file metadata.

        Args:
            file_info (DownloadFileInfo): The metadata object containing the file path
                and playlist status.

        Returns:
            str: A unique 6-character alphanumeric hash associated with the registered file.
        """
        while True:
            # Generate hash
            new_hash = ''.join(random.sample(string.ascii_letters + string.digits, 6))
            # Check uniqueness
            if new_hash not in self._registry:
                self._registry[new_hash] = file_info
                return new_hash

    def get_file(self, file_hash: str) -> Optional[DownloadFileInfo]:
        """Retrieves file metadata associated with a specific hash.

        Args:
            file_hash (str): The unique 6-character hash identifier.

        Returns:
            Optional[DownloadFileInfo]: The file metadata object if found, otherwise None.
        """
        return self._registry.get(file_hash)