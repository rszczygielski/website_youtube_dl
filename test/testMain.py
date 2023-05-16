import unittest
import main
from mailManager import Mail
from unittest import TestCase
from unittest.mock import MagicMock, patch, call

class TestMainWeb(TestCase):

    def setUp(self):
        main.app.config["TESTING"] = True
        main.mailManager
        self.flask = main.app.test_client()

    def testIndexHTML(self):
        response = self.flask.get("/index.html")
        self.assertIn("<title>FlaskHomePage</title>", str(response.data))
        self.assertEqual(response.status_code, 200)

    def testWrongHTML(self):
        response = self.flask.get("/index")
        self.assertEqual(response.status_code, 404)

    def testWrongSenMail(self):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput",
                                           "messageText": "testMessageText"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Wrong mail adress", str(response.data))

    @patch.object(Mail, "initialize")
    @patch.object(Mail, "sendMailFromHTML")
    def testSenMail(self, mockSendMail, mockInitialize):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput@gmail.com",
                                           "messageText": "testMessageText"})
        self.assertEqual(response.status_code, 200)
        mockSendMail.assert_called_once()
        mockInitialize.assert_called_once()
        # self.assertIn("Mail was sucessfuly was send", str(response.data))

if __name__ == "__main__":
    unittest.main()

    # przekazywać obiekt Gmail do MailManagera po to aby można było zamockować send_massage tak 
    # samo jak w przypadku Config menagera 