import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, ADMIN_GROUP_ID, RANKING_GROUP_ID, CANAL_LINK, GRUPO_LINK
from database import Database
from personagens import PersonagensManager
from afiliados import AfiliadosManager
from mineracao import MineracaoManager
from pagamentos import PagamentosManager
from ranking import RankingManager
import threading
import time
from datetime import datetime

bot = telebot.TeleBot(TOKEN)
db = Database()
personagens_manager = PersonagensManager(db)
afiliados_manager = AfiliadosManager(db)
mineracao_manager = MineracaoManager(db, personagens_manager)
pagamentos_manager = PagamentosManager(db)
ranking_manager = RankingManager(db, bot, RANKING_GROUP_ID)

start_time = datetime.now()

def uptime():
    delta = datetime.now() - start_time
    return delta.days

# Envia o ranking todo dia 00:00
def enviar_ranking_diario():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            ranking_text = ranking_manager.gerar_texto_ranking_top20()
            total_depositos = db.somar_depositos()
            total_saques = db.somar_saques()
            dias_online = uptime()
            pagamentos_pendentes = db.contar_pagamentos_pendentes()

            texto_final = (f"🏆 Ranking Top 20 Mineradores 🏆\n\n"
                           f"{ranking_text}\n\n"
                           f"📊 Estatísticas Gerais:\n"
                           f"- Dias online: {dias_online}\n"
                           f"- Total depósitos: R${total_depositos:.2f}\n"
                           f"- Total saques: R${total_saques:.2f}\n"
                           f"- Pagamentos pendentes: {pagamentos_pendentes}\n\n"
                           f"Canal: {CANAL_LINK}\nGrupo: {GRUPO_LINK}")
            
            bot.send_message(RANKING_GROUP_ID, texto_final)
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=enviar_ranking_diario, daemon=True).start()

# Teclado principal
def teclado_principal():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🛒 Loja"), KeyboardButton("👛 Carteira"))
    markup.row(KeyboardButton("👥 Indicação"), KeyboardButton("📜 Registros"))
    markup.row(KeyboardButton("🎮 Meu personagem"), KeyboardButton("❓ Suporte"))
    return markup

# Comandos
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    db.criar_usuario_se_nao_existir(user_id)
    texto = "Bem-vindo ao DB-LTC!\n\nUse o menu abaixo para navegar:"
    bot.send_message(user_id, texto, reply_markup=teclado_principal())

@bot.message_handler(commands=['menu'])
def cmd_menu(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Menu principal:", reply_markup=teclado_principal())

# Handlers de botões
@bot.message_handler(func=lambda m: m.text == "🛒 Loja")
def loja_handler(message):
    from personagens import mostrar_loja
    mostrar_loja(bot, message.chat.id, db)

@bot.message_handler(func=lambda m: m.text == "👛 Carteira")
def carteira_handler(message):
    from pagamentos import mostrar_carteira
    mostrar_carteira(bot, message.chat.id, db)

@bot.message_handler(func=lambda m: m.text == "👥 Indicação")
def indicacao_handler(message):
    from afiliados import mostrar_indicacao
    mostrar_indicacao(bot, message.chat.id, db)

@bot.message_handler(func=lambda m: m.text == "📜 Registros")
def historico_handler(message):
    from pagamentos import mostrar_historico
    mostrar_historico(bot, message.chat.id, db)

@bot.message_handler(func=lambda m: m.text == "🎮 Meu personagem")
def meu_personagem_handler(message):
    from personagens import mostrar_personagens_comprados
    mostrar_personagens_comprados(bot, message.chat.id, db)

@bot.message_handler(func=lambda m: m.text == "❓ Suporte")
def suporte_handler(message):
    bot.send_message(message.chat.id, "Para suporte, entre em contato com: @j_anderson_bds")

# Inicia o bot
bot.polling(none_stop=True)
