# config.py

TOKEN = "8133159958:AAF1aUZfozpr530BZPAett732InChbqW_uM"

# IDs dos grupos para notificações e ranking
ADMIN_GROUP_ID = -1001234567890  # substitua pelo chat_id do seu grupo admin
RANKING_GROUP_ID = -1009876543210  # substitua pelo chat_id do grupo de ranking

# Links Telegram
CANAL_LINK = "https://t.me/seucanal"  # coloque seu link real aqui
GRUPO_LINK = "https://t.me/seugrupo"  # coloque seu link real aqui

# API KuCoin (informações que você passou)
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

# Cashback multi-nível para indicação
CASHBACK_NIVEIS = [1.0, 0.5, 0.25]

# Preço dos personagens (dobrando a cada um, começando em 0.10 BRL)
PERSONAGENS_PRECO_BRL = [0.10 * (2 ** i) for i in range(10)]
