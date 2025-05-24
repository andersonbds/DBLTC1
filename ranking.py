# ranking.py
from datetime import datetime

class RankingManager:
    def __init__(self, db, bot, grupo_id):
        self.db = db
        self.bot = bot
        self.grupo_id = grupo_id

    def gerar_texto_ranking_top20(self):
        ranking = self.db.get_top_20_usuarios()
        if not ranking:
            return "Sem dados para exibir."
        texto = ""
        for i, user in enumerate(ranking, 1):
            texto += f"{i}. @{user['username']} - GH/s: {user['ghs']} - Minerado: {user['ltc']:.6f} LTC\n"
        return texto
