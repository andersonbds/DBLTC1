import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path='db_ltc.sqlite'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            saldo REAL DEFAULT 0,
            indicacao_id INTEGER,
            total_investido REAL DEFAULT 0
        )
        """)
        self.cursor.execute("""
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
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tipo TEXT,
            valor REAL,
            data TEXT
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tipo TEXT, -- 'pix' ou 'ltc'
            valor REAL,
            chave TEXT, -- chave pix ou endereço LTC
            status TEXT DEFAULT 'pendente', -- 'pendente', 'aprovado', 'rejeitado'
            data TEXT
        )
        """)
        self.conn.commit()

    # Usuários
    def criar_usuario(self, user_id, username, indicacao_id=None):
        self.cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
        if self.cursor.fetchone():
            return False
        self.cursor.execute(
            "INSERT INTO users (id, username, indicacao_id) VALUES (?, ?, ?)",
            (user_id, username, indicacao_id)
        )
        self.conn.commit()
        return True

    def criar_usuario_se_nao_existir(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users (id, username) VALUES (?, ?)",
                (user_id, None)
            )
            self.conn.commit()

    def atualizar_saldo(self, user_id, valor):
        self.cursor.execute("UPDATE users SET saldo = saldo + ? WHERE id = ?", (valor, user_id))
        self.conn.commit()

    def obter_saldo(self, user_id):
        self.cursor.execute("SELECT saldo FROM users WHERE id = ?", (user_id,))
        res = self.cursor.fetchone()
        return res[0] if res else 0

    def adicionar_investimento(self, user_id, valor):
        self.cursor.execute("UPDATE users SET total_investido = total_investido + ? WHERE id = ?", (valor, user_id))
        self.conn.commit()

    def obter_usuario(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def obter_total_investido(self, user_id):
        self.cursor.execute("SELECT total_investido FROM users WHERE id = ?", (user_id,))
        res = self.cursor.fetchone()
        return res[0] if res else 0

    # Personagens
    def comprar_personagem(self, user_id, personagem_id, preco):
        data_compra = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Verifica se personagem já existe para o usuário
        self.cursor.execute("SELECT quantidade FROM personagens WHERE user_id = ? AND personagem_id = ?", (user_id, personagem_id))
        res = self.cursor.fetchone()
        if res:
            # Incrementa quantidade e atualiza data da compra para a última
            self.cursor.execute(
                "UPDATE personagens SET quantidade = quantidade + 1, data_compra = ? WHERE user_id = ? AND personagem_id = ?",
                (data_compra, user_id, personagem_id)
            )
        else:
            # Insere novo registro
            self.cursor.execute(
                "INSERT INTO personagens (user_id, personagem_id, quantidade, data_compra) VALUES (?, ?, ?, ?)",
                (user_id, personagem_id, 1, data_compra)
            )
        self.conn.commit()

    def listar_personagens(self, user_id):
        self.cursor.execute("SELECT personagem_id, quantidade, saldo_minerado, total_minerado FROM personagens WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def atualizar_mineracao(self, user_id, personagem_id, saldo_incremento, total_incremento):
        self.cursor.execute("""
        UPDATE personagens
        SET saldo_minerado = saldo_minerado + ?, total_minerado = total_minerado + ?
        WHERE user_id = ? AND personagem_id = ?
        """, (saldo_incremento, total_incremento, user_id, personagem_id))
        self.conn.commit()

    def resetar_saldo_minerado(self, user_id, personagem_id):
        self.cursor.execute("UPDATE personagens SET saldo_minerado = 0 WHERE user_id = ? AND personagem_id = ?", (user_id, personagem_id))
        self.conn.commit()

    # Transações
    def registrar_transacao(self, user_id, tipo, valor):
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO transacoes (user_id, tipo, valor, data) VALUES (?, ?, ?, ?)", (user_id, tipo, valor, data))
        self.conn.commit()

    def obter_historico(self, user_id):
        self.cursor.execute("SELECT tipo, valor, data FROM transacoes WHERE user_id = ? ORDER BY data DESC LIMIT 50", (user_id,))
        return self.cursor.fetchall()

    # Estatísticas
    def somar_depositos(self):
        self.cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'deposito'")
        res = self.cursor.fetchone()
        return res[0] if res and res[0] else 0.0

    def somar_saques(self):
        self.cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'saque'")
        res = self.cursor.fetchone()
        return res[0] if res and res[0] else 0.0

    def contar_pagamentos_pendentes(self):
        self.cursor.execute("SELECT COUNT(*) FROM pagamentos WHERE status = 'pendente'")
        res = self.cursor.fetchone()
        return res[0] if res else 0
     def listar_usuarios(self):
        cursor = self.conn.execute("SELECT id FROM users")
        return [row[0] for row in cursor.fetchall()]
