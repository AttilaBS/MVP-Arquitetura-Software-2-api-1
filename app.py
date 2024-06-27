'''Module responsible for routing'''
from datetime import datetime
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from unidecode import unidecode
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from model import Reminder, Email, EmailClient
from model import Session
from logger import logger
from schemas import *
import requests


info = Info(title = 'Reminder API', version = '1.0.0')
app = OpenAPI(__name__, info = info)
CORS(app)

documentation_tag = Tag(name = 'Documentação', description = 'Seleção de documentação: Swagger')
reminder_tag = Tag(name = 'Lembrete', description = 'Adição, edição, visualização individual ou geral e remoção de lembretes')
prepare_tag = Tag(name = 'Preparo de payload', description = 'Envia o payload do email à API específica para envio de emails.')
email_tag = Tag(name = 'Envio de Email', description = 'Envia um email de lembrete caso a data estipulada no lembrete esteja próxima')

@app.get('/', tags = [documentation_tag])
def documentation():
    '''
        Redireciona para openapi, com a documentação das rotas da API.
    '''
    return redirect('/openapi')

@app.post('/create', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema,
                     '409': ErrorSchema,
                     '400': ErrorSchema})
def create(form: ReminderSchema):
    '''
        Persiste um novo lembrete no banco de dados.
    '''
    reminder = Reminder(
        name = form.name,
        description = form.description,
        due_date = datetime.strptime(form.due_date, '%Y-%m-%dT%H:%M:%S.%fZ'),
        send_email = form.send_email,
        recurring = form.recurring)

    try:
        reminder.insert_email(Email(form.email))
        session = Session()
        session.add(reminder)
        logger.debug('Adicionado lembrete de nome: %s', reminder.name)
        session.commit()
        if reminder.validate_email_before_send():
            email_receiver = reminder.email_relationship[0].email
            due_date_adjusted = reminder.due_date.strftime('%d/%m/%Y')
            payload = {
                'name': reminder.name,
                'description': reminder.description,
                'due_date': due_date_adjusted,
                'email_receiver': email_receiver
            }
            response = __email_payload(payload)
            logger.debug(f'Response email_payload: {response}')

            # email_client.prepare_and_send_email(flag_create = True)
        # After email validation and sending or not, commit changes

        return show_reminder(reminder), 200

    except IntegrityError:
        error_msg = 'Lembrete de mesmo nome já salvo :/'
        logger.warning('Erro ao adicionar lembrete %s - %s', reminder.name, error_msg)

        return format_error_response(error_msg, 409)

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete.'
        logger.warning(' %s : %s', error_msg, error)
        logger.debug(' %s : %s', error_msg, error)

        return format_error_response(error_msg, 400)

@app.get('/reminder', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def get_reminder(query: ReminderSearchSchema):
    '''
        Retorna o lembrete buscado pelo id.
    '''
    reminder_id = query.id
    logger.info('Coletando dados sobre o lembrete # %s', reminder_id)

    try:
        session = Session()
        reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
        logger.info('reminder: %s', reminder.name)
    except Exception as error:
        error_msg = 'O lembrete buscado não existe.'
        logger.debug('Exceção : %s', error)
        logger.warning('Erro ao buscar lembrete %s : %s', reminder_id, error_msg)

        return format_error_response(error_msg, 404)
    logger.debug('Lembrete econtrado: %s', reminder.name)

    return show_reminder(reminder), 200

@app.get('/reminder_name', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def get_reminder_name(query: ReminderSearchByNameSchema):
    '''
        Retorna o lembrete buscado pelo nome.
    '''
    reminder_name = query.name
    logger.info('Coletando dados sobre o lembrete # %s', reminder_name)

    session = Session()
    name_normalized = unidecode(reminder_name.lower())
    reminder = session.query(Reminder).filter(Reminder.name_normalized == name_normalized).first()

    error_msg = 'O lembrete buscado não existe.'
    if not reminder:
        logger.warning('Erro ao buscar lembrete %s - %s', reminder_name, error_msg)
        return format_error_response(error_msg, 404)

    logger.debug('Lembrete encontrado: %s', reminder.name)
    return show_reminder(reminder), 200

@app.get('/reminders', tags = [reminder_tag],
         responses = {'200': RemindersListSchema, '404': ErrorSchema})
def get_all_reminders():
    '''
        Retorna todos os lembretes salvos no banco de dados.
    '''
    logger.debug('Retornando todos os lembretes')
    session = Session()
    reminders = session.query(Reminder).all()

    if not reminders:
        return {'Lembretes': []}, 200

    logger.debug('%d lembretes encontrados', len(reminders))
    return show_reminders(reminders), 200

@app.put('/update', tags = [reminder_tag],
         responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def update(form: ReminderUpdateSchema):
    '''
        Atualiza um lembrete pelo id.
    '''
    session = Session()
    reminder = session.query(Reminder).filter(Reminder.id == form.id).first()

    logger.debug('Alterando um lembrete de nome: %s', reminder.name)
    try:
        reminder.name = form.name or reminder.name
        reminder.name_normalized = unidecode(form.name.lower())
        reminder.description = form.description or reminder.description
        reminder.due_date = form.due_date or reminder.due_date
        reminder.send_email = form.send_email
        reminder.email_relationship[0].email = form.email
        reminder.recurring = form.recurring
        reminder.updated_at = datetime.now()

        logger.debug('Lembrete atualizado, nome: %s', reminder.name)

        if reminder.validate_email_before_send():
            #Sending email if has an email and send_email is True
            email_receiver = reminder.email_relationship[0].email
            due_date_adjusted = reminder.due_date.strftime('%d/%m/%Y')
            email_client = EmailClient(
                reminder.name,
                reminder.description,
                due_date_adjusted,
                email_receiver
                )
            email_client.prepare_and_send_email(flag_update = True)
        # After email validation and sending or not, commit changes
        session.commit()

        return show_reminder(reminder), 200

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete na base'
        logger.info(' %s : %s', error_msg, error)
        return format_error_response(error_msg, 500)

@app.delete('/delete', tags = [reminder_tag],
            responses = {'200': ReminderDeleteSchema, '404': ErrorSchema})
def delete_reminder(query: ReminderSearchSchema):
    '''
        Remove um lembrete pelo id.
    '''
    reminder_id = query.id
    logger.debug('Deletando dados do lembrete # %d', reminder_id)

    session = Session()
    try:
        session.query(Email).filter(Email.reminder == reminder_id).delete()
        reminder_query = session.query(Reminder).filter(Reminder.id == reminder_id)
        reminder = reminder_query.first()
        reminder_query.delete()
        session.commit()
    except:
        error_msg = 'Lembrete não encontrado :/'
        logger.warning('Erro ao deletar lembrete # %d - %s', reminder_id, error_msg)
        return format_error_response(error_msg, 404)

    logger.debug('Lembrete # %d removido com sucesso.', reminder_id)
    return {'mensagem': 'Lembrete removido', 'nome': reminder.name}

def __email_payload(payload):
    '''
        Esta rota envia o payload de email para a api de envio de email.
    '''
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://api2:5000/prepare', json=payload, headers=headers)
        logger.debug(f'response : {response}')
        return response
    except Exception as error:
        logger.warning('Erro ao validar e enviar email para lembrete#')
        return {'mensagem': 'Ocorreu um erro ao enviar o email: %s', 'erro': error}, 404

@app.route('/format_error')
def format_error_response(error_message:str, status:int) -> list:
    response = [
        {
            'ctx': {
                'error': error_message
            }
        }
    ]

    return response, status
