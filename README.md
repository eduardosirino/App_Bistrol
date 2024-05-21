# App Bristol - Análise de Cores

Aplicação para análise de cores dos produtos da Bristol Parts

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

&nbsp;

## Criar tabela de usuários no banco de dados:

Para criar a tabela de acordo com o software, crie através do comando (para Mysql)

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
&nbsp;

## Configuração do projeto:

Para configurar o projeto, copie o arquivo .env.example e renomeie com o nome .env, depois insira os dados no arquivo.


`DATABASE_HOST_BRISTOL=` Inclua nele o host do banco de dados

`DATABASE_PORT_BRISTOL=` Inclua nele a porta do banco de dados

`DATABASE_DATABASE_BRISTOL=` Inclua nele o schema do banco de dados onde tem a tabela de usuários

`DATABASE_USERNAME_BRISTOL=` Inclua nele um username do banco de dados que tem acesso a ``SELECT`` e ``INSERT``

`DATABASE_PASSWORD_BRISTOL=` Inclua nele a senha do username incluso do banco de dados

`DATABASE_TIMEOUT_BRISTOL=` e `DATABASE_CONNECTION_LIMIT_BRISTOL=
` Inclua neles os valores de timeout e tempo limite de conexão com o banco de dados

&nbsp;

`FLASK_SECRET_KEY_BRISTOL=` Inclua nele a secret key para usar no flask, deve ser uma senha aleatória que será usada para criptografar as informações entre o usuário e o servidor, recomendo usar o `gerar_keys.py` onde é gerado uma senha aleatória de 24 dígitos para usar nessa senha secreta

&nbsp;

`ADMIN_USER_ID=` Inclua nele a id de um usuário admin para poder criar novos usuários, recomendo usar o ``gerar_keys.py`` para ter uma id aleatória e não interferir em outros usuários

`ADMIN_USERNAME=` Inclua nele um username ou e-mail para o Admin

`ADMIN_PASSWORD_HASH=` Inclua nele a senha para o Admin, a senha OBRIGATÓRIAMENTE DEVE SER CRIPTOGRAFADA, para isso, pode usar o ``gerar_password_hash_admin.py`` para criptografar uma senha que queira, e incluir no env

`ADMIN_PROFILE=ADMIN` Inclua nele um o tipo do perfil para a conta, deve ser Obrigatóriamente ADMIN, como já está, pois somente dessa forma conseguirá registrar novos usuários

`ADMIN_NAME=ADMIN` Inclua nele um o nome do usuário admin

`ADMIN_OFFICE=ADMIN` Inclua nele um o cargo do usuário admin 

&nbsp;

`PATH_SPREADSHEET=` Inclua nele o PATH onde está as planilhas

&nbsp;

`COLOR_FIELD=` Inclua nele um o campo das planilhas que será responsável pela cor

`NOME_FIELD=` Inclua nele um o campo das planilhas que será responsável pelo nome do item/ponto

`L_FIELD=` Inclua nele um o campo das planilhas que será responsável pelo L* original (será usado para coordenada do campo no eixo X)

`A_FIELD=` Inclua nele um o campo das planilhas que será responsável pelo a* original (será usado para coordenada do campo no eixo y)

`B_FIELD=` Inclua nele um o campo das planilhas que será responsável pelo b* original (será usado para coordenada do campo no eixo Z)

`SIZE_SPREADSHEET=` Inclua nele um o tamanho para o ponto gerado pela planilha

`SIZE_INPUT=` Inclua nele um o tamanho para o ponto gerado pelo input, deve ser maior que o `SIZE_SPREADSHEET=` para um maior destaque

## Após isso:

Prosseguir as configurações do servidor e domínio...