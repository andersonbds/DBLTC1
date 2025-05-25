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

        # Informações extras, como nome e preço em BRL, para o front
        self.personagens_detalhes = {
            1: {"nome": "Personagem 1", "preco_brl": 100.00},
            2: {"nome": "Personagem 2", "preco_brl": 200.00},
            3: {"nome": "Personagem 3", "preco_brl": 300.00},
            4: {"nome": "Personagem 4", "preco_brl": 400.00},
            5: {"nome": "Personagem 5", "preco_brl": 500.00},
        }

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

    def obter_personagens_disponiveis(self):
        # Retorna lista de personagens com nome e preço para exibir na loja
        personagens = []
        for pid, detalhes in self.personagens_detalhes.items():
            personagens.append({
                "id": pid,
                "nome": detalhes["nome"],
                "preco_brl": detalhes["preco_brl"],
                "ghs": self.personagens_info[pid][1]
            })
        return personagens

    def comprar_personagem(self, user_id, indice_personagem):
        personagens = self.obter_personagens_disponiveis()
        if indice_personagem < 0 or indice_personagem >= len(personagens):
            return False, "Personagem inválido."
        personagem = personagens[indice_personagem]
        preco = personagem["preco_brl"]

        saldo = self.db.get_saldo(user_id)
        if saldo["brl"] < preco:
            return False, "Saldo insuficiente para comprar esse personagem."

        # Deduz o saldo em BRL
        self.db.atualizar_saldo_brl(user_id, saldo["brl"] - preco)

        # Registra o personagem comprado no banco, quantidade 1, saldo minerado 0, total minerado 0
        self.db.adicionar_personagem(user_id, personagem["id"], 1, 0, 0)

        return True, f"Personagem {personagem['nome']} comprado com sucesso!"

    def get_personagens_usuario(self, user_id):
        # Retorna personagens ativos do usuário com detalhes
        ativos = self.db.listar_personagens_ativos(user_id)
        lista = []
        for pid, quantidade, saldo_minerado, total_minerado in ativos:
            detalhes = self.personagens_detalhes.get(pid, {})
            ghs = self.personagens_info.get(pid, (0, 0))[1]
            lista.append({
                "id": pid,
                "nome": detalhes.get("nome", f"Personagem {pid}"),
                "quantidade": quantidade,
                "ghs": ghs,
                "minerado_ltc": saldo_minerado,
                "total_minerado": total_minerado
            })
        return lista

    def resgatar_mineracao(self, user_id, nome_personagem):
        personagens = self.get_personagens_usuario(user_id)
        personagem = next((p for p in personagens if p["nome"].lower() == nome_personagem.lower()), None)
        if not personagem:
            return False, "Personagem não encontrado."

        if personagem["minerado_ltc"] <= 0:
            return False, "Nenhum saldo disponível para resgate."

        # Atualiza saldo LTC do usuário
        saldo_atual = self.db.get_saldo(user_id)["ltc"]
        novo_saldo = saldo_atual + personagem["minerado_ltc"]
        self.db.atualizar_saldo_ltc(user_id, novo_saldo)

        # Reseta saldo minerado do personagem (mas mantém total minerado para controle)
        self.resetar_mineracao_personagem(user_id, personagem["id"])

        return True, f"Você resgatou {personagem['minerado_ltc']:.6f} LTC do personagem {personagem['nome']}."
