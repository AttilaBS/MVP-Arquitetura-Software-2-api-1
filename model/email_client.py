'''Module responsible for email formatting and sending'''
import os
from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv

load_dotenv('../.env')


class EmailClient():
    '''Class representing a email_client'''
    def __init__(
        self,
        name: str,
        description: str,
        due_date: str,
        email_receiver: str,
        subject: str = 'Aviso de Lembrete',
        email_sender: str = os.environ.get('EMAIL_SENDER'),
        email_password: str = os.environ.get('APP_PASSWORD')):
        self.name = name
        self.description = description
        self.due_date = due_date
        self.email_receiver = email_receiver
        self.subject = subject
        self.email_sender = email_sender
        self.email_password = email_password

    def prepare_and_send_email(
            self,
            flag_create: bool = None,
            flag_update: bool = None,
            flag_due_date: bool = None) -> None:
        '''
            Function to create the email and send it.
        '''
        message = EmailMessage()
        if flag_create or flag_update:
            term = 'criado' if flag_update is None else 'atualizado'
            message.set_content(f'''
                    Olá usuário(a), este é um email automatizado para avisar
                    que o lembrete nome:  {self.name}, de descrição:
                    {self.description}, e com data final: {self.due_date},
                    foi {term}.

                    Atenciosamente,
                    Aplicativo Lembretes
                ''')
            message.add_alternative(f'''\
            <!DOCTYPE html>
                <html>
                    <body>
                        <h1 style="color:#dd8888;">Lembrete:</h1>
                            <div><p>Olá usuário(a), este é um email automatizado
                            para avisar </br> que o lembrete nome: <strong>{self.name}</strong> 
                            </br> de descrição: <strong>{self.description}</strong>,
                            e com data final: <strong>{self.due_date}</strong>,
                            </br> foi {term}.</p>
                                <p>Atenciosamente,</p>
                                <p>Aplicativo Lembretes</p>
                            </div>
                    </body>
                </html>
            ''', subtype = 'html')
        elif flag_due_date:
            message.set_content(f'''
                    Olá usuário(a), este é um email automatizado para avisar
                    que o lembrete nome:  {self.name}, de descrição:
                    {self.description}, e com data final: {self.due_date},
                    está próximo à data estipulada.

                    Atenciosamente,
                    Aplicativo Lembretes
                ''')
            message.add_alternative(f'''\
            <!DOCTYPE html>
                <html>
                    <body>
                        <h1 style="color:#dd8888;">Lembrete:</h1>
                            <div><p>Olá usuário(a), este é um email automatizado
                            para avisar </br> que o lembrete nome: <strong>{self.name}</strong>
                            </br> de descrição: <strong>{self.description}</strong>,
                            e com data final: <strong>{self.due_date}</strong>,
                            </br> está próximo à data estipulada.</p>
                                <p>Atenciosamente,</p>
                                <p>Aplicativo Lembretes</p>
                            </div>
                    </body>
                </html>
            ''', subtype = 'html')
        message['From'] = self.email_sender
        message['To'] = self.email_receiver
        message['Subject'] = self.subject
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(self.email_sender, self.email_password)
            smtp.sendmail(self.email_sender, self.email_receiver, message.as_string())
