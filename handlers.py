from telebot import types
from config import ADMIN_GROUP_ID, CANAL_LINK, GRUPO_LINK, MIN_SAQUE_PIX, MIN_SAQUE_LTC
from database import Database
from personagens import PersonagemManager
from datetime import datetime

db = Database()
personagem_manager = PersonagemManager(db)

def register_handlers(bot):
    def main_menu_keyboard():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("💰 Carteira", "🛒 Loja")
        markup.row("👤 Meu Personagem", "📊 Ranking")
        markup.row("📢 Indicação", "ℹ️ Sobre")
        return markup

    @bot.message_handler(commands=['start'])
    def start_handler(message):
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        if not db.user_exists(user_id):
            db.add_user(user_id, username)
        markup = main_menu_keyboard()
        bot.send_message(user_id, f"Olá, {username}! Bem-vindo ao DB-LTC. Escolha uma opção:", reply_markup=markup)

    @bot.message_handler(func=lambda m: m.text == "💰 Carteira")
    def carteira_handler(message):
        user_id = message.from_user.id
        saldo = db.get_saldo(user_id)
        texto = f"Seu saldo atual:\nLTC: {saldo['ltc']:.6f}\nBRL: R$ {saldo['brl']:.2f}\n\n" \
                f"Para saque, mínimo: {MIN_SAQUE_PIX} BRL (Pix) ou {MIN_SAQUE_LTC} LTC."
        bot.send_message(user_id, texto)

    @bot.message_handler(func=lambda m: m.text == "🛒 Loja")
    def loja_handler(message):
        user_id = message.from_user.id
        personagens_disponiveis = personagem_manager.listar_personagens_disponiveis()
        texto = "Personagens disponíveis para compra:\n"
        for idx, p in enumerate(personagens_disponiveis, start=1):
            texto += f"{idx}. {p['nome']} - Preço: R$ {p['preco_brl']:.2f}\n"
        texto += "\nPara comprar, envie: comprar <número do personagem>"
        bot.send_message(user_id, texto)

    @bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("comprar "))
    def comprar_handler(message):
        user_id = message.from_user.id
        try:
            idx = int(message.text.split()[1]) - 1
            sucesso, msg = personagem_manager.comprar_personagem(user_id, idx)
            bot.send_message(user_id, msg)
            if sucesso:
                notify_admin(bot, f"Usuário {user_id} comprou personagem #{idx+1}")
        except Exception:
            bot.send_message(user_id, "Formato inválido. Use: comprar <número do personagem>")

    @bot.message_handler(func=lambda m: m.text == "👤 Meu Personagem")
    def meus_personagens_handler(message):
        user_id = message.from_user.id
        personagens = personagem_manager.get_personagens_usuario(user_id)
        if not personagens:
            bot.send_message(user_id, "Você não possui personagens ativos.")
            return
        texto = "Seus personagens:\n"
        for p in personagens:
            texto += f"- {p['nome']}: GH/s = {p['ghs']}, Minerado: {p['minerado_ltc']:.6f} LTC\n"
        texto += "\nPara resgatar, envie: resgatar <nome do personagem>"
        bot.send_message(user_id, texto)

    @bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("resgatar "))
    def resgatar_handler(message):
        user_id = message.from_user.id
        nome_pers = message.text.split(" ", 1)[1]
        sucesso, msg = personagem_manager.resgatar_mineracao(user_id, nome_pers)
        bot.send_message(user_id, msg)
        if sucesso:
            notify_admin(bot, f"Usuário {user_id} resgatou mineração do personagem {nome_pers}")

    @bot.message_handler(func=lambda m: m.text == "📊 Ranking")
    def ranking_handler(message):
        ranking = db.get_top_20_usuarios()
        texto = "Ranking Top 20 Mineradores:\n"
        for i, user in enumerate(ranking, 1):
            texto += f"{i}. @{user['username']} - GH/s: {user['ghs']} - Saldo LTC: {user['ltc']:.6f}\n"
        bot.send_message(message.chat.id, texto)

    @bot.message_handler(func=lambda m: m.text == "📢 Indicação")
    def indicacao_handler(message):
        user_id = message.from_user.id
        link = db.get_link_indicacao(user_id)
        texto = f"Seu link de indicação:\n{link}"
        bot.send_message(user_id, texto)

    @bot.message_handler(func=lambda m: m.text == "ℹ️ Sobre")
    def sobre_handler(message):
        texto = ("DB-LTC Bot\n"
                 "Mineração simulada com pagamento real em LTC.\n"
                 "Suporte e grupo oficial:\n" + GRUPO_LINK + "\n"
                 "Canal oficial:\n" + CANAL_LINK)
        bot.send_message(message.chat.id, texto)

def notify_admin(bot, text):
    bot.send_message(ADMIN_GROUP_ID, f"[NOTIFICAÇÃO]\n{text}")
