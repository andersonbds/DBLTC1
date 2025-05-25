import sqlite3
from threading import Lock

class Database:
    def __init__(self, db_path='dbltc.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = Lock()
        self._criar_tabelas()

    def _criar_tabelas(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    saldo_brl REAL DEFAULT 0,
                    saldo_ltc REAL DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personagens_ativos (
                    user_id INTEGER,
                    personagem_id INTEGER,
                    quantidade INTEGER DEFAULT 1,
                    minerado_ltc REAL DEFAULT 0,
                    total_minerado REAL DEFAULT 0,
                    PRIMARY KEY(user_id, personagem_id),
                    FOREIGN KEY(user_id) REFERENCES usuarios(user_id)
                )
            ''')
            self.conn.commit()

    def user_exists(self, user_id):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM usuarios WHERE user_id = ?", (user_id,))
            return cursor.fetchone() is not None

    def add_user(self, user_id, username):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO usuarios(user_id, username, saldo_brl, saldo_ltc) VALUES (?, ?, 0, 0)",
                           (user_id, username))
            self.conn.commit()

    def get_saldo(self, user_id):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT saldo_brl, saldo_ltc FROM usuarios WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {'brl': row[0], 'ltc': row[1]}
            else:
                return {'brl': 0.0, 'ltc': 0.0}

    def deduzir_saldo_brl(self, user_id, valor):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT saldo_brl FROM usuarios WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row is None or row[0] < valor:
                return False
            novo_saldo = row[0] - valor
            cursor.execute("UPDATE usuarios SET saldo_brl = ? WHERE user_id = ?", (novo_saldo, user_id))
            self.conn.commit()
            return True

    def creditar_saldo_ltc(self, user_id, valor):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT saldo_ltc FROM usuarios WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                return False
            novo_saldo = row[0] + valor
            cursor.execute("UPDATE usuarios SET saldo_ltc = ? WHERE user_id = ?", (novo_saldo, user_id))
            self.conn.commit()
            return True

    def adicionar_personagem_usuario(self, user_id, personagem_id):
        with self.lock:
            cursor = self.conn.cursor()
            # Verifica se personagem já ativo, soma quantidade ou insere novo
            cursor.execute("SELECT quantidade FROM personagens_ativos WHERE user_id = ? AND personagem_id = ?",
                           (user_id, personagem_id))
            row = cursor.fetchone()
            if row:
                nova_quantidade = row[0] + 1
                cursor.execute("UPDATE personagens_ativos SET quantidade = ? WHERE user_id = ? AND personagem_id = ?",
                               (nova_quantidade, user_id, personagem_id))
            else:
                cursor.execute("INSERT INTO personagens_ativos(user_id, personagem_id, quantidade, minerado_ltc, total_minerado) VALUES (?, ?, 1, 0, 0)",
                               (user_id, personagem_id))
            self.conn.commit()

    def listar_personagens_ativos(self, user_id):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT personagem_id, quantidade, minerado_ltc, total_minerado FROM personagens_ativos WHERE user_id = ?", (user_id,))
            return cursor.fetchall()

    def resetar_saldo_minerado(self, user_id, personagem_id):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE personagens_ativos SET minerado_ltc = 0 WHERE user_id = ? AND personagem_id = ?",
                           (user_id, personagem_id))
            self.conn.commit()
