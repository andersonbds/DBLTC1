# config.py

TOKEN = "8133159958:AAF1aUZfozpr530BZPAett732InChbqW_uM"

# IDs dos grupos para notificações e ranking
ADMIN_GROUP_ID = -1002133147416  # grupo de notificações administrativas
RANKING_GROUP_ID = -1002097853797  # grupo de ranking diário

# Links Telegram
CANAL_LINK = "https://t.me/+zarG81QZG-42Yzkx"
GRUPO_LINK = "https://t.me/+8C2QrANF1BMwMGRh"

# API KuCoin (ainda a definir uso)
KUCOIN_API_KEY = "6831feed92fc6e0001dc2323"
KUCOIN_API_SECRET = "96407457-4c15-4964-b3a3-1384521270c5"
KUCOIN_API_PASSPHRASE = "Brasileiro355"

# Configurações financeiras
MIN_SAQUE_PIX = 0.10  # mínimo saque Pix em BRL
MIN_SAQUE_LTC = 0.0002  # mínimo saque LTC

# Conversão
GH_S_TO_REAL = 0.01  # 100 GH/s = R$1,00 (0.01 por GH/s)

# Mineração
MINERACAO_PERCENTUAL_MENSAL = 1.0  # 1% ao mês por personagem

# Preço dos personagens (dobrando a cada um, começando em 0.10 BRL)
PERSONAGENS_PRECO_BRL = [0.10 * (2 ** i) for i in range(10)]
