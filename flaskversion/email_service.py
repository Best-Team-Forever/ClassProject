import smtplib
import ssl
from email.message import EmailMessage

port = 465  # For SSL
password = "pnhv myhs hncs masy"

# Create a secure SSL context
context = ssl.create_default_context()


class EmailService:

    def send_email(self, receiver):
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("deepscan.patient.info@gmail.com", password)

            message = EmailMessage()
            message['Subject'] = 'Your analysis results'
            message['From'] = 'DeepScan'
            message['To'] = 'alejandro855@gmail.com'
            message.set_content('Your risk score is: 10%')

            server.send_message(message)
