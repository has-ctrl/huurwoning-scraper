import smtplib
from email.message import EmailMessage
from datetime import datetime


def send_email(config: dict, urls: list):
    """
    Send email with available 'homes' based on config.
    """
    host, port = config["mail"]["host"], config["mail"]["port"]
    user, password = config["mail"]["sender"], config["mail"]["password"]
    receivers = config["mail"]["receivers"]
    dt = datetime.today()

    with smtplib.SMTP_SSL(host=host, port=port) as server:
        server.login(user=user, password=password)

        msg = EmailMessage()
        msg["Subject"] = f"{len(urls)} NEW HOMES! | {dt.strftime('%d-%m-%Y %H:%M')}"
        msg["From"] = f"{config['mail']['display_name']} <{user}>"
        msg["To"] = ', '.join(receivers)

        body = "\n\n".join(urls)
        msg.set_content(body)

        server.send_message(msg=msg)

    print("Sent!")


