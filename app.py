from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Configuração dos Logs
logger = logging.getLogger('my_application')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
handler = RotatingFileHandler('log.log', maxBytes=5*1024*1024, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()

# Coleta dos dados da planilha
try:
    logger.info("Carregando dados da planilha")
    file_path = 'planilha/7533.xlsx'
    data = pd.read_excel(file_path, header=0)
    data.columns = [col.strip() for col in data.columns]
    data = data.dropna(how='all').fillna(0)
    logger.info("Dados carregados com sucesso")
except Exception as e:
    logger.error(f"Erro ao carregar dados da planilha: {e}")

# Conexão com o banco de dados
db_config = {
    'host': os.getenv('DATABASE_HOST_BISTROL'),
    'port': os.getenv('DATABASE_PORT_BISTROL'),
    'user': os.getenv('DATABASE_USERNAME_BISTROL'),
    'password': os.getenv('DATABASE_PASSWORD_BISTROL'),
    'database': os.getenv('DATABASE_DATABASE_BISTROL')
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY_BISTROL', 'super-secret')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página!'

class User(UserMixin):
    def __init__(self, id, username, profile):
        self.id = id
        self.username = username
        self.profile = profile

def get_db_connection():
    return mysql.connector.connect(**db_config)

def check_user_credentials(email, password):
    if email == os.getenv('ADMIN_USERNAME') and check_password_hash(os.getenv('ADMIN_PASSWORD_HASH'), password):
        return (os.getenv('ADMIN_USER_ID'), os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD_HASH'), os.getenv('ADMIN_PROFILE'))
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user_pass = cursor.fetchone()
    connection.close()
    if user_pass and check_password_hash(user_pass[2], password):
        return user_pass
    return False

@login_manager.user_loader
def load_user(user_id):
    try:
        if user_id == os.getenv('ADMIN_USER_ID'):
            return User(id=os.getenv('ADMIN_USER_ID'), username=os.getenv('ADMIN_USERNAME'), profile=os.getenv('ADMIN_PROFILE'))
    
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        connection.close()
        if user:
            return User(id=user[0], username=user[1], profile=user[3])
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar usuário: {e}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = check_user_credentials(username, password)
            if user:
                user_obj = User(id=user[0], username=user[1], profile=user[3])
                login_user(user_obj)
                return redirect(url_for('index'))
            else:
                flash('Usuário ou senha inválidos', 'error')
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Erro durante o login: {e}")
        flash('Erro interno', 'error')
        return render_template('login.html'), 500

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Erro durante o logout: {e}")
        return redirect(url_for('login')), 500

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    try:
        if current_user.profile != 'ADMIN':
            return render_template('404.html'), 404
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                flash('E-mail e senha são obrigatórios!', 'error')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email já cadastrado!', 'error')
                conn.close()
                return redirect(url_for('register'))

            cursor.execute("INSERT INTO users (email, password, profile) VALUES (%s, %s, %s)", (email, hashed_password, 'COMUM'))
            conn.commit()
            conn.close()
            flash('Usuário registrado com sucesso!', 'success')
            logger.info(f"Usuário {email} registrado com sucesso")
            return redirect(url_for('login'))

        return render_template('register.html')
    except Exception as e:
        logger.error(f"Erro durante o registro: {e}")
        flash('Erro interno', 'error')
        return render_template('register.html'), 500
    

@app.route('/')
@login_required
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Erro ao acessar a página inicial: {e}")
        return render_template('404.html'), 500

@app.route('/item-names')
@login_required
def item_names():
    try:
        items = data[['Nome', 'L*', 'a*', 'b*']].drop_duplicates().to_dict(orient='records')
        return jsonify(items)
    except Exception as e:
        logger.error(f"Erro ao listar nomes de itens: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    try:
        request_data = request.json
        item_name = request_data['name']

        # Buscar dados na planilha pelo nome
        item_data = data[data['Nome'] == item_name]

        if item_data.empty:
            return jsonify({'error': 'Item não encontrado'}), 404

        # Extrair valores da planilha
        L_planilha = item_data['L*'].values[0]
        A_planilha = item_data['a*'].values[0]
        B_planilha = item_data['b*'].values[0]

        # Verificar e converter os valores recebidos ou usar valores da planilha se vazios ou inválidos
        def safe_float(value, default):
            try:
                return float(value) if value not in [None, '', ' '] else default
            except ValueError:
                return default

        L_input = safe_float(request_data.get('L'), L_planilha)
        A_input = safe_float(request_data.get('A'), A_planilha)
        B_input = safe_float(request_data.get('B'), B_planilha)

        df = pd.DataFrame({
            'L*': [L_planilha, L_input],
            'a*': [A_planilha, A_input],
            'b*': [B_planilha, B_input],
            'Status': ['Dado Original', 'Entrada Usuário']
        })

        fig = px.scatter_3d(df, x='L*', y='a*', z='b*', color='Status')
        return jsonify(json.dumps(fig, cls=PlotlyJSONEncoder))
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    logger.info("Iniciando o servidor Flask")
    app.run(debug=False)
