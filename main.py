import telebot
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

def enviar_ranking_diario():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            ranking_text = ranking_manager.gerar_texto_ranking_top20()
            # Adiciona informações gerais
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
            time.sleep(60)  # Espera 1 minuto para evitar múltiplas execuções no mesmo minuto
        time.sleep(30)

# Start da thread que envia ranking diário
threading.Thread(target=enviar_ranking_diario, daemon=True).start()

# Aqui você pode continuar com handlers de comando e menus

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    db.criar_usuario_se_nao_existir(user_id)
    bot.send_message(user_id, "Bem-vindo ao DB-LTC! Use /menu para começar.")

@bot.message_handler(commands=['menu'])
def cmd_menu(message):
    user_id = message.from_user.id
    texto = ("Menu principal:\n"
             "1. Loja\n"
             "2. Carteira\n"
             "3. Indicação\n"
             "4. Histórico\n"
             "5. Meu personagem\n"
             "6. Suporte")
    bot.send_message(user_id, texto)

# Adicione outros handlers e lógica conforme necessidade

bot.polling(none_stop=True)
