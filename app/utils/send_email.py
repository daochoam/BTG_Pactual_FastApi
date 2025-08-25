## Envío de correos electrónicos utils/send_email.py
import jwt
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import Config

def generate_verification_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def send_email(recipient, subject, body):
    msg = MIMEMultipart()
    msg['From'] = Config.SES_VERIFIED_EMAIL
    msg['To'] = recipient
    msg['Subject'] = subject

    if "Text" in body:
        msg.attach(MIMEText(body["Text"], 'plain'))
    if "Html" in body:
        msg.attach(MIMEText(body["Html"], 'html'))

    server = None
    try:
        server = smtplib.SMTP(Config.AWS_SMTP_HOST, Config.AWS_SMTP_PORT)
        server.starttls()
        server.login(Config.AWS_SMTP_USER, Config.AWS_SMTP_PASS)
        server.send_message(msg)
        print("Correo enviado correctamente")
    except Exception as e:
        print(f"Error al enviar correo: {e}")
    finally:
        if server:
            server.quit()

def send_subscription_funds_email(to_email, user_name, bank_fund):
    subject = "Fondo de Inversión Registrado"
    body = {
        "Html": f"Hola {user_name}, usted se ha registrado al fondo de inversión {bank_fund['name']} con un monto de {bank_fund['currency']} {bank_fund['min_amount']}."
    }

    try:
        send_email(to_email, subject, body)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
   
def send_retired_funds_email(to_email, user_name, bank_fund):
    subject = "Fondo de Inversión Retirado"
    body = {
        "Html": f"Hola {user_name}, se ha retirado del fondo de inversión {bank_fund['name']}, le ha sido retornado el capital invertido por valor de {bank_fund['currency']} {bank_fund['min_amount']}."
    }

    try:
        send_email(to_email, subject, body)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def send_insufficient_funds_email(to_email, user_name, bank_fund):
    subject = "Fondo de Inversión Insuficiente"
    body = {
        "Html": f"Hola {user_name}, usted no cuenta con saldo disponible para subscribirse al fondo de inversión {bank_fund['name']}. Para ello necesita disponer de un monto mínimo de {bank_fund['currency']} {bank_fund['min_amount']}."
    }

    try:
        send_email(to_email, subject, body)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False