from unittest import TestCase, main
from common.mailManager import Mail
import mainWebPage
from unittest.mock import patch

class TestMail(TestCase):

    def setUp(self):
        mainWebPage.app.config["TESTING"] = True
        self.flask = mainWebPage.app.test_client()

    def testWrongSenMail(self):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput",
                                           "messageText": "testMessageText"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Wrong mail adress", str(response.data))

    def testSendMailWithNoText(self):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput@gmail.com",
                                    "messageText": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Wrong empty massage", str(response.data))

    @patch.object(Mail, "sendMailFromHTML")
    def testSendMail(self, mockSendMail):
        response = self.flask.post("/sendMail", data={"senderInput": "testSenderInput@gmail.com",
                                    "messageText": "testMessageText"})
        self.assertEqual(response.status_code, 200)
        mockSendMail.assert_called_once_with("testSenderInput@gmail.com", "Automatic mail from flask", "testMessageText")
        self.assertIn("Mail was sucessfuly was send", str(response.data))

    @patch.object(Mail, "initialize")
    def testMailHTML(self, mockInitialize):
        response = self.flask.get("/mail.html")
        self.assertEqual(response.status_code, 200)
        mockInitialize.assert_called_once()

if __name__ == "__main__":
    main()