class PersonagemManager:
    def __init__(self, db):
        self.db = db
        # personagem_id: (preco, gh_s)
        self.personagens_info = {
            1: (100, 1000),
            2: (200, 2500),
            3: (300, 4000),
            4: (400, 6000),
            5: (500, 8000),
            # Adicione mais personagens conforme necessário
        }
        self.limite_retorno = 1.3  # 130%

    def pode_minerar(self, user_id):
        personagens = self.db.listar_personagens_ativos(user_id)
        return len(personagens) > 0

    def calcular_ghs_total(self, user_id):
        personagens = self.db.listar_personagens_ativos(user_id)
        total_ghs = 0
        for personagem_id, quantidade, _, _ in personagens:
            info = self.personagens_info.get(personagem_id)
            if info:
                _, gh_s = info
                total_ghs += gh_s * quantidade
        return total_ghs

    def personagem_bateu_limite(self, user_id, personagem_id):
        info = self.personagens_info.get(personagem_id)
        if not info:
            return True  # Se personagem não for reconhecido, impede mineração

        preco, _ = info
        personagens = self.db.listar_personagens_ativos(user_id)
        for pid, _, _, total_minerado in personagens:
            if pid == personagem_id:
                return total_minerado >= preco * self.limite_retorno
        return True  # Se não encontrado, bloqueia mineração

    def registrar_mineracao(self, user_id, personagem_id, valor_minerado):
        if self.personagem_bateu_limite(user_id, personagem_id):
            return False
        self.db.atualizar_mineracao(user_id, personagem_id, valor_minerado, valor_minerado)
        return True

    def resetar_mineracao_personagem(self, user_id, personagem_id):
        self.db.resetar_saldo_minerado(user_id, personagem_id)
