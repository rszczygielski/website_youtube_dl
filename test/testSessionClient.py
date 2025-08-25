from website_youtube_dl.flaskAPI.sessions.session import SessionClient
from unittest import main, TestCase
from unittest.mock import patch
from website_youtube_dl.config import TestingConfig
from website_youtube_dl import create_app
from website_youtube_dl.flaskAPI.sessions.session import DownloadFileInfoSession
from unittest.mock import MagicMock
import os


class SessionTest(TestCase):
    test_key1 = "key_1"
    test_value = "value_1"
    test_path = "testdir/testfile"

    def setUp(self):
        self.config_manager_mock = MagicMock()
        app = create_app(TestingConfig, self.config_manager_mock)
        session_dict = {}
        self.session_client = SessionClient(session_dict)
        self.flask = app.test_client()
        self.app = app

    def test_add_element_to_session(self):
        session_keys_empty = self.session_client.get_all_session_keys()
        self.assertEqual(len(session_keys_empty), 0)
        self.session_client.add_elem_to_session(
            self.test_key1, self.test_value)
        session_one_elem = self.session_client.get_all_session_keys()
        self.assertEqual(len(session_one_elem), 1)
        value = self.session_client.get_session_elem(self.test_key1)
        self.assertEqual(self.test_value, value)

    def test_delete_element_to_session(self):
        session_keys_empty = self.session_client.get_all_session_keys()
        self.assertEqual(len(session_keys_empty), 0)
        self.session_client.add_elem_to_session(
            self.test_key1, self.test_value)
        session_one_elem = self.session_client.get_all_session_keys()
        self.assertEqual(len(session_one_elem), 1)
        self.session_client.delete_elem_form_session(self.test_key1)
        sessionAfterDelete = self.session_client.get_all_session_keys()
        self.assertEqual(len(sessionAfterDelete), 0)

    # test na delete jeśli nie ma elementu

    def test_if_elem_in_session_true(self):
        session_keys_empty = self.session_client.get_all_session_keys()
        self.assertEqual(len(session_keys_empty), 0)
        self.session_client.add_elem_to_session(
            self.test_key1, self.test_value)
        session_one_elem = self.session_client.get_all_session_keys()
        self.assertEqual(len(session_one_elem), 1)
        result = self.session_client.if_elem_in_session(self.test_key1)
        self.assertTrue(result)

    def test_elem_not_in_session(self):
        session_keys_empty = self.session_client.get_all_session_keys()
        self.assertEqual(len(session_keys_empty), 0)
        with self.app.app_context():
            result = self.session_client.if_elem_in_session(self.test_key1)
        self.assertFalse(result)

    @patch.object(os.path, "isfile", return_value=True)
    def test_init_session_download_data(self, mock_is_file):
        session_data = DownloadFileInfoSession(self.test_path)
        mock_is_file.assert_called_once_with(self.test_path)
        splieted_test_path = self.test_path.split("/")
        file_name = splieted_test_path[-1]
        dir_name = splieted_test_path[0]
        self.assertEqual(session_data.file_name, file_name)
        self.assertEqual(session_data.file_directory_path, dir_name)


if __name__ == "__main__":
    main()
