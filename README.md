# Lembretes api1

## Vídeo de demonstração da aplicação em funcionamento:
    https://youtu.be/yPVw6CfYXRI

## Link do fluxograma do projeto:
    https://www.figma.com/board/QQJ05XsjOiAJMTkwIXN6FQ/Fluxograma-Aplica%C3%A7%C3%A3o-Reminder-Web-2.0?node-id=0-1&t=ULFW6Rmb2CMpkqWs-1

## Descrição do projeto:
   Este repositório faz parte das exigências da sprint Arquitetura de Software
  da pós graduação da PUC-Rio, curso Engenharia de Software, turma de julho de 2023.
  Neste repositório se encontra a API que funciona como gateway da aplicação e
  possui como funcionalidades: o CRUD (Create, Read/Retrieve, Update e Delete)
  de lembretes, criação de usuário usando bcrypt para armazenar a senha, validação
  de username e senha de usuário, além de relacionamento com a tabela emails,
  bem como se comunicar com a api2, responsável pelo envio de emails, atuando assim
  como gateway da aplicação (são mais de 12 rotas).

   Este repositório possui também o arquivo de orquestração de containers, sendo
  assim o componente principal do sistema.

   A aplicação consiste basicamente em permitir que um usuário cadastre
  lembretes que podem ser facilmente criados, recuperados, editados, removidos
  e enviados à qualquer email.

  As linguagens usadas são Python 3.x, SqLite.

## Árvore de módulos. O sistema de pastas e arquivos do projeto está estruturado:
    api1
    |__ database
        |__ db.sqlite3
    |__ log
        |__ detailed.log
        |__ detailed.log1 ... .log5
    |__ model
        |__ __init__.py
        |__ base.py
        |__ email.py
        |__ reminder.py
        |__ user.py
    |__ schemas
        |__ __init__.py
        |__ error.py
        |__ reminder.py
        |__ user.py
        |__ send_email.py
    |__ .gitignore
    |__ app.py
    |__ docker-compose.yml
    |__ Dockerfile
    |__ logger.py
    |__ README.md
    |__ requirements.txt

## Como executar

    #1 git clone git@github.com:AttilaBS/MVP-Arquitetura-Software-1-front.git
    #2 git clone https://github.com/AttilaBS/MVP-Arquitetura-Software-2-api-1
    #3 git clone https://github.com/AttilaBS/MVP-Arquitetura-Software-3-api-2
      OBS.:Os repositórios devem estar na seguinte hierarquia de pastas:
      Pasta-raiz
          |__ frontend
          |__ api1
          |__ api2
    #4 na pasta raiz do repositório presente (api1), se encontra o docker-compose.
    Digitar: docker compose up --build
     Obs.: Pode ser necessário executar o comando com sudo
    #5 aguardar o final do build dos containers
    #6 criar um arquivo .env na raiz da aplicação api2 e preencher as informações
     passadas via mensagem no momento de postagem deste MVP.
    #7 acessar o frontend pela url: http://localhost:3000

## Responsabilidades dos arquivos do componente

## Pasta database:
  ### db.sqlite3
   Arquivo onde as operações no projeto são persistidas usando o banco
  de dados relacional SQLite.

## Pasta log:
  ### detailed.log
   Arquivo de log principal da aplicação, é um arquivo de texto
  responsável por armazenar informações de debug, erros e também sucesso
  mais genéricas.

  ### detailed.log1 ... .log5
   Arquivos de log com mais detalhes, com trace mais completo. Importantes
  para debug mais aprofundado ou então backup dos logs.

## Pasta model:
  ### \_\_init\_\_.py
   Responsável por importar a lib de banco de dados, inicializá-lo,
  também por criá-lo na primeira execução do projeto e importar os demais
  models da aplicação.

  ### base.py
   Importa e inicializa a classe base que será usada nas operações no banco
  de dados.

  ### email.py
   Responsável pela relação com a classe Reminder. Esta classe permite
  atribuir um email a um lembrete.

  ### reminder.py
   Model principal da aplicação. Responsável pela lógica referente aos
  models do tipo reminder.

  ### user.py
   Responsável pela criação e validação dos usuários criados na aplicação para
  acesso das rotas protegidas.

## Pasta schemas:
  ### \_\_init\_\_.py
   Responsável por importar os schemas para a aplicação.

  ### error.py
   Responsável por definir o padrão das respostas de erro da aplicação.

  ### reminder.py
   Responsável por definir os padrões das respostas das rotas da aplicação,
  bem como validar o tipo de informação passada nas requisições.

  ### user.py
   Responsável por definir os padrões de requisições e respostas das rotas
  relativas à criação e validação de usuários.

  ### send_email.py
   Responsável por definir os padrões de requisições e respostas das rotas
  relativas ao envio de emails.

## Pasta raiz da aplicação:
  ### .gitignore
   Responsável por adicionar arquivos e pastas que serão ignorados
  pelo sistema de versionamento do repositório.

  ### app.py
   Controlador da aplicação. Possui todas as rotas e lógica respectiva
  deste repositório, bem como responsável pelas rotas de comunicação
  com os demais serviços.

  ### docker-compose.yml
   Arquivo de orquestração de containers do docker. Responsável pela comunicação
  entre os serviços da aplicação, bem como funcionamento deles.

  ### Dockerfile
   Arquivo de configuração docker, específico para o serviço api1.

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

  ### Sobre a API externa consumida e envio de emails pela aplicação
   A API externa consumida é da Google, com a funcionalidade de envio de
  emails. Para que funcione corretamente, é necessário criar e preencher
  o arquivo .env na raiz do repositório da api2 com as informações que serão
  colocadas no momento de postagem deste MVP.

  A rota que acessa a API externa (por meio do serviço api2), é:
  __sent_email_payload(payload), chamada nas rotas de criação e atualização
  de lembretes, quando o usuário opta pelo envio de email (opção enviar email).

  ### Teste das rotas das apis.
   Todas as rotas principais das APIs podem ser testadas via frontend, mas é
  possível também testar as rotas das APIs via Swagger ou similares, por meio
  da url: 'http://localhost:5000'.
