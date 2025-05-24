import telebot
from telebot import types
from datetime import datetime, timedelta
from database import Database
from config import TOKEN, CANAL_LINK, GRUPO_LINK, ADMIN_GROUP_ID, RANKING_GROUP_ID, MIN_SAQUE_PIX, MIN_SAQUE_LTC, GH_S_TO_REAL
from personagens import get_personagem_by_id, calcular_retorno_mensal, limite_retorno, listar_personagens_texto

bot = telebot.TeleBot(TOKEN)
db = Database()

# Menu principal
def menu_principal_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛒 Loja", "📦 Meus Personagens")
    markup.row("💰 Carteira", "👥 Indicação")
    markup.row("📜 Registros", "ℹ️ Sobre")
    markup.row("🔗 Grupo", "📢 Canal")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    # Registrar usuário se não existir
    db.criar_usuario(user_id, username)
    texto = (
        f"Olá, {username}! Bem-vindo ao DB-LTC Bot.\n\n"
        "Aqui você pode comprar personagens para minerar LTC, acompanhar seu saldo, sacar e muito mais.\n\n"
        "Use o menu abaixo para navegar."
    )
    bot.send_message(user_id, texto, reply_markup=menu_principal_keyboard())

# Loja - lista personagens
@bot.message_handler(func=lambda m: m.text == "🛒 Loja")
def loja(message):
    texto = "🛒 Personagens disponíveis:\n\n"
    texto += listar_personagens_texto()
    texto += "\nEnvie o número do personagem para comprar."
    bot.send_message(message.chat.id, texto)

# Receber compra personagem
@bot.message_handler(func=lambda m: m.text.isdigit())
def comprar_personagem(message):
    user_id = message.from_user.id
    pid = int(message.text)
    personagem = get_personagem_by_id(pid)
    if not personagem:
        bot.send_message(user_id, "Personagem inválido. Tente novamente.")
        return

    saldo = db.get_saldo(user_id)
    preco = personagem["preco_brl"]
    if saldo < preco:
        bot.send_message(user_id, f"Saldo insuficiente para comprar {personagem['nome']}. Preço: R${preco:.2f}. Saldo atual: R${saldo:.2f}")
        return

    # Registrar compra
    db.comprar_personagem(user_id, pid, preco)
    bot.send_message(user_id, f"Parabéns! Você comprou {personagem['nome']} por R${preco:.2f}.")
    # Notificar admin
    bot.send_message(ADMIN_GROUP_ID, f"Usuário @{message.from_user.username or user_id} comprou personagem {personagem['nome']} por R${preco:.2f}")

# Meus Personagens
@bot.message_handler(func=lambda m: m.text == "📦 Meus Personagens")
def meus_personagens(message):
    user_id = message.from_user.id
    personagens_user = db.listar_personagens_usuario(user_id)
    if not personagens_user:
        bot.send_message(user_id, "Você não possui personagens comprados.")
        return

    texto = "Seus personagens:\n\n"
    for p in personagens_user:
        personagem = get_personagem_by_id(p['personagem_id'])
        minerado = p['minerado']
        total_investido = personagem['preco_brl']
        limite = total_investido * 1.3
        texto += (f"{personagem['nome']} - Minerado: R${mineral := minerado:.4f} / Limite: R${limite:.2f}\n")

    texto += "\nPara resgatar o valor minerado, envie: resgatar seguido do número do personagem, ex: resgatar 1"
    bot.send_message(user_id, texto)

# Resgatar mineração manual
@bot.message_handler(func=lambda m: m.text.lower().startswith("resgatar"))
def resgatar_mineracao(message):
    user_id = message.from_user.id
    try:
        pid = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(user_id, "Envie no formato correto: resgatar <número do personagem>")
        return

    personagem = get_personagem_by_id(pid)
    if not personagem:
        bot.send_message(user_id, "Personagem inválido.")
        return

    registro = db.get_personagem_usuario(user_id, pid)
    if not registro:
        bot.send_message(user_id, "Você não possui esse personagem.")
        return

    minerado = registro['minerado']
    if minerado <= 0:
        bot.send_message(user_id, "Não há saldo minerado para resgatar.")
        return

    # Adicionar minerado ao saldo da carteira
    db.adicionar_saldo(user_id, minerado)
    # Resetar minerado no personagem (mas manter total minerado para limite)
    db.resetar_minerado_personagem(user_id, pid)

    bot.send_message(user_id, f"Você resgatou R${minerado:.4f} para sua carteira.")
    # Notificar admin
    bot.send_message(ADMIN_GROUP_ID, f"Usuário @{message.from_user.username or user_id} resgatou R${minerado:.4f} do personagem {personagem['nome']}.")

# Carteira
@bot.message_handler(func=lambda m: m.text == "💰 Carteira")
def carteira(message):
    user_id = message.from_user.id
    saldo = db.get_saldo(user_id)
    texto = f"Seu saldo atual é: R${saldo:.4f}\n"
    texto += f"Mínimo para saque PIX: R${MIN_SAQUE_PIX:.2f}\n"
    texto += f"Mínimo para saque LTC: {MIN_SAQUE_LTC:.6f} LTC\n"
    texto += "Para sacar, envie:\nPIX <valor> ou LTC <valor>"
    bot.send_message(user_id, texto)

# Processar saque manual
@bot.message_handler(func=lambda m: m.text.upper().startswith(("PIX ", "LTC ")))
def processar_saque(message):
    user_id = message.from_user.id
    texto = message.text.upper()
    parts = texto.split()
    if len(parts) != 2:
        bot.send_message(user_id, "Formato incorreto. Use: PIX <valor> ou LTC <valor>")
        return

    tipo, valor_str = parts
    try:
        valor = float(valor_str.replace(',', '.'))
    except:
        bot.send_message(user_id, "Valor inválido.")
        return

    saldo = db.get_saldo(user_id)

    if tipo == "PIX":
        if valor < MIN_SAQUE_PIX:
            bot.send_message(user_id, f"Valor mínimo para saque PIX é R${MIN_SAQUE_PIX:.2f}")
            return
        if valor > saldo:
            bot.send_message(user_id, "Saldo insuficiente.")
            return
        # Registrar pedido de saque PIX
        db.registrar_saque(user_id, tipo, valor)
        bot.send_message(user_id, f"Saque PIX de R${valor:.2f} solicitado. Aguarde aprovação.")
        bot.send_message(ADMIN_GROUP_ID, f"Pedido de saque PIX de R${valor:.2f} do usuário @{message.from_user.username or user_id}.")
    elif tipo == "LTC":
        if valor < MIN_SAQUE_LTC:
            bot.send_message(user_id, f"Valor mínimo para saque LTC é {MIN_SAQUE_LTC:.6f} LTC")
            return
        # Aqui precisa converter saldo R$ para LTC (exemplo simplificado)
        saldo_ltc = saldo / GH_S_TO_REAL / 100  # ajustar lógica conforme saldo
        if valor > saldo_ltc:
            bot.send_message(user_id, "Saldo LTC insuficiente.")
            return
        db.registrar_saque(user_id, tipo, valor)
        bot.send_message(user_id, f"Saque LTC de {valor:.6f} solicitado. Aguarde aprovação.")
        bot.send_message(ADMIN_GROUP_ID, f"Pedido de saque LTC de {valor:.6f} do usuário @{message.from_user.username or user_id}.")
    else:
        bot.send_message(user_id, "Tipo de saque inválido.")

# Indicação - mostrar link
@bot.message_handler(func=lambda m: m.text == "👥 Indicação")
def indicacao(message):
    user_id = message.from_user.id
    link = f"https://t.me/SeuBot?start={user_id}"
    texto = (
        f"Seu link de indicação:\n{link}\n\n"
        "Quando seu indicado comprar na loja, você ganha bônus em múltiplos níveis.\n"
        "Bônus só válido para compras feitas na loja."
    )
    bot.send_message(user_id, texto)

# Registros - submenu com histórico simples
@bot.message_handler(func=lambda m: m.text == "📜 Registros")
def registros(message):
    user_id = message.from_user.id
    historico = db.get_historico(user_id)
    if not historico:
        bot.send_message(user_id, "Você não possui registros.")
        return
    texto = "Seus registros:\n\n
