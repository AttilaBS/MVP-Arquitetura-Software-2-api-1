'''Schema responsible for defining how error messages are displayed'''
from pydantic import BaseModel


class ErrorSchema(BaseModel):
    '''
        Define como uma mensagem de erro será representada.
    '''
    message: str
