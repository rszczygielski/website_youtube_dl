from website_youtube_dl.flaskAPI.session import SessionClient
from unittest import main, TestCase
from unittest.mock import patch
from website_youtube_dl.config import TestingConfig
from website_youtube_dl import create_app
from website_youtube_dl.flaskAPI.session import SessionDownloadData
import os


class SessionTest(TestCase):
    testKey1 = "key_1"
    testValue = "value_1"
    testPath = "testdir/testfile"

    def setUp(self):
        app = create_app(TestingConfig)
        sessionDict = {}
        self.sessionClient = SessionClient(sessionDict)
        self.flask = app.test_client()
        self.app = app

    def testAddElementToSession(self):
        sessionKeysEmpty = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionKeysEmpty), 0)
        self.sessionClient.addElemtoSession(self.testKey1, self.testValue)
        sessionOneElem = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionOneElem), 1)
        value = self.sessionClient.getSessionElem(self.testKey1)
        self.assertEqual(self.testValue, value)

    def testDeleteElementToSession(self):
        sessionKeysEmpty = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionKeysEmpty), 0)
        self.sessionClient.addElemtoSession(self.testKey1, self.testValue)
        sessionOneElem = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionOneElem), 1)
        self.sessionClient.deleteElemFormSession(self.testKey1)
        sessionAfterDelete = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionAfterDelete), 0)

    # test na delete jeśli nie ma elementu

    def testIfElemInSessionTrue(self):
        sessionKeysEmpty = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionKeysEmpty), 0)
        self.sessionClient.addElemtoSession(self.testKey1, self.testValue)
        sessionOneElem = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionOneElem), 1)
        result = self.sessionClient.ifElemInSession(self.testKey1)
        self.assertTrue(result)

    def testElemNotInSession(self):
        sessionKeysEmpty = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionKeysEmpty), 0)
        with self.app.app_context():
            result = self.sessionClient.ifElemInSession(self.testKey1)
        self.assertFalse(result)

    @patch.object(os.path, "isfile", return_value=True)
    def testInitSessionDownloadData(self, mockIsFile):
        sessionData = SessionDownloadData(self.testPath)
        mockIsFile.assert_called_once_with(self.testPath)
        splietedTestPath = self.testPath.split("/")
        fileName = splietedTestPath[-1]
        dirName = splietedTestPath[0]
        self.assertEqual(sessionData.fileName, fileName)
        self.assertEqual(sessionData.fileDirectoryPath, dirName)


if __name__ == "__main__":
    main()
