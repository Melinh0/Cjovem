import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    DESTINATARIOS_IMERSAO,
    SMTP_HOST,
    SMTP_PORT,
    ler_lista_arquivo,
    require_email_credentials,
)

emails = ler_lista_arquivo(DESTINATARIOS_IMERSAO)

remetente, senha = require_email_credentials()

assunto = "Aviso Imersão CJovem"
mensagem = """
Pessoal, o professor Lucas vai passar para conversar e planejar com as equipes e enquanto e não chega para atender vocês, priorizem de debaterem e discutirem evoluções do projeto e elicitar dúvidas com ele."""

try:
    servidor = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    servidor.starttls()
    servidor.login(remetente, senha)

    for destino in emails:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destino
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'plain'))

        servidor.sendmail(remetente, destino, msg.as_string())
        print(f"E-mail enviado para {destino}")

    servidor.quit()
    print("Todos os e-mails foram enviados com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
