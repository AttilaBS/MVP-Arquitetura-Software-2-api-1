'''
    Schema responsible for defining how routes return messages are
    displayed and also for routes parameters validation.
'''
from typing import Optional, List
import re
from datetime import datetime
from pydantic import BaseModel, validator
from model.reminder import Reminder


class ReminderSchema(BaseModel):
    '''
        Define como um novo lembrete a ser persistido deve ser.
    '''
    name: str = 'Trocar o óleo do carro'
    description: str = 'trocar o óleo a cada 10 mil km no Moraes AutoCenter'
    due_date: str = '2023-09-20T00:00:00.000Z'
    send_email: Optional[bool] = False
    email: str
    recurring: Optional[bool] = False

    @validator('name', allow_reuse = True)
    def validator_name(cls, parameter):
        '''Validator for name'''
        if not len(parameter) > 0:
            raise ValueError('O nome não pode ser vazio!')
        if re.search('[0-9]', parameter):
            raise ValueError('O nome do lembrete não pode conter números')
        return parameter

    @validator('description', allow_reuse = True)
    def validator_description(cls, parameter):
        '''Validator for description'''
        if not len(parameter) > 0:
            raise ValueError('A descrição não pode ser vazia!')
        return parameter

    @validator('email', allow_reuse = True, check_fields=False)
    def validator_email(cls, parameter):
        '''Validator for email'''
        if not len(parameter) > 0:
            raise ValueError('O email não pode ser vazio!')
        return parameter


class ReminderUpdateSchema(BaseModel):
    '''
        Define como um lembrete a ser atualizado pode ser salvo.
    '''
    id: int = 1
    name: Optional[str] = 'Ir no dentista'
    name_normalized: str = 'ir no dentista'
    description: Optional[str] = 'Marcar o retorno da consulta'
    due_date: Optional[datetime] = '2023-10-20T00:00:00.000Z'
    send_email: Optional[bool] = True
    email: str = 'emaildeexemplo@email.com'
    recurring: Optional[bool] = False
    updated_at: datetime = datetime.now()

    @validator('name', allow_reuse = True)
    def validator_name(cls, parameter):
        '''Validator for name'''
        if not len(parameter) > 0:
            raise ValueError('O nome não pode ser vazio!')
        if re.search('[0-9]', parameter):
            raise ValueError('O nome do lembrete não pode conter números')
        return parameter

    @validator('description')
    def validator_description(cls, parameter):
        '''Validator for description'''
        if not len(parameter) > 0:
            raise ValueError('A descrição não pode ser vazia!')
        return parameter


class ReminderSearchSchema(BaseModel):
    '''
        Define como será a busca de lembrete apenas pelo id.
    '''
    id: int


class ReminderSearchByNameSchema(BaseModel):
    '''
        Define como será a busca de lembrete apenas pelo nome.
    '''
    name: str


class ReminderDeleteSchema(BaseModel):
    '''
        Define como será o retorno após a remoção de um lembrete.
    '''
    message: str
    name: str


class RemindersListSchema(BaseModel):
    '''
        Define como a listagem de lembretes será retornada.
    '''
    reminders:List[ReminderSchema]


class ReminderViewSchema(BaseModel):
    '''
        Define como será a visualização de um lembrete.
    '''
    id: int
    name: str
    name_normalized: str
    description: str
    due_date: datetime
    email: str
    send_email: Optional[bool]
    recurring: Optional[bool]

def show_reminder(reminder: Reminder):
    '''
        Retorna a representação de um lembrete seguindo o esquema definido
        em ReminderViewSchema.
    '''
    return {
        'id': reminder.id,
        'name': reminder.name,
        'name_normalized': reminder.name_normalized,
        'description': reminder.description,
        'due_date': reminder.due_date,
        'send_email': reminder.send_email,
        'email': reminder.email_relationship[0].email,
        'recurring': reminder.recurring
    }

def show_reminders(reminders: List[Reminder]):
    '''
        Retorna a representação do lembrete seguindo o esquema definido
        em ReminderViewSchema.
    '''
    result = []
    for reminder in reminders:
        result.append({
            'id': reminder.id,
            'name': reminder.name,
            'name_normalized': reminder.name_normalized,
            'description': reminder.description,
            'due_date': reminder.due_date,
            'send_email': reminder.send_email,
            'email': reminder.email_relationship[0].email,
            'recurring': reminder.recurring
        })
    return {'reminders': result}
