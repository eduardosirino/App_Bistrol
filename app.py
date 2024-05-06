from flask import Flask, render_template, request, jsonify
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder  # Esta é a linha a ser adicionada

# Caminho para o arquivo Excel
file_path = 'planilha/7533.xlsx'
data = pd.read_excel(file_path)

# Exibir as primeiras linhas para verificação
print(data.head())

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Receber dados do formulário
    data = request.json
    L = float(data['L'])
    A = float(data['A'])
    B = float(data['B'])

    # Simular dados - substituir por dados reais conforme necessário
    df = pd.DataFrame({
        'L*': [L, L+5, L-5],
        'a*': [A, A+5, A-5],
        'b*': [B, B+5, B-5],
        'Status': ['Aprovado', 'Reprovado', 'Aprovação Condicional']
    })

    # Criar gráfico com Plotly
    fig = px.scatter_3d(df, x='L*', y='a*', z='b*', color='Status')
    graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)

    return jsonify(graphJSON)

if __name__ == '__main__':
    app.run(debug=True)