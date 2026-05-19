from flask import Flask, request, jsonify
import random
import pyodbc

app = Flask(__name__)

CONNECTION_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=sql-server-cp3-rm559810-switzerlandnorth.database.windows.net,1433;"
    "Database=db-dimdim;"
    "Uid=user-dimdim;"
    "Pwd=Fiap@2tdspm;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

def get_db_connection():
    return pyodbc.connect(CONNECTION_STRING)

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "Empate"
    elif (
        (user_choice == "pedra" and computer_choice == "tesoura") or
        (user_choice == "tesoura" and computer_choice == "papel") or
        (user_choice == "papel" and computer_choice == "pedra")
    ):
        return "Você"
    else:
        return "Computador"

@app.route('/')
def index():
    return "Bem-vindo ao Jogo de Jokenpô com Banco de Dados! Use as rotas de /jogadores ou /play."

@app.route('/jogadores', methods=['POST'])
def create_user():
    """Cria um novo jogador (CREATE)"""
    data = request.json or {}
    nome = data.get('nome_jogador', 'Jogador Anonimo')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    

    cursor.execute(
        "INSERT INTO tb_jogadores (nome_jogador) OUTPUT INSERTED.id_jogador VALUES (?);", 
        (nome,)
    )
    id_jogador = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'id_jogador': id_jogador, 'nome_jogador': nome, 'message': 'Jogador criado com sucesso!'}), 201

@app.route('/jogadores/<int:id_jogador>', methods=['GET'])
def get_user(id_jogador):
    """Busca dados de um jogador (READ)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_jogador, nome_jogador, dt_criacao FROM tb_jogadores WHERE id_jogador = ?;", (id_jogador,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not row:
        return jsonify({'error': 'Jogador não encontrado.'}), 404
        
    return jsonify({
        'id_jogador': row[0],
        'nome_jogador': row[1],
        'dt_criacao': row[2].strftime('%d/%m/%Y %H:%M') if row[2] else None
    })

@app.route('/jogadores/<int:id_jogador>', methods=['PUT'])
def update_user(id_jogador):
    """Atualiza o nome do jogador (UPDATE)"""
    data = request.json or {}
    novo_nome = data.get('nome_jogador')
    
    if not novo_nome:
        return jsonify({'error': 'O campo nome_jogador é obrigatório.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tb_jogadores SET nome_jogador = ? WHERE id_jogador = ?;", (novo_nome, id_jogador))
    updated = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    
    if updated == 0:
        return jsonify({'error': 'Jogador não encontrado.'}), 404
        
    return jsonify({'message': 'Jogador atualizado com sucesso!'})

@app.route('/jogadores/<int:id_jogador>', methods=['DELETE'])
def delete_user(id_jogador):
    """Deleta o jogador e limpa histórico via CASCADE (DELETE)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tb_jogadores WHERE id_jogador = ?;", (id_jogador,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    
    if deleted == 0:
        return jsonify({'error': 'Jogador não encontrado.'}), 404
        
    return jsonify({'message': 'Jogador e histórico de partidas removidos com sucesso!'})



@app.route('/play', methods=['POST'])
def play_game():
    """Roda uma rodada do jogo e salva na tabela tb_partidas"""
    data = request.json or {}
    id_jogador = data.get('id_jogador')
    user_choice = data.get('choice', '').lower()

    if not id_jogador:
        return jsonify({'error': 'O campo id_jogador é obrigatório para registrar a partida.'}), 400

    if user_choice not in ['pedra', 'papel', 'tesoura']:
        return jsonify({'error': 'Escolha inválida. Escolha entre pedra, papel ou tesoura.'}), 400
    
    computer_choice = random.choice(['pedra', 'papel', 'tesoura'])
    result = determine_winner(user_choice, computer_choice)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO tb_partidas (id_jogador, escolha_jogador, escolha_computador, resultado) 
               VALUES (?, ?, ?, ?);""",
            (id_jogador, user_choice, computer_choice, result)
        )
        conn.commit()
    except pyodbc.IntegrityError:
        cursor.close()
        conn.close()
        return jsonify({'error': f'O id_jogador {id_jogador} não existe no banco de dados.'}), 400

    
    cursor.execute("SELECT COUNT(*) FROM tb_partidas WHERE id_jogador = ? AND resultado = 'Você';", (id_jogador,))
    user_score = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_partidas WHERE id_jogador = ? AND resultado = 'Computador';", (id_jogador,))
    computer_score = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tb_partidas WHERE id_jogador = ?;", (id_jogador,))
    rounds = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return jsonify({
        'result': result,
        'computer_choice': computer_choice,
        'score': {
            'user': user_score,
            'computer': computer_score,
            'rounds': rounds
        }
    })

@app.route('/jogadores/<int:id_jogador>/partidas', methods=['GET'])
def get_game_history(id_jogador):
    """Retorna o histórico completo de partidas de um jogador (READ do Histórico)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id_partida, escolha_jogador, escolha_computador, resultado, dt_partida 
           FROM tb_partidas WHERE id_jogador = ? ORDER BY dt_partida DESC;""", 
        (id_jogador,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    historico = []
    for row in rows:
        historico.append({
            'id_partida': row[0],
            'escolha_jogador': row[1],
            'escolha_computador': row[2],
            'resultado': row[3],
            'dt_partida': row[4].strftime('%d/%m/%Y %H:%M') if row[4] else None
        })
        
    return jsonify(historico)

@app.route('/reset', methods=['POST'])
def reset_score():
    """Reseta o placar apagando todas as rodadas de um jogador específico (DELETE do Histórico)"""
    data = request.json or {}
    id_jogador = data.get('id_jogador')
    
    if not id_jogador:
        return jsonify({'error': 'O campo id_jogador é obrigatório para resetar o placar.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tb_partidas WHERE id_jogador = ?;", (id_jogador,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': f'Placar do jogador {id_jogador} totalmente resetado!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
