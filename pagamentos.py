from pagamentos import mostrar_carteira, mostrar_historico

# Exemplo dentro de um handler de comando:
/*
@bot.message_handler(commands=['carteira'])
def carteira_handler(message):
    texto = mostrar_carteira(message.from_user.id)
    bot.send_message(message.chat.id, texto)
*/
