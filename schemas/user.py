'''
    Schema responsible for defining how routes return messages are
    displayed and also for routes parameters validation.
'''
from pydantic import BaseModel, validator
from model.user import User
import re


class UserSchema(BaseModel):
    '''
        Define os parâmetros para criação de um usuário.
    '''
    username: str = 'Usuário Novo'
    password: str = 'a1c2d'
    
    @validator('username', allow_reuse = True)
    def validator_name(cls, parameter):
        '''Validator for username'''
        if not len(parameter) > 0 or parameter == '':
            raise ValueError('O nome não pode ser vazio!')
        if re.search('[0-9]', parameter):
            raise ValueError('O nome do usuário não pode conter números!')
        return parameter
    
    @validator('password', allow_reuse = True)
    def validator_name(cls, parameter):
        '''Validator for password'''
        if not len(parameter.strip()) > 3:
            raise ValueError('A senha precisa ter no mínimo 4 caracteres!')
        return parameter
