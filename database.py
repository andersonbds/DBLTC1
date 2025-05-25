import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path='dbltc.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                saldo_ltc REAL DEFAULT 0,
                saldo_brl REAL DEFAULT 0,
                criado_em TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personagens_ativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                personagem_id INTEGER,
                quantidade INTEGER DEFAULT 1,
                minerado_total REAL DEFAULT 0,
                minerado_saldo REAL DEFAULT 0,
                comprado_em TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        self.conn.commit()

    def user_exists(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
        return cursor.fetchone() is not None

    def add_user(self, user_id, username):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, criado_em) VALUES (?, ?, ?)",
                       (user_id, username, datetime.utcnow().isoformat()))
        self.conn.commit()

    def get_saldo(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT saldo_ltc, saldo_brl FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {"ltc": row[0], "brl": row[1]}
        else:
            return {"ltc": 0, "brl": 0}

    def listar_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, username FROM users")
        usuarios = cursor.fetchall()
        return [{"user_id": u[0], "username": u[1]} for u in usuarios]

    def listar_personagens_ativos(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT personagem_id, quantidade, minerado_saldo, minerado_total
            FROM personagens_ativos
            WHERE user_id=?
        """, (user_id,))
        return cursor.fetchall()

    def atualizar_mineracao(self, user_id, personagem_id, minerado_saldo_incremento, minerado_total_incremento):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE personagens_ativos
            SET minerado_saldo = minerado_saldo + ?,
                minerado_total = minerado_total + ?
            WHERE user_id=? AND personagem_id=?
        """, (minerado_saldo_incremento, minerado_total_incremento, user_id, personagem_id))
        self.conn.commit()

    def resetar_saldo_minerado(self, user_id, personagem_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE personagens_ativos
            SET minerado_saldo = 0
            WHERE user_id=? AND personagem_id=?
        """, (user_id, personagem_id))
        self.conn.commit()

    def get_top_20_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT u.username, SUM(p.quantidade * pi.gh_s) as gh_s, u.saldo_ltc as ltc
            FROM users u
            LEFT JOIN personagens_ativos p ON u.user_id = p.user_id
            LEFT JOIN (
                SELECT 1 as personagem_id, 1000 as gh_s UNION ALL
                SELECT 2, 2500 UNION ALL
                SELECT 3, 4000 UNION ALL
                SELECT 4, 6000 UNION ALL
                SELECT 5, 8000
            ) pi ON p.personagem_id = pi.personagem_id
            GROUP BY u.user_id
            ORDER BY gh_s DESC
            LIMIT 20
        """)
        rows = cursor.fetchall()
        return [{"username": r[0], "ghs": r[1] or 0, "ltc": r[2] or 0} for r in rows]

    # Adicione outros métodos conforme suas necessidades
