# App Bistrol - Análise de Cores

## Instalação do projeto:

Primeiro, copie toda a pasta do projeto para o servidor, depois, para instalar todas as dependências do projeto execute os seguintes comandos (uma linha por vez e alterando o path/para/projeto)

Para Windows:
```sh
cd ~/path/para/projeto

python -m venv venv

venv\Scripts\activate

python -m pip install --upgrade pip

pip install -r requirements.txt
```

Para Linux:
```sh
cd ~/path/para/projeto

python3 -m venv venv

source venv/bin/activate

python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

## Criar tabela de usuários no banco de dados:

Para criar a tabela de acordo com o software, crie através do comando

```SQL
CREATE TABLE usersAnaliseCores (
    id VARCHAR(255) NOT NULL UNIQUE PRIMARY KEY,
    email VARCHAR(510) NOT NULL UNIQUE,
    name TEXT NOT NULL,
    office VARCHAR(255) NOT NULL,
    password VARCHAR(300) NOT NULL,
    profile enum('ADMIN', 'COMUM') NOT NULL
);
```

## Configuração do projeto:

Para configurar o projeto, copie o arquivo .env.example e renomeie com o nome .env, depois insira os dados no arquivo.

``
DATABASE_HOST_BISTROL=
``
Inclua nele o host do banco de dados

``
DATABASE_PORT_BISTROL=
``
Inclua nele a porta do banco de dados

``
DATABASE_DATABASE_BISTROL=
``
Inclua nele o schema do banco de dados onde tem a tabela de usuários

``
DATABASE_USERNAME_BISTROL=
``
Inclua nele um username do banco de dados que tem acesso a ``SELECT`` e ``INSERT``

``
DATABASE_PASSWORD_BISTROL=
``
Inclua nele a senha do username incluso do banco de dados

``
DATABASE_TIMEOUT_BISTROL=
`` e 
``
DATABASE_CONNECTION_LIMIT_BISTROL=
``
Inclua neles os valores de timeout e tempo limite de conexão com o banco de dados

``
FLASK_SECRET_KEY_BISTROL=
``
Inclua nele a secret key para usar no flask, deve ser uma senha aleatória que será usada para criptografar as informações entre o usuário e o servidor, recomendo usar o ``gerar_keys.py`` onde é gerado uma senha aleatória de 24 dígitos para usar nessa senha secreta

``
ADMIN_USER_ID=
``
Inclua nele a id de um usuário admin para poder criar novos usuários, recomendo usar o ``gerar_keys.py`` para ter uma id aleatória e não interferir em outros usuários

``
ADMIN_USERNAME=
``
Inclua nele um username ou e-mail para o Admin

``
ADMIN_PASSWORD_HASH=
``
Inclua nele a senha para o Admin, a senha OBRIGATÓRIAMENTE DEVE SER CRIPTOGRAFADA, para isso, pode usar o ``gerar_password_hash_admin.py`` para criptografar uma senha que queira, e incluir no env

``
ADMIN_PROFILE=ADMIN
``
Inclua nele um o tipo do perfil para a conta, deve ser Obrigatóriamente ADMIN, como já está, pois somente dessa forma conseguirá registrar novos usuários

``
ADMIN_NAME=ADMIN
``
Inclua nele um o nome do usuário admin

``
ADMIN_OFFICE=ADMIN
``
Inclua nele um o cargo do usuário admin

## Após isso:

Prosseguir as configurações do servidor e domínio...