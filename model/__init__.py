'''Module responsible for initializing the database'''
import os
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from model.base import Base
from model.email import Email
from model.email_client import EmailClient
from model.reminder import Reminder

DB_PATH = 'database/'
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

DB_URL = 'sqlite:///%s/db.sqlite3' % DB_PATH
engine = create_engine(DB_URL, echo = False)

Session = sessionmaker(bind = engine)

if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)
