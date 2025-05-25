from datetime import datetime, timedelta

class PersonagemManager:
    MINERACAO_MENSAL_PERCENTUAL = 1.0  # 1% ao mês

    PERSONAGENS = [
        {"id": 1, "nome": "Goku",       "preco_brl": 0.10,  "ghs": 100},
        {"id": 2, "nome": "Vegeta",     "preco_brl": 0.20,  "ghs": 200},
        {"id": 3, "nome": "Gohan",      "preco_brl": 0.40,  "ghs": 400},
        {"id": 4, "nome": "Piccolo",    "preco_brl": 0.80,  "ghs": 800},
        {"id": 5, "nome": "Trunks",     "preco_brl": 1.60,  "ghs": 1600},
        {"id": 6, "nome": "Frieza",     "preco_brl": 3.20,  "ghs": 3200},
        {"id": 7, "nome": "Cell",       "preco_brl": 6.40,  "ghs": 6400},
        {"id": 8, "nome": "Majin Buu",  "preco_brl": 12.80, "ghs": 12800},
        {"id": 9, "nome": "Broly",      "preco_brl": 25.60, "ghs": 25600},
        {"id": 10,"nome": "Beerus",     "preco_brl": 51.20, "ghs": 51200},
    ]

    def get_personagem_by_id(self, pid):
        for p in self.PERSONAGENS:
            if p["id"] == pid:
                return p
        return None

    def calcular_retorno_mensal(self, preco_brl):
        return preco_brl * (self.MINERACAO_MENSAL_PERCENTUAL / 100)

    def calcular_ghs_total(self, quantidade, ghs_unitario):
        return quantidade * ghs_unitario

    def pode_comprar(self, user_saldo, preco):
        return user_saldo >= preco

    def pode_minerar_mais(self, personagem_id, total_minerado, quantidade):
        personagem = self.get_personagem_by_id(personagem_id)
        if not personagem:
            return False
        preco_total = personagem["preco_brl"] * quantidade
        limite = preco_total * 1.3
        return total_minerado < limite

    def calcular_recompensa_intervalo(self, ghs, minutos=1):
        fator_minuto = self.MINERACAO_MENSAL_PERCENTUAL / 100 / 43200  # 43200 min = 30 dias
        recompensa = ghs * fator_minuto * minutos
        return round(recompensa, 8)

    def listar_personagens_texto(self):
        texto = ""
        for p in self.PERSONAGENS:
            texto += f"{p['id']} - {p['nome']} - Preço: R${p['preco_brl']:.2f} - Poder: {p['ghs']} GH/s\n"
        return texto

    def mostrar_loja(self, bot, chat_id, db):
        texto = "🛒 Loja de Personagens:\n\n" + self.listar_personagens_texto()
        texto += "\nPara comprar, envie /comprar <id> <quantidade>.\nExemplo: /comprar 1 2"
        bot.send_message(chat_id, texto)

    def mostrar_personagens_comprados(self, bot, chat_id, db):
        personagens = db.get_personagens_do_usuario(chat_id)
        if not personagens:
            bot.send_message(chat_id, "Você ainda não comprou nenhum personagem.")
            return
        texto = "🎮 Seus Personagens:\n\n"
        for p in personagens:
            texto += (f"{p['nome']} - Qtd: {p['quantidade']} - Minerado: R${p['total_minerado']:.2f}\n")
        bot.send_message(chat_id, texto)


# Funções globais para facilitar a importação
def mostrar_loja(bot, chat_id, db):
    pm = PersonagemManager()
    pm.mostrar_loja(bot, chat_id, db)

def mostrar_personagens_comprados(bot, chat_id, db):
    pm = PersonagemManager()
    pm.mostrar_personagens_comprados(bot, chat_id, db)
