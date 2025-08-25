import os


class DownloadFileInfo():
    file_name = None
    file_directory_path = None
    media_from_playlist = None

    def __init__(self, fullFilePath: str, media_from_playlist) -> None:
        self.set_file_download_data(fullFilePath)
        self.media_from_playlist = media_from_playlist

    def set_file_download_data(self, fullFilePath):
        if not os.path.isfile(fullFilePath):
            raise FileNotFoundError(
                f"File {fullFilePath} doesn't exist - something went wrong")
        splited_file_path = fullFilePath.split("/")
        self.file_name = splited_file_path[-1]
        self.file_directory_path = "/".join(splited_file_path[:-1])

