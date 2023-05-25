import unittest
import mainWebPage
from mailManager import Mail
from unittest import TestCase
from unittest.mock import MagicMock, patch, call

class TestMainWeb(TestCase):

    def setUp(self):
        mainWebPage.app.config["TESTING"] = True
        self.flask = mainWebPage.app.test_client()

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

    @patch.object(Mail, "sendMailFromHTML")
    def testSendMail(self, mockSendMail):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput@gmail.com",
                                           "messageText": "testMessageText"})
        self.assertEqual(response.status_code, 200)
        mockSendMail.assert_called_once_with("testSenderInput@gmail.com", "Automatic mail from flask", "testMessageText")
        self.assertIn("Mail was sucessfuly was send", str(response.data))

if __name__ == "__main__":
    unittest.main()

    # przekazywać obiekt Gmail do MailManagera po to aby można było zamockować send_massage tak
    # samo jak w przypadku Config menagera