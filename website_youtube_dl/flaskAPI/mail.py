# from mainWebPage import app, logger, mail
# from flask import flash, render_template, request

# @app.route("/sendMail", methods=['POST'])
# def sendMail():
#     if request.method == "POST":
#         senderInput = request.form["senderInput"]
#         messageText = request.form["messageText"]
#         if len(senderInput) == 0 or "@" not in senderInput:
#             flash("Wrong mail adress", category="danger")
#             logger.warning("No email adress or email adress not contains @")
#             return render_template("mail.html")
#         if len(messageText) == 0:
#             flash("Wrong empty massage", category="danger")
#             logger.warning("Message text empty")
#             return render_template("mail.html")
#         mail.sendMailFromHTML(senderInput, "Automatic mail from flask", messageText)
#         flash("Mail was sucessfuly was send", category="success")
#         logger.info("Email successfully sent")
#     return render_template("mail.html")

# @app.route("/mail.html")
# def mail_html():
#     mail.initialize()
#     return render_template("mail.html")
