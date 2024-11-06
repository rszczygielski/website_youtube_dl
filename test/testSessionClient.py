from website_youtube_dl.flaskAPI.session import SessionClient
from unittest import main, TestCase
from unittest.mock import patch


class SessionTest(TestCase):
    testKey1 = "key_1"
    testValue = "value_1"

    def setUp(self):
        sessionDict = {}
        self.sessionClient = SessionClient(sessionDict)

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

    def testIfElemInSessionTrue(self):
        sessionKeysEmpty = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionKeysEmpty), 0)
        self.sessionClient.addElemtoSession(self.testKey1, self.testValue)
        sessionOneElem = self.sessionClient.getAllSessionKeys()
        self.assertEqual(len(sessionOneElem), 1)
        result = self.sessionClient.ifElemInSession(self.testKey1)
        self.assertTrue(result)


    # def testElemNotInSession(self):
    #     sessionKeysEmpty = self.sessionClient.getAllSessionKeys()
    #     self.assertEqual(len(sessionKeysEmpty), 0)
    #     result = self.sessionClient.ifElemInSession(self.testKey1)
    #     self.assertTrue(result)
    #     self.assertFalse(result)


if __name__ == "__main__":
    main()
