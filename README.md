# Lembretes API

## Vídeo de demonstração das rotas e da aplicação:
    Link: https://youtu.be/EI1YREB8ulw

## Descrição do projeto:
      Este projeto faz parte das exigências da 1ª sprint da pós graduação 
    da PUC-Rio, curso Engenharia de Software, turma de julho de 2023.
    Neste projeto se encontra a API que possui como funcionalidades,
    além do CRUD básico (Create, Read/Retrieve, Update e Delete),
    algumas funcionalidades extras como envio de email, por exemplo.
    Este projeto é um MVP que é complementado pelo front-end que se
    encontra em outro repositório.

      A aplicação tem como objetivo evitar com que compromissos sejam
    esquecidos, permitindo que o usuário cadastre lembretes que podem ser
    facilmente criados, recuperados, editados ou removidos.

## Árvore de módulos. O sistema de pastas e arquivos do projeto está estruturado:
    Projeto
    |__ database
        |__ db.sqlite3
    |__ log
        |__ gunicorn.detailed.log
    |__ model
        |__ __init__.py
        |__ base.py
        |__ email_client.py
        |__ email.py
        |__ reminder.py
    |__ schemas
        |__ __init__.py
        |__ error.py
        |__ reminder.py
    |__ .env (não será commitado por questões de segurança)
    |__ app.py
    |__ logger.py
    |__ requirements.txt

## Como executar
Será necessário ter todas as libs python listadas no requirements.txt instaladas. 
Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para 
poder executar os comandos descritos abaixo.

É fortemente indicado o uso de ambientes virtuais do tipo virtualenv.

Passos para o ambiente virtual:

    #1 python3 -m pip install --user pipx
    #2 pipx install virtualenv
    #3 mkdir <diretorio_ambiente_virtual>
    #4 source <diretorio_ambiente_virtual>/bin/activate

Em qualquer dos cenários (ambiente virtual ou não), no diretório raiz da
aplicação instalar os requerimentos com:
 
 pip install -r requirements.txt

Para executar a API, executar:
$ flask run --host 0.0.0.0 --port 5000 --reload

Abra o http://localhost:5000/#/ no navegador para verificar o status da API em execução.

## Responsabilidades dos arquivos do projeto

## Pasta database:
  ### db.sqlite3
        Arquivo onde as operações no projeto são persistidas usando o banco
    de dados relacional SQLite.

  ### detailed.log
        Arquivo de log principal da aplicação, é um arquivo de texto 
    responsável por armazenar informações de debug, erros e também sucesso.

## Pasta model:
  ### \_\_init\_\_.py
      Responsável por inicializar o banco de dados e também por criá-lo na
    primeira execução do projeto.

  ### base.py
      Relacionado ao módulo SQLAlchemy, permite que operações no banco a
    partir de outras classes que não a base, sejam realizadas.

  ### email_client.py
      Responsável por enviar emails com as informações do lembrete.
    Atualmente, um email é enviado de forma automática quando o lembrete
    é criado e também quando o lembrete é editado / atualizado, caso o 
    usuário opte por isso.
      Também é possível enviar emails manualmente pela rota /send_email caso
    alguns requisitos sejam preenchidos. 

  ### email.py
      Responsável pela relação com a classe Reminder. Esta classe permite
    atribuir um email a um lembrete.

  ### reminder.py
      Model principal da aplicação. Responsável pela lógica de instanciar
    um modelo do tipo reminder. Também é responsável pela validação
    das regras de envio de um email de lembrete. 

## Pasta schemas:
  ### \_\_init\_\_.py
      Responsável por importar os schemas para a aplicação.

  ### error.py
      Responsável por definir o padrão das respostas de erro da aplicação.

  ### reminder.py
      Responsável por definir os padrões das respostas das rotas da aplicação,
    bem como validar o tipo de informação passada nas requisições.

## Pasta raiz da aplicação:
  ### .env
      Responsável pelas variáveis de ambiente do projeto. Por usualmente
    possuir informações sensíveis , não deve ser enviado para o 
    repositório.

  ### app.py
      Controlador da aplicação. Possui todas as rotas e lógica respectiva.

  ### logger.py
      Responsável pela configuração de logs da aplicação. Neste arquivo
    é possível customizar diversas opções de log, como o nível de disparo 
    de log, formatação dos logs e etc.

  ### README.md
      Este arquivo. Responsável por descrever a aplicação, seus objetivos
    e instruções para execução.

  ### requirements.txt
      Possui as bibliotecas / módulos necessários para a execução correta
      da aplicação.
