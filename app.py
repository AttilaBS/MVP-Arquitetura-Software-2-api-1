'''Module responsible for routing'''
from datetime import datetime
from flask_openapi3 import OpenAPI, Info, Tag
from flask_httpauth import HTTPBasicAuth
from flask import redirect, request, g
from unidecode import unidecode
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from model import Reminder, Email, User
from model import Session
from logger import logger
from schemas import *
import requests

info = Info(title = 'Reminder API', version = '1.0.0')
app = OpenAPI(__name__, info = info)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
CORS(app)
auth = HTTPBasicAuth()

documentation_tag = Tag(name = 'Documentação', description = 'Seleção de documentação: Swagger')
reminder_tag = Tag(name = 'Lembrete', description = 'Adição, edição, visualização individual ou geral e remoção de lembretes')
prepare_tag = Tag(name = 'Preparo de payload', description = 'Envia o payload do email à API específica para envio de emails.')
user_tag = Tag(name = 'Usuário', description = 'Adição, validação e busca de usuário.')
send_email_tag = Tag(name = 'Envio de email', description = 'Rota de envio de email.')


@app.get('/', tags = [documentation_tag])
def documentation():
    '''
        Redireciona para openapi, com a documentação das rotas da API.
    '''
    return redirect('/openapi')


@app.post('/user/create', tags = [user_tag],
          responses = {'200': UserViewSchema,
                     '400': ErrorSchema})
def new_user(form: UserSchema):
    '''
        Cria um novo usuário na aplicação.
    '''
    name = form.username
    passkey = form.password
    session = Session()
    if name is None or passkey is None:
        error_msg = 'O username e senha são obrigatórios!'
        return format_error_response(error_msg, 400)

    if session.query(User).filter(User.username == name).first() is not None:
        error_msg = 'Não é possível utilizar este nome!'
        return format_error_response(error_msg, 400)

    user = User(name, passkey)
    session.add(user)
    session.commit()

    return { 'username': user.username }, 201


@app.post('/user/validate', tags = [user_tag],
          responses = {'200': UserViewSchema,
                     '400': ErrorSchema})
def validate_user(form: UserSchema):
    '''
        Faz a validação do username e do hash da senha, salvos na aplicação.
    '''
    name = form.username
    passkey = form.password
    session = Session()
    user = session.query(User).filter(User.username == name).first()
    if user is not None:
        if user.verify_password(passkey):
            return { 'username': user.username }, 200
    error_msg = 'Não foi encontrado usuário com essas credenciais!'
    return format_error_response(error_msg, 400)


@app.get('/user/get/', tags = [user_tag],
         responses = {'200': UserWithIdViewSchema,
                     '400': ErrorSchema})
def get_user(query: UserSearchSchema):
    '''
        Retorna o username e o id do usuário.
    '''
    if request.args.get('username'):
        username = request.args.get('username')
    else:
        username = query.username
    session = Session()
    user = session.query(User).filter(User.username == username).first()
    if not user:
        error_msg = 'Não foi encontrado usuário !'
        return format_error_response(error_msg, 400)
    return {'username': user.username, 'user_id': user.id}

@auth.verify_password
def verify_password(username, password):
    '''
        Rota para validar a sessão do usuário logado em rotas protegidas.
    '''
    if not username:
        username = request.args.get('username')
    session = Session()
    user = session.query(User).filter(User.username == username).first()
    if user and password:
        validation = user.verify_password(password)
    if user and not password:
        return True
    if not user or not validation:
        return False
    g.user = user
    return True

@auth.error_handler
def auth_error():
    error_msg = 'Você precisa estar logado para acessar os lembretes.'
    return format_error_response(error_msg, 403)

@app.post('/create', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema,
                     '409': ErrorSchema,
                     '400': ErrorSchema})
@auth.login_required
def create(form: ReminderSchema, query: ReminderCreateOrUpdateSchema):
    '''
        Persiste um novo lembrete no banco de dados.
        Se for inserido um email válido e a flag send_email como True,
        enviará um email com os dados do lembrete.
    '''
    if request.args.get('username'):
        username = request.args.get('username')
    else:
        username = query.username
    user = get_user(username)
    reminder = Reminder(
        name = form.name,
        description = form.description,
        user_id = user['user_id'],
        due_date = datetime.strptime(form.due_date, '%Y-%m-%dT%H:%M:%S.%fZ'),
        send_email = form.send_email,
        recurring = form.recurring)

    try:
        reminder.insert_email(Email(form.email))
        session = Session()
        session.add(reminder)
        session.commit()
        if reminder.validate_email_before_send():
            email_receiver = reminder.email_relationship[0].email
            due_date_adjusted = reminder.due_date.strftime('%d/%m/%Y')
            payload = {
                'name': reminder.name,
                'description': reminder.description,
                'due_date': due_date_adjusted,
                'email_receiver': email_receiver,
                'flag': 'create'
            }
            __sent_email_payload(payload)

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
@auth.login_required
def get_reminder(query: ReminderSearchSchema):
    '''
        Retorna o lembrete buscado pelo id e username.
    '''
    reminder_id = query.id
    if request.args.get('username'):
        username = request.args.get('username')
    else:
        username = query.username
    user = get_user(username)
    logger.info('Coletando dados sobre o lembrete # %s', reminder_id)
    try:
        session = Session()
        reminder = session.query(Reminder).filter(
                Reminder.id == reminder_id,
                Reminder.user_id == user['user_id']
            ).first()
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
@auth.login_required
def get_reminder_name(query: ReminderSearchByNameSchema):
    '''
        Retorna o lembrete buscado pelo nome.
    '''
    reminder_name = query.name
    if request.args.get('username'):
        username = request.args.get('username')
    else:
        username = query.username
    user = get_user(username)
    logger.info('Coletando dados sobre o lembrete # %s', reminder_name)

    session = Session()
    name_normalized = unidecode(reminder_name.lower())
    reminder = session.query(Reminder).filter(
            Reminder.name_normalized == name_normalized,
            Reminder.user_id == user['user_id']
        ).first()

    if not reminder:
        error_msg = 'O lembrete buscado não existe.'
        logger.warning('Erro ao buscar lembrete %s - %s', reminder_name, error_msg)
        return format_error_response(error_msg, 404)

    logger.debug('Lembrete encontrado: %s', reminder.name)
    return show_reminder(reminder), 200

@app.get('/reminders', tags = [reminder_tag],
         responses = {'200': RemindersListSchema, '404': ErrorSchema})
@auth.login_required
def get_all_reminders(query: RemindersSearchSchema):
    '''
        Retorna todos os lembretes salvos no banco de dados de usuário específico.
    '''
    if request.args.get('username'):
        username = request.args.get('username')
    else:
        username = query.username
    session = Session()
    user = get_user(username)
    reminders = session.query(Reminder).filter(Reminder.user_id == user['user_id']).all()

    if not reminders:
        return {'Lembretes': []}, 200

    logger.debug('%d lembretes encontrados', len(reminders))
    return show_reminders(reminders), 200

@app.put('/update', tags = [reminder_tag],
         responses = {'200': ReminderViewSchema, '404': ErrorSchema})
@auth.login_required
def update(form: ReminderUpdateSchema, query: ReminderCreateOrUpdateSchema):
    '''
        Atualiza um lembrete pelo id. Se for inserido um email válido e a flag
        send_email como True, enviará um email com os dados do lembrete.
    '''
    session = Session()
    if request.args.get('username'):
        username = request.args.get('username')
    else:
        username = query.username
    session = Session()
    user = get_user(username)
    reminder = session.query(Reminder).filter(
            Reminder.id == form.id,
            Reminder.user_id == user['user_id']
        ).first()
    try:
        reminder.name = form.name or reminder.name
        reminder.name_normalized = unidecode(form.name.lower())
        reminder.description = form.description or reminder.description
        reminder.due_date = form.due_date or reminder.due_date
        reminder.send_email = form.send_email
        reminder.email_relationship[0].email = form.email
        reminder.recurring = form.recurring
        reminder.updated_at = datetime.now()
        session.commit()

        if reminder.validate_email_before_send():
            email_receiver = reminder.email_relationship[0].email
            due_date_adjusted = reminder.due_date.strftime('%d/%m/%Y')
            payload = {
                'name': reminder.name,
                'description': reminder.description,
                'due_date': due_date_adjusted,
                'email_receiver': email_receiver,
                'flag': 'update'
            }
            __sent_email_payload(payload)

        return show_reminder(reminder), 200

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete na base'
        logger.info(' %s : %s', error_msg, error)
        return format_error_response(error_msg, 500)

@app.delete('/delete', tags = [reminder_tag],
            responses = {'200': ReminderDeleteSchema, '404': ErrorSchema})
@auth.login_required
def delete_reminder(query: ReminderSearchSchema):
    '''
        Remove um lembrete pelo id.
    '''
    reminder_id = query.id
    user = get_user(request.args.get('username'))
    logger.debug('Deletando dados do lembrete # %d', reminder_id)

    session = Session()
    try:
        session.query(Email).filter(Email.reminder == reminder_id).delete()
        reminder_query = session.query(Reminder).filter(
                Reminder.id == reminder_id,
                Reminder.user_id == user['user_id']
            )
        reminder = reminder_query.first()
        reminder_query.delete()
        session.commit()
    except:
        error_msg = 'Lembrete não encontrado :/'
        logger.warning('Erro ao deletar lembrete # %d - %s', reminder_id, error_msg)
        return format_error_response(error_msg, 404)

    logger.debug('Lembrete # %d removido com sucesso.', reminder_id)
    return {'mensagem': 'Lembrete removido', 'nome': reminder.name}


def __sent_email_payload(body: SendEmailSchema):
    '''
        Esta rota envia o payload de email para a api de envio de email.
    '''
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://api2:5000/prepare', json=body, headers=headers)
        response.raise_for_status()

        return response
    except requests.exceptions.RequestException as e:
        return {'message': e}, 500
    except Exception as error:
        logger.error(f'Erro ao validar e enviar email para lembrete: {error}')
        return {'mensagem': 'Ocorreu um erro ao enviar o email: %s', 'erro': error}, 404

def format_error_response(error_message:str, status:int) -> list:
    response = [
        {
            'ctx': {
                'error': error_message
            }
        }
    ]

    return response, status
