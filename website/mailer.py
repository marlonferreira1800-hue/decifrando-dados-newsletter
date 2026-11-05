import os
import smtplib
from email.message import EmailMessage


class LogMailer:
    def __init__(self):
        self.outbox = []

    def send(self, para, assunto, html):
        self.outbox.append({"para": para, "assunto": assunto, "html": html})
        print(f"[mail-log] para={para} assunto={assunto!r} bytes_html={len(html)}")
        return True, "registrado no log (SMTP nao configurado)"


class SMTPMailer:
    def __init__(self):
        self.host = os.environ.get("SMTP_HOST", "")
        self.porta = int(os.environ.get("SMTP_PORT", "587"))
        self.usuario = os.environ.get("SMTP_USER", "")
        self.senha = os.environ.get("SMTP_PASSWORD", "")
        self.remetente = os.environ.get("SMTP_FROM", "") or self.usuario or "newsletter@localhost"
        self.tls = os.environ.get("SMTP_TLS", "1") != "0"

    def send(self, para, assunto, html):
        msg = EmailMessage()
        msg["From"] = self.remetente
        msg["To"] = para
        msg["Subject"] = assunto
        msg.set_content("Esta edicao da newsletter possui conteudo HTML. Veja no site.")
        msg.add_alternative(html, subtype="html")
        try:
            with smtplib.SMTP(self.host, self.porta, timeout=30) as servidor:
                if self.tls:
                    servidor.starttls()
                if self.usuario:
                    servidor.login(self.usuario, self.senha)
                servidor.send_message(msg)
            return True, "enviado via SMTP"
        except Exception as exc:
            return False, str(exc)


def get_mailer():
    if os.environ.get("SMTP_HOST"):
        return SMTPMailer()
    return LogMailer()
