import threading
import time

class MineracaoManager:
    def __init__(self, db):
        self.db = db
        self.rodar_mineracao = True
        threading.Thread(target=self.executar_mineracao_continua, daemon=True).start()

    def executar_mineracao_continua(self):
        while self.rodar_mineracao:
            usuarios = self.db.listar_usuarios()
            for user_id in usuarios:
                personagens = self.db.listar_personagens_ativos(user_id)
                for personagem in personagens:
                    id_perso = personagem['id']
                    gh_s = personagem['ghs']
                    ganho = gh_s * 0.000001  # Ganho por minuto
                    self.db.adicionar_minerado(id_perso, ganho)
                    self.db.atualizar_mineracao_total(id_perso, ganho)
                    
                    total_minerado = personagem['total_minerado'] + ganho
                    limite = personagem['valor_pago'] * 1.3
                    if total_minerado >= limite:
                        self.db.desativar_personagem(id_perso)
            time.sleep(60)

    def calcular_ghs_usuario(self, user_id):
        personagens = self.db.listar_personagens_ativos(user_id)
        total = sum(p['ghs'] for p in personagens)
        return total

    def resgatar_mineracao_personagem(self, personagem_id):
        personagem = self.db.obter_personagem_por_id(personagem_id)
        if not personagem:
            return None
        minerado = personagem['minerado']
        self.db.resetar_minerado(personagem_id)
        self.db.adicionar_saldo(personagem['user_id'], minerado)
        return minerado
