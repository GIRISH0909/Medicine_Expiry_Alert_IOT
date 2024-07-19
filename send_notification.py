import smtplib
from email.mime.text import MIMEText


def send_email(subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = ''
    sender_password = ''
    recipient_email = ''

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Create the email message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send the email
    server.sendmail(sender_email, [recipient_email], msg.as_string())

    # Close the connection
    server.quit()


send_email('Medicine Expiry Alert (Test)',
           '')
