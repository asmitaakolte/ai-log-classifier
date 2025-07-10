import smtplib
from email.mime.text import MIMEText

def send_email(smtp_server, smtp_port, smtp_user, smtp_pass, email_from, email_to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(email_from, email_to, msg.as_string())
            print(f"📧 Email sent to {email_to}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")