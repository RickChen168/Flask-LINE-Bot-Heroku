import os
import smtplib
from email.mime.text import MIMEText


def is_configured():
    return bool(os.environ.get("SMTP_HOST") and os.environ.get("MANAGER_EMAIL"))


def send_manager_email(subject, body):
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
    from_email = os.environ.get("FROM_EMAIL", username)
    to_emails = [e.strip() for e in os.environ["MANAGER_EMAIL"].split(",") if e.strip()]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        if username and password:
            server.login(username, password)
        server.sendmail(from_email, to_emails, msg.as_string())
