# personagem_manager.py

class PersonagemManager:
    def __init__(self, db):
        self.db = db
        # Defina os valores e GH/s de cada personagem aqui
        # Exemplo: personagem_id: (preco, gh_s)
        self.personagens_info = {
            1: (100, 1000),
            2: (200, 2500),
            3: (300, 4000),
            4: (400, 6000),
            5: (500, 8000),
            # adicione mais conforme necessário
        }
        # Limite de retorno de investimento (130%)
        self.limite_retorno = 1.3

    def pode_minerar(self, user_id):
        # Usuário pode minerar se tiver pelo menos um personagem
        personagens = self.db.listar_personagens(user_id)
        return len(personagens) > 0

    def calcular_ghs_total(self, user_id):
        personagens = self.db.listar_personagens(user_id)
        total_ghs = 0
        for p in personagens:
            personagem_id = p[0]
            quantidade = p[1]
            info = self.personagens_info.get(personagem_id)
            if info:
                _, gh_s = info
                total_ghs += gh_s * quantidade
        return total_ghs

    def personagem_bateu_limite(self, user_id, personagem_id):
        # Verifica se personagem ultrapassou 130% do valor investido
        info = self.personagens_info.get(personagem_id)
        if not info:
            return True  # personagem desconhecido não pode minerar

        preco, _ = info

        # Obtem total minerado do personagem
        personagens = self.db.listar_personagens(user_id)
        for p in personagens:
            pid = p[0]
            total_minerado = p[3]
            if pid == personagem_id:
                # Se total minerado >= 130% do preço, bateu limite
                if total_minerado >= preco * self.limite_retorno:
                    return True
                else:
                    return False
        return True  # se personagem não encontrado, bloqueia

    def registrar_mineracao(self, user_id, personagem_id, valor_minerado):
        # Registra incremento na mineração do personagem (saldo e total)
        if self.personagem_bateu_limite(user_id, personagem_id):
            return False  # não pode minerar mais

        self.db.atualizar_mineracao(user_id, personagem_id, valor_minerado, valor_minerado)
        return True

    def resetar_mineracao_personagem(self, user_id, personagem_id):
        self.db.resetar_saldo_minerado(user_id, personagem_id)
