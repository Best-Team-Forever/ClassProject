import smtplib
import ssl
from email.message import EmailMessage

port = 465  # For SSL
password = "pnhv myhs hncs masy"

# Create a secure SSL context
context = ssl.create_default_context()


class EmailService:

    def build_message(self, subject, sender, receiver, content):
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = receiver
        message.set_content(content)
        return message

    def send_email(self, receiver, probability):
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("deepscan.patient.info@gmail.com", password)

            subject = 'Your analysis results'
            sender_name = 'DeepScan'
            content = f'Your risk score is: {round(probability, 2)}%'

            message = self.build_message(subject, sender_name, receiver, content)
            server.send_message(message)
