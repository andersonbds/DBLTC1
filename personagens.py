from datetime import datetime, timedelta

# Definição dos personagens (exemplo: 10 tipos)
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

MINERACAO_MENSAL_PERCENTUAL = 1.0  # 1% ao mês

def get_personagem_by_id(pid):
    for p in PERSONAGENS:
        if p["id"] == pid:
            return p
    return None

def calcular_retorno_mensal(preco_brl):
    # Retorno mensal = 1% do preço investido
    return preco_brl * (MINERACAO_MENSAL_PERCENTUAL / 100)

def calcular_ghs_total(quantidade, ghs_unitario):
    return quantidade * ghs_unitario

def pode_comprar(user_saldo, preco):
    return user_saldo >= preco

# Controle de retorno máximo 130% (investimento + 30% lucro)
def limite_retorno(preco, total_minerado):
    limite = preco * 1.3
    return total_minerado < limite

# Exemplo para formatar os personagens para mostrar no bot
def listar_personagens_texto():
    texto = ""
    for p in PERSONAGENS:
        texto += f"{p['id']} - {p['nome']} - Preço: R${p['preco_brl']:.2f} - Poder: {p['ghs']} GH/s\n"
    return texto
