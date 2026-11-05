"""Envio de notificações por e-mail.

As credenciais vêm da configuração (nunca do código). Enquanto `SMTP_HOST`
estiver vazio — o default de desenvolvimento — o serviço apenas registra a
notificação em log, sem abrir conexão de rede.
"""
import logging
import smtplib

from models.base import now_utc

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, settings):
        self.settings = settings

    @property
    def enabled(self):
        return bool(self.settings.SMTP_HOST)

    def send_email(self, to, subject, body):
        if not self.enabled:
            logger.info('notificacao.simulada destinatario=%s assunto=%s', to, subject)
            return False
        try:
            server = smtplib.SMTP(self.settings.SMTP_HOST, self.settings.SMTP_PORT)
            server.starttls()
            if self.settings.SMTP_USER:
                server.login(self.settings.SMTP_USER, self.settings.SMTP_PASSWORD)
            server.sendmail(self.settings.SMTP_USER, to, f'Subject: {subject}\n\n{body}')
            server.quit()
            logger.info('notificacao.enviada destinatario=%s', to)
            return True
        except OSError:
            # Falha de notificação nunca deve derrubar a operação de negócio
            logger.exception('notificacao.falhou destinatario=%s', to)
            return False

    def notify_task_assigned(self, user, task):
        subject = f'Nova task atribuída: {task.title}'
        body = (
            f'Olá {user.name},\n\n'
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f'Prioridade: {task.priority}\nStatus: {task.status}'
        )
        return self.send_email(user.email, subject, body)

    def notify_task_overdue(self, user, task):
        subject = f'Task atrasada: {task.title}'
        body = (
            f'Olá {user.name},\n\n'
            f"A task '{task.title}' está atrasada!\n\n"
            f'Data limite: {task.due_date}'
        )
        return self.send_email(user.email, subject, body)


class NullNotificationService(NotificationService):
    """Usada em testes/seed: nunca envia nada."""

    def __init__(self):
        super().__init__(settings=None)

    @property
    def enabled(self):
        return False

    def send_email(self, to, subject, body):
        logger.debug('notificacao.ignorada destinatario=%s em=%s', to, now_utc())
        return False
