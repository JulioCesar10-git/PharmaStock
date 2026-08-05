import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def enviar_ticket_por_correo(destinatario, ticket_texto, folio):
    try:
        remitente = os.getenv("GMAIL_USER")
        password = os.getenv("GMAIL_APP_PASSWORD")

        mensaje = MIMEMultipart()
        mensaje["From"] = remitente
        mensaje["To"] = destinatario
        mensaje["Subject"] = f"Ticket de compra - {folio}"
        mensaje.attach(MIMEText(ticket_texto, "plain"))

        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.send_message(mensaje)
        servidor.quit()

        print(f"Ticket enviado a {destinatario}")

    except Exception as e:

        print("Error al enviar el ticket")
        print(e)

