import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config

from utils.html import render_template

def send_email(
    email_to,
    subject,
    message
):

    EMAIL_FROM = config('EMAIL_FROM')
    EMAIL_PASSWD = config('EMAIL_PASSWD')
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT')
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
    EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)

    email_message = MIMEMultipart()
    email_message['From'] = EMAIL_FROM
    email_message['To'] = email_to
    email_message['Subject'] = subject

    email_message.attach(MIMEText(message, 'html'))
    email_string = email_message.as_string()

    if EMAIL_USE_SSL:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context)
    else:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)

    server.ehlo()

    if EMAIL_USE_TLS: 
        server.starttls()
    
    server.login(EMAIL_FROM, EMAIL_PASSWD)
    server.sendmail(EMAIL_FROM, email_to, email_string)
    server.quit()

def send_template_email(
    email_to,
    subject,
    template_name,
    context
):

    content = render_template(template_name, context)
    send_email(email_to, subject, content)