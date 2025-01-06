import telebot
from tabulate import tabulate
from db_utils import obter_pagamentos
from config import TELEGRAM_TOKEN, usuarios
import logging

# Configurar o logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Inicializa o bot do Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def gerar_tabela_pagamentos():
    '''
    Gera uma tabela formatada com o status dos pagamentos.
    Obtém os pagamentos do banco de dados e cruza com a lista de usuários.
    Se o pagamento do usuário for encontrado, adiciona o status do pagamento na tabela.
    Caso contrário, marca o status como "Pendente".
    '''
    pagamentos = obter_pagamentos()

    # Log para verificar os pagamentos obtidos
    logging.info(f"Pagamentos obtidos: {pagamentos}")

    tabela = []
    for usuario in usuarios:
        pagamento = next((p for p in pagamentos if p[1] == usuario["id_usuario"]), None)
        if pagamento:
            tabela.append([usuario["nome"], pagamento[6]])
        else:
            tabela.append([usuario["nome"], "Pendente"])

    tabela_formatada = tabulate(tabela, headers=["Usuário", "Status"], tablefmt="grid")
    return tabela_formatada

def enviar_notificacao_telegram(mensagem):
    '''
    Envia uma mensagem para o ID do Telegram especificado.
    '''
    bot.send_message(6361695761, mensagem, parse_mode="Markdown")

def enviar_notificacao_final():
    '''
    Envia uma notificação final quando todos os usuários tiverem pago.
    '''
    mensagem = "Todos os usuários pagaram! Pode abater a fatura."
    bot.send_message(6361695761, mensagem, parse_mode="Markdown")
