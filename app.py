from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import pandas as pd
import json
import glob
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import os
from dotenv import load_dotenv
import uuid
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

# Pasta dos arquivos
file_path = 'planilha'

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
    def __init__(self, id, username, profile, name, office):
        self.id = id
        self.username = username
        self.profile = profile
        self.name = name
        self.office = office

def get_db_connection():
    return mysql.connector.connect(**db_config)

def check_user_credentials(email, password):
    if email == os.getenv('ADMIN_USERNAME') and check_password_hash(os.getenv('ADMIN_PASSWORD_HASH'), password):
        return User(
            id=os.getenv('ADMIN_USER_ID'),
            username=os.getenv('ADMIN_USERNAME'),
            profile=os.getenv('ADMIN_PROFILE'),
            name=os.getenv('ADMIN_NAME'),
            office=os.getenv('ADMIN_OFFICE')
        )
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, email, password, profile, name, office FROM usersAnaliseCores WHERE email = %s", (email,))
    user  = cursor.fetchone()
    connection.close()

    if user and check_password_hash(user[2], password):
        return User(id=user[0], username=user[1], profile=user[3], name=user[4], office=user[5])
    return False

@login_manager.user_loader
def load_user(user_id):
    try:
        if user_id == os.getenv('ADMIN_USER_ID'):
            return User(
                id=os.getenv('ADMIN_USER_ID'),
                username=os.getenv('ADMIN_USERNAME'),
                profile=os.getenv('ADMIN_PROFILE'),
                name=os.getenv('ADMIN_NAME'),
                office=os.getenv('ADMIN_OFFICE')
            )
    
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, email, profile, name, office FROM usersAnaliseCores WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        connection.close()

        if user:
            return User(id=user[0], username=user[1], profile=user[2], name=user[3], office=user[4])
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
                login_user(user)
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
            name = request.form.get('name')
            office = request.form.get('office')
            password = request.form.get('password')
            profile = request.form.get('profile')

            if ' ' not in name:
                flash('Nome completo obrigatório!', 'error')
                return redirect(url_for('register'))
            
            if profile != 'COMUM' and profile != 'ADMIN':
                flash('Tipo do perfil obrigatório!', 'error')
                return redirect(url_for('register'))
            
            if not email or not password or not name or not office or not profile:
                flash('E-mail, nome, senha, cargo e perfil são obrigatórios!', 'error')
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usersAnaliseCores WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email já cadastrado!', 'error')
                conn.close()
                return redirect(url_for('register'))

            user_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO usersAnaliseCores (id, email, name, office, password, profile) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, email, name, office, hashed_password, profile))
            conn.commit()
            conn.close()
            flash('Usuário registrado com sucesso!', 'success')
            logger.info(f"Usuário {email} registrado com sucesso com ID {user_id}")
            return redirect(url_for('register'))

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
        file_names = [file.split('.')[0] for file in os.listdir(file_path) if file.endswith('.xlsx')]
        items = [{'Nome': name} for name in file_names]
        return jsonify(items)
    except Exception as e:
        print(e)
        logger.error(f"Erro ao listar nomes de itens: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    try:
        request_data = request.json
        item_name = request_data['name']

        item_files = glob.glob(os.path.join(file_path, item_name + '.*'))
        if not item_files:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        item_data = pd.read_excel(item_files[0])
        if 'Nome' not in item_data.columns:
            return jsonify({'error': 'Coluna "Nome" não encontrada nos dados'}), 500
        
        # Extrair valores da planilha
        L_planilha = item_data['L*'].values
        A_planilha = item_data['a*'].values
        B_planilha = item_data['b*'].values
        Nome_planilha = item_data['Nome'].values

        def safe_float(value):
            try:
                return float(value) if value not in [None, '', ' '] else 0
            except ValueError:
                return 0

        L_input = safe_float(request_data.get('L'))
        A_input = safe_float(request_data.get('A'))
        B_input = safe_float(request_data.get('B'))

        # DataFrame com os dados originais
        df_planilha = pd.DataFrame({
            'L*': L_planilha,
            'a*': A_planilha,
            'b*': B_planilha,
            'Status': ['Dado Original'] * len(L_planilha),
            'Nome': Nome_planilha
        })

        # DataFrame com os dados do usuário
        df_usuario = pd.DataFrame({
            'L*': [L_input],
            'a*': [A_input],
            'b*': [B_input],
            'Status': ['Entrada Usuário'],
            'Nome': ['Dado Usuário']
        })

        df_final = None

        # Combinar os DataFrames caso tenha valores inseridos pelo usuário
        df_final = pd.concat([df_planilha, df_usuario], ignore_index=True) if L_input or A_input or B_input else df_planilha

        fig = px.scatter_3d(df_final, x='L*', y='a*', z='b*', color='Status', color_discrete_map={'Dado Original': 'darkblue', 'Entrada Usuário': 'red'}, hover_data=['Status', 'Nome'])
        return jsonify(json.dumps(fig, cls=PlotlyJSONEncoder))
    except Exception as e:
        print(e)
        logger.error(f"Erro ao gerar gráfico: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.json
        current_password = data['currentPassword']
        new_password = data['newPassword']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM usersAnaliseCores WHERE id = %s", (current_user.id,))
        user_password = cursor.fetchone()
        connection.close()
        
        if not user_password:
            return jsonify({'success': False, 'message': 'Usuário não encontrado no banco de dados!'}), 400

        # Verificar se a senha atual está correta
        if not check_password_hash(user_password[0], current_password):
            return jsonify({'success': False, 'message': 'Senha atual incorreta!'}), 400

        # Atualizar a senha no banco de dados
        hashed_new_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE usersAnaliseCores SET password = %s WHERE id = %s", (hashed_new_password, current_user.id))
        connection.commit()
        connection.close()

        return jsonify({'success': True, 'message': 'Senha atualizada com sucesso!'})
    except Exception as e:
        print(e)
        logger.error(f"Erro ao trocar a senha: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    logger.info("Iniciando o servidor Flask")
    app.run(debug=True)
