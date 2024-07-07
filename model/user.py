'''Module responsible for user model'''
from typing import Union
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from model import Base
import bcrypt

class User(Base):
    '''Class representing an user'''
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    username = Column(String(32), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default = datetime.now())
    updated_at = Column(DateTime, default = None)
    # relationship with model reminder
    reminder_relationship = relationship('Reminder')
    
    def __init__(
        self,
        username,
        password,
        created_at: Union[DateTime, None] = None,
        updated_at: Union[DateTime, None] = None):
        self.username = username
        self.set_password(password)

        if not created_at:
            self.created_at = created_at
        if not updated_at:
            self.updated_at = updated_at

    def set_password(self, password):
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)

        self.password_hash = hash.decode('utf-8')

    def verify_password(self, password) -> bool:
        bytes = password.encode('utf-8')
        hashed_password_bytes = self.password_hash.encode('utf-8')

        return bcrypt.checkpw(bytes, hashed_password_bytes)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
