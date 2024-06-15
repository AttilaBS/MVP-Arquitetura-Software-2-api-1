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


info = Info(title = 'Reminder API', version = '1.0.0')
app = OpenAPI(__name__, info = info)
CORS(app)

documentation_tag = Tag(name = 'Documentação', description = 'Seleção de documentação: Swagger')
reminder_tag = Tag(name = 'Lembrete', description = 'Adição, edição, visualização individual ou geral e remoção de lembretes')
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

    logger.debug('Adicionando um lembrete de nome: %s', reminder.name)
    try:
        reminder.insert_email(Email(form.email))
        session = Session()
        session.add(reminder)
        logger.debug('Adicionado lembrete de nome: %s', reminder.name)

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
            email_client.prepare_and_send_email(flag_create = True)
        # After email validation and sending or not, commit changes
        session.commit()

        return show_reminder(reminder), 200

    except IntegrityError:
        error_msg = 'Lembrete de mesmo nome já salvo na base :/'
        logger.warning('Erro ao adicionar lembrete %s - %s', reminder.name, error_msg)

        return {'mensagem': error_msg}, 409

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete na base'
        logger.warning(' %s : %s', error_msg, error)
        logger.debug(' %s : %s', error_msg, error)

        return {'mensagem': error_msg}, 400

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

        return {'mensagem': error_msg}, 404
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
        return {'mensagem': error_msg}, 404

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
        return {'mensagem': error_msg}, 400

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
        return {'mensagem': error_msg}, 404

    logger.debug('Lembrete # %d removido com sucesso.', reminder_id)
    return {'mensagem': 'Lembrete removido', 'nome': reminder.name}

@app.get('/send_email', tags = [email_tag],
         responses = {'200': EmailSentSchema, '404': ErrorSchema})
def validate_send_email(query: ReminderSearchSchema):
    '''
        Esta rota envia um email com as informações do lembrete, ao email cadastrado.
        Regras para enviar email por esta rota:
        1) Email cadastrado no lembrete,
        2) Boolean send_email como True,
        3) Lembrete a 1 dia ou menos de alcançar a data final (due_date).
    '''
    session = Session()
    reminder = session.query(Reminder).filter(Reminder.id == query.id).first()
    send_email: bool = reminder.validate_email_before_send()

    if send_email and reminder.validate_due_date():
        email_receiver = reminder.email_relationship[0].email
        due_date_adjusted = reminder.due_date.strftime('%d/%m/%Y')
        email_client = EmailClient(
            reminder.name,
            reminder.description,
            due_date_adjusted,
            email_receiver
            )
        try:
            email_client.prepare_and_send_email(flag_due_date = True)
            return {'mensagem': f'Email avisando do prazo final do lembrete enviado para o destinatário: {email_receiver}'}, 200
        except Exception as error:
            logger.warning('Erro ao validar e enviar email para lembrete# %d - erro : %s', reminder.id, error)
            return {'mensagem': 'Ocorreu um erro ao enviar o email.'}, 404
    else:
        if not reminder.email_relationship[0].email:
            return {'mensagem': 'O lembrete não possui email cadastrado'}, 200
        if not reminder.send_email:
            return {'mensagem': 'O usuário optou por não receber email.'}, 200
        return {'mensagem': f'A data do lembrete é {reminder.due_date} e, portanto, superior à 1 dia a data atual'}, 200
