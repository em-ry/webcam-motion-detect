# collects metadata of images
import imghdr
import os
import smtplib
from email.message import EmailMessage


PASSWORD = os.getenv("webcam_email")
SENDER = "emry390@gmail.com"
RECEIVER = "emry390@gmail.com"


def send_email(img_path):
    # create email message object
    email_message = EmailMessage()
    email_message["Subject"] = "New customer showed up!"
    email_message.set_content("Hey, we just saw a new customer!")

    with open(img_path, 'rb') as file:
        content = file.read()
    email_message.add_attachment(content, maintype="image", subtype=imghdr.what(None, content))

    # setup email server
    gmail = smtplib.SMTP("smtp.gmail.com", 587)

    # run routines to start email server parameters
    gmail.ehlo()
    gmail.starttls()

    gmail.login(SENDER, PASSWORD)
    gmail.sendmail(SENDER, RECEIVER, email_message.as_string())

    gmail.quit()

if __name__ == "__main__":
    send_email()
