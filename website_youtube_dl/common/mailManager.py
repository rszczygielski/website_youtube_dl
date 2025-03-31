from simplegmail import Gmail


class Mail():
    def __init__(self, sender):
        self.sender = sender

    def initialize(self):  # pragma: no_cover
        self.gmail = Gmail()

    def send_mail(self, msg, subject, toSend):  # pragma: no_cover
        self.gmail.send_message(
            to =toSend,
            msg_html =msg,
            sender =self.sender,
            subject =subject)

    def send_mail_from_h_t_m_l(self, autor, subject, msg):  # pragma: no_cover
        full_text = f"Otrzymałem maile: {autor}<br> O treści: {msg}"
        self.gmail.send_message(
            to ="radek.szczygielski87@gmail.com",
            msg_html =full_text,
            subject =subject,
            sender =self.sender)


if __name__ == "__main__":
    mail = Mail("radek.szczygielski.trash@gmail.com")
    mail.send_mail(msg="Hello World", subject ="Test email",
                  to_send ="radek.szczygielski87@gmail.com")
