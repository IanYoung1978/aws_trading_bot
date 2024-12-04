import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_email(subject, body, to=config.EMAIL_ADDRESS):
    try:
        with smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_PORT) as server:
            server.starttls()
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

            msg = MIMEMultipart()
            msg['From'] = config.EMAIL_ADDRESS
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server.send_message(msg)
            print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")
