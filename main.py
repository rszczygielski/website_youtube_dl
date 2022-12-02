from flask import Flask, render_template, request
from mailManager import MailManager

app = Flask(__name__)


# app.route jest po to aby wywołać funkcję pod tym adresem w przeglądarce
@app.route("/")
@app.route("/index.html")
@app.route('/example')
def index():
    # render_remplate daje mi odpowiedź na requesta z przeglądarki w postaci pliku HTML
    return render_template('index.html')

@app.route("/sendMail", methods=['POST'])
def sendMail():
    print("Send mail")
    if request.method == "POST":
        senderInput = request.form["senderInput"]
        messageText = request.form["messageText"]
        mailManager = MailManager("radek.szczygielski.trash@gmail.com")
        mailManager.sendMailFromHTML("Automatic mail from flask", f"Otrzymałem maile: {senderInput}<br> O treści: {messageText}""")
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)