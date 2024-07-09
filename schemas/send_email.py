'''
    Schema responsible for defining how routes return messages are
    displayed and also for routes parameters validation.
'''
from pydantic import BaseModel


class SendEmailSchema(BaseModel):
    '''
        Define os parâmetros para envio de payload de email para a api2.
    '''
    name: str = 'Lembrete teste, envio'
    description: str = 'Esta é a descrição de teste para envio de email'
    due_date: str = '15/09/2024'
    email_receiver: str = 'umemaildeteste@email.com'
    flag: str = 'create'
