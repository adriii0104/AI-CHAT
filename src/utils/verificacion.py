import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario, asunto, contenido):
    remitente = 'ctgenuine@outlook.com'
    clave = 'Joselopez12@'

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    mensaje.attach(MIMEText(contenido, 'plain'))

    servidor_smtp = 'smtp-mail.outlook.com'
    puerto_smtp = 587
    servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
    servidor.starttls()

    servidor.login(remitente, clave)
    servidor.send_message(mensaje)
    servidor.quit()