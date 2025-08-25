from flask import current_app as app
import os


class DownloadFileInfoSession():
    file_name = None
    file_directory_path = None

    def __init__(self, fullFilePath) -> None:
        self.set_session_download_data(fullFilePath)

    def set_session_download_data(self, fullFilePath):
        if not os.path.isfile(fullFilePath):
            raise FileNotFoundError(
                f"File {fullFilePath} doesn't exist - something went wrong")
        splited_file_path = fullFilePath.split("/")
        self.file_name = splited_file_path[-1]
        self.file_directory_path = "/".join(splited_file_path[:-1])


class SessionClient():

    def __init__(self, session):
        self.session = session

    def add_elem_to_session(self, key, value):
        self.session[key] = value

    def delete_elem_form_session(self, key):
        if not self.if_elem_in_session(key):
            return
        self.session.pop(key)

    def if_elem_in_session(self, key):
        if key not in self.session.keys():
            app.logger.error(f"Session doesn't have a key: {key}")
            return False
        return True

    def get_session_elem(self, key):
        if not self.if_elem_in_session(key):
            return
        return self.session[key]

    def print_session_keys(self):  # pragma: no_cover
        app.logger.info(self.session.keys())

    def clear_session(self):  # pragma: no_cover
        self.session.clear()

    def get_all_session_keys(self):  # pragma: no_cover
        return self.session.keys()

    def __del__(self):
        self.clear_session()
