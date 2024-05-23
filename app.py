from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import uuid
import json
import glob
import logging
from logging.handlers import RotatingFileHandler
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


# Configuração dos Logs
logger = logging.getLogger('my_application')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
handler = RotatingFileHandler('log.log', maxBytes=5*1024*1024, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()

# Pasta dos arquivos
file_path = os.getenv('PATH_SPREADSHEET')

# Conexão com o banco de dados
db_config = {
    'host': os.getenv('DATABASE_HOST_BRISTOL'),
    'port': os.getenv('DATABASE_PORT_BRISTOL'),
    'user': os.getenv('DATABASE_USERNAME_BRISTOL'),
    'password': os.getenv('DATABASE_PASSWORD_BRISTOL'),
    'database': os.getenv('DATABASE_DATABASE_BRISTOL')
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY_BRISTOL', 'super-secret')

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
    admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH')
    if email == os.getenv('ADMIN_USERNAME') and admin_password_hash:
        if check_password_hash(admin_password_hash, password):
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
    user = cursor.fetchone()
    connection.close()

    if user:
        if check_password_hash(user[2], password):
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
        logger.error(f"Erro ao listar nomes de itens: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    try:
        request_data = request.json
        item_name = request_data['name']
        nome_field = os.getenv('NOME_FIELD', 'Nome')
        color_field = os.getenv('COLOR_FIELD', 'Observações')
        l_field = os.getenv('L_FIELD', 'L*')
        a_field = os.getenv('A_FIELD', 'a*')
        b_field = os.getenv('B_FIELD', 'b*')
        size_spreadsheet = int(os.getenv('SIZE_SPREADSHEET', 5))
        size_input = int(os.getenv('SIZE_INPUT', 10))

        item_files = glob.glob(os.path.join(file_path, item_name + '.*'))
        if not item_files:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        item_data = pd.read_excel(item_files[0])
        required_columns = [nome_field, color_field, l_field, a_field, b_field]
        if not all(col in item_data.columns for col in required_columns):
            return jsonify({'error': 'Colunas necessárias não encontradas nos dados'}), 500
        
        # Extrair valores da planilha
        L_planilha = item_data[l_field].values
        A_planilha = item_data[a_field].values
        B_planilha = item_data[b_field].values
        Nome_planilha = item_data[nome_field].values
        Observacoes_planilha = item_data[color_field].values

        def safe_float(value):
            try:
                return float(value) if value not in [None, '', ' '] else 0
            except ValueError:
                return 0

        L_input = safe_float(request_data.get('L'))
        A_input = safe_float(request_data.get('A'))
        B_input = safe_float(request_data.get('B'))

        # Mapear cores únicas para o campo Observações
        unique_observacoes = item_data[color_field].unique()
        distinct_colors = px.colors.qualitative.Alphabet
        color_map = {obs: distinct_colors[i % len(distinct_colors)] for i, obs in enumerate(unique_observacoes)}

        # Criar figura com pontos originais
        fig = go.Figure()

        # Adicionar pontos originais
        for obs in unique_observacoes:
            mask = Observacoes_planilha == obs
            fig.add_trace(go.Scatter3d(
                x=L_planilha[mask],
                y=A_planilha[mask],
                z=B_planilha[mask],
                mode='markers',
                marker=dict(
                    size=size_spreadsheet,
                    color=color_map[obs],
                    line=dict(width=2, color='DarkSlateGrey')
                ),
                text=[f'Nome: {nome}<br>Status: Dado Original<br>Observação: {obs}<br>L*: {L}<br>a*: {A}<br>b*: {B}' for L, A, B, nome in zip(L_planilha[mask], A_planilha[mask], B_planilha[mask], Nome_planilha[mask])],
                hoverinfo='text',
                name=obs
            ))

        # Adicionar ponto de entrada do usuário
        if L_input or A_input or B_input:
            fig.add_trace(go.Scatter3d(
                x=[L_input],
                y=[A_input],
                z=[B_input],
                mode='markers',
                marker=dict(
                    size=size_input,
                    color='rgb(0,0,0)',
                    line=dict(width=2, color='DarkSlateGrey')
                ),
                text=[f'Nome: Dado Usuário<br>Status: Entrada Usuário<br>Observação: Entrada Usuário<br>L*: {L_input}<br>a*: {A_input}<br>b*: {B_input}'],
                hoverinfo='text',
                name='Entrada Usuário'
            ))

        # Atualizar layout da figura
        fig.update_layout(
            autosize=True,
            scene=dict(
                xaxis_title=l_field,
                yaxis_title=a_field,
                zaxis_title=b_field
            ),
            margin=dict(l=10, r=10, t=10, b=13),
            legend_title_text=color_field,
            legend=dict(
                itemsizing='constant',
            )
        )

        return jsonify(json.dumps(fig, cls=PlotlyJSONEncoder))
    except Exception as e:
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
        logger.error(f"Erro ao trocar a senha: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    logger.info("Iniciando o servidor Flask")
    app.run(threaded=False, debug=False)
