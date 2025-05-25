# personagem_manager.py

from datetime import datetime, timedelta

class PersonagemManager:
    def __init__(self, db):
        self.db = db
        # Exemplo de personagens com poder de mineração (GH/s) e preço
        self.personagens = {
            1: {"nome": "Goku", "ghs": 10, "preco": 10},
            2: {"nome": "Vegeta", "ghs": 20, "preco": 20},
            3: {"nome": "Gohan", "ghs": 35, "preco": 35},
            4: {"nome": "Trunks", "ghs": 50, "preco": 50},
            5: {"nome": "Piccolo", "ghs": 75, "preco": 75},
            6: {"nome": "Freeza", "ghs": 100, "preco": 100},
            7: {"nome": "Cell", "ghs": 150, "preco": 150},
            8: {"nome": "Majin Boo", "ghs": 200, "preco": 200},
            9: {"nome": "Bills", "ghs": 250, "preco": 250},
            10: {"nome": "Whis", "ghs": 300, "preco": 300}
        }

    def obter_personagens_disponiveis(self):
        return self.personagens

    def get_nome_personagem(self, personagem_id):
        return self.personagens.get(personagem_id, {}).get("nome", "Desconhecido")

    def get_ghs_personagem(self, personagem_id):
        return self.personagens.get(personagem_id, {}).get("ghs", 0)

    def get_preco_personagem(self, personagem_id):
        return self.personagens.get(personagem_id, {}).get("preco", 0)

    def personagem_ativo(self, user_id, personagem_id):
        personagens = self.db.listar_personagens(user_id)
        for p_id, qtd, _, _ in personagens:
            if p_id == personagem_id and qtd > 0:
                return True
        return False

    def pode_minerar(self, user_id):
        personagens = self.db.listar_personagens(user_id)
        return len(personagens) > 0

    def calcular_ghs_total(self, user_id):
        total_ghs = 0
        personagens = self.db.listar_personagens(user_id)
        for personagem_id, quantidade, _, _ in personagens:
            ghs = self.get_ghs_personagem(personagem_id)
            total_ghs += ghs * quantidade
        return total_ghs

    def personagem_bateu_limite(self, user_id, personagem_id):
        preco = self.get_preco_personagem(personagem_id)
        limite = preco * 1.3
        personagens = self.db.listar_personagens(user_id)
        for pid, _, _, total_minerado in personagens:
            if pid == personagem_id:
                return total_minerado >= limite
        return False
