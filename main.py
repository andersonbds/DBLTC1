import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, ADMIN_GROUP_ID, RANKING_GROUP_ID, CANAL_LINK, GRUPO_LINK
from database import Database
from personagens import PersonagemManager
from afiliados import mostrar_indicacao
from mineracao import MineracaoManager
from pagamentos import mostrar_carteira, mostrar_historico
from ranking import RankingManager
import threading
import time
from datetime import datetime

# Inicializa o bot e os gerenciadores
bot = telebot.TeleBot(TOKEN)
db = Database()
mineracao_manager = MineracaoManager(db)
personagem_manager = PersonagemManager(db)  # <-- Corrigido aqui, passando db
ranking_manager = RankingManager(db, bot, RANKING_GROUP_ID)

start_time = datetime.now()

# Importa handlers depois do bot
import handlers

def uptime():
    delta = datetime.now() - start_time
    return delta.days

# Envio diário de ranking no grupo
def enviar_ranking_diario():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            ranking_text = ranking_manager.gerar_texto_ranking_top20()
            total_depositos = db.somar_depositos()
            total_saques = db.somar_saques()
            dias_online = uptime()
            pagamentos_pendentes = db.contar_pagamentos_pendentes()

            texto_final = (
                f"🏆 Ranking Top 20 Mineradores 🏆\n\n"
                f"{ranking_text}\n\n"
                f"📊 Estatísticas Gerais:\n"
                f"- Dias online: {dias_online}\n"
                f"- Total depósitos: R${total_depositos:.2f}\n"
                f"- Total saques: R${total_saques:.2f}\n"
                f"- Pagamentos pendentes: {pagamentos_pendentes}\n\n"
                f"Canal: {CANAL_LINK}\nGrupo: {GRUPO_LINK}"
            )

            bot.send_message(RANKING_GROUP_ID, texto_final)
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=enviar_ranking_diario, daemon=True).start()

# Menu principal
def teclado_principal():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🛒 Loja"), KeyboardButton("👛 Carteira"))
    markup.row(KeyboardButton("👥 Indicação"), KeyboardButton("📜 Registros"))
    markup.row(KeyboardButton("🎮 Meu personagem"), KeyboardButton("❓ Suporte"))
    return markup

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

# Handler para suporte
@bot.message_handler(func=lambda m: m.text == "❓ Suporte")
def suporte_handler(message):
    bot.send_message(message.chat.id, "Para suporte, entre em contato com: @j_anderson_bds")

# Registra os handlers do arquivo handlers.py
handlers.register_handlers(bot)

# Iniciar o bot
bot.polling(none_stop=True)
