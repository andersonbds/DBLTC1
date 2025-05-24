import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, ADMIN_GROUP_ID, RANKING_GROUP_ID, CANAL_LINK, GRUPO_LINK
from database import Database
from personagens import mostrar_loja, mostrar_personagens_comprados
from afiliados import mostrar_indicacao
from mineracao import MineracaoManager
from pagamentos import mostrar_carteira, mostrar_historico
from ranking import RankingManager
import threading
import time
from datetime import datetime

# Importa os handlers personalizados (isso ativa todos os handlers definidos lá)
import handlers

bot = telebot.TeleBot(TOKEN)
db = Database()
ranking_manager = RankingManager(db, bot, RANKING_GROUP_ID)
mineracao_manager = MineracaoManager(db)

start_time = datetime.now()

def uptime():
    delta = datetime.now() - start_time
    return delta.days

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

# Apenas os botões extras (se não estiverem no handlers.py)
@bot.message_handler(func=lambda m: m.text == "❓ Suporte")
def suporte_handler(message):
    bot.send_message(message.chat.id, "Para suporte, entre em contato com: @j_anderson_bds")

# Iniciar o bot
bot.polling(none_stop=True)
