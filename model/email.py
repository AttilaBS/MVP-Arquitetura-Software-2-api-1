'''Module responsible for email relationship model'''
from datetime import datetime
from typing import Union
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from model import Base


class Email(Base):
    '''Class representing an email'''
    __tablename__ = 'email'

    id = Column(Integer, primary_key = True)
    email = Column(String(60))
    #relation
    reminder = Column(Integer, ForeignKey('reminder.pk_reminder'), nullable = False)
    created_at = Column(DateTime, default = datetime.now())
    updated_at = Column(DateTime, default = None)

    def __init__(
        self,
        email:str,
        created_at:Union[DateTime, None] = None,
        updated_at:Union[DateTime, None] = None):
        '''
            Adiciona um email a um lembrete.
        '''
        self.email = email
        if not created_at:
            self.created_at = created_at
        if not updated_at:
            self.updated_at = updated_at
