import sqlite3
from datetime import datetime

conn = sqlite3.connect('db_ltc.sqlite', check_same_thread=False)
cursor = conn.cursor()

def criar_tabelas():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        saldo REAL DEFAULT 0,
        indicacao_id INTEGER,
        total_investido REAL DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        personagem_id INTEGER,
        quantidade INTEGER DEFAULT 1,
        saldo_minerado REAL DEFAULT 0,
        total_minerado REAL DEFAULT 0,
        data_compra TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tipo TEXT,
        valor REAL,
        data TEXT
    )
    """)
    conn.commit()

criar_tabelas()

# USUÁRIOS
def criar_usuario(user_id, username, indicacao_id=None):
    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO users (id, username, indicacao_id) VALUES (?, ?, ?)", (user_id, username, indicacao_id))
    conn.commit()
    return True

def atualizar_saldo(user_id, valor):
    cursor.execute("UPDATE users SET saldo = saldo + ? WHERE id = ?", (valor, user_id))
    conn.commit()

def obter_saldo(user_id):
    cursor.execute("SELECT saldo FROM users WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 0

def adicionar_investimento(user_id, valor):
    cursor.execute("UPDATE users SET total_investido = total_investido + ? WHERE id = ?", (valor, user_id))
    conn.commit()

def obter_usuario(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# PERSONAGENS
def comprar_personagem(user_id, personagem_id, preco):
    data_compra = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT quantidade FROM personagens WHERE user_id = ? AND personagem_id = ?", (user_id, personagem_id))
    res = cursor.fetchone()
    if res:
        cursor.execute("UPDATE personagens SET quantidade = quantidade + 1, data_compra = ? WHERE user_id = ? AND personagem_id = ?", (data_compra, user_id, personagem_id))
    else:
        cursor.execute("INSERT INTO personagens (user_id, personagem_id, quantidade, data_compra) VALUES (?, ?, ?, ?)", (user_id, personagem_id, 1, data_compra))
    conn.commit()

def listar_personagens(user_id):
    cursor.execute("SELECT personagem_id, quantidade, saldo_minerado, total_minerado FROM personagens WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def atualizar_mineracao(user_id, personagem_id, saldo_incremento, total_incremento):
    cursor.execute("""
    UPDATE personagens
    SET saldo_minerado = saldo_minerado + ?, total_minerado = total_minerado + ?
    WHERE user_id = ? AND personagem_id = ?
    """, (saldo_incremento, total_incremento, user_id, personagem_id))
    conn.commit()

def resetar_saldo_minerado(user_id, personagem_id):
    cursor.execute("UPDATE personagens SET saldo_minerado = 0 WHERE user_id = ? AND personagem_id = ?", (user_id, personagem_id))
    conn.commit()

# TRANSAÇÕES
def registrar_transacao(user_id, tipo, valor):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO transacoes (user_id, tipo, valor, data) VALUES (?, ?, ?, ?)", (user_id, tipo, valor, data))
    conn.commit()

def obter_historico(user_id):
    cursor.execute("SELECT tipo, valor, data FROM transacoes WHERE user_id = ? ORDER BY data DESC LIMIT 50", (user_id,))
    return cursor.fetchall()
