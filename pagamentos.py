from telebot import types
from config import MIN_SAQUE_PIX, MIN_SAQUE_LTC
from database import Database

db = Database()

def mostrar_carteira(user_id):
    saldo = db.get_saldo(user_id)
    texto = (
        f"Seu saldo atual:\n"
        f"LTC: {saldo['ltc']:.6f}\n"
        f"BRL: R$ {saldo['brl']:.2f}\n\n"
        f"Para sacar, o mínimo é {MIN_SAQUE_PIX} BRL (Pix) ou {MIN_SAQUE_LTC} LTC.\n\n"
        "Para solicitar saque, envie:\n"
        "/saque pix <chave_pix> <valor_em_brl>\n"
        "ou\n"
        "/saque ltc <endereco_ltc> <valor_em_ltc>"
    )
    return texto

def mostrar_historico(user_id):
    registros = db.get_historico_pagamentos(user_id)
    if not registros:
        return "Você não possui histórico de pagamentos."
    texto = "Histórico de pagamentos:\n"
    for r in registros[-20:]:  # últimos 20
        tipo = "Depósito" if r['tipo'] == 'deposito' else "Saque"
        valor = r['valor']
        status = r['status']
        data = r['data'].strftime("%d/%m/%Y %H:%M")
        texto += f"{data} - {tipo}: {valor} - Status: {status}\n"
    return texto

def solicitar_saque(bot, message, metodo, destino, valor_str):
    user_id = message.from_user.id
    try:
        valor = float(valor_str)
    except ValueError:
        bot.send_message(user_id, "Valor inválido. Use números, ex: 0.1")
        return

    saldo = db.get_saldo(user_id)

    if metodo == 'pix':
        if valor < MIN_SAQUE_PIX:
            bot.send_message(user_id, f"Valor mínimo para saque via Pix é R$ {MIN_SAQUE_PIX}")
            return
        if valor > saldo['brl']:
            bot.send_message(user_id, "Saldo insuficiente em BRL.")
            return
    elif metodo == 'ltc':
        if valor < MIN_SAQUE_LTC:
            bot.send_message(user_id, f"Valor mínimo para saque via LTC é {MIN_SAQUE_LTC}")
            return
        if valor > saldo['ltc']:
            bot.send_message(user_id, "Saldo insuficiente em LTC.")
            return
    else:
        bot.send_message(user_id, "Método de saque inválido. Use 'pix' ou 'ltc'.")
        return

    # Registrar saque no banco com status "pendente"
    db.registrar_saque(user_id, metodo, destino, valor)

    bot.send_message(user_id, f"Saque de {valor} {metodo.upper()} solicitado com sucesso! Aguarde aprovação.")

    # Notificar admin
    texto_admin = (
        f"Novo pedido de saque:\n"
        f"Usuário: {user_id}\n"
        f"Método: {metodo}\n"
        f"Destino: {destino}\n"
        f"Valor: {valor}"
    )
    bot.send_message(ADMIN_GROUP_ID, texto_admin)
