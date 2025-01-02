import schedule
import time
import logging
from config import usuarios
from db_utils import criar_tabela, verificar_todos_pagamentos, usuario_pagou
from whatsapp_utils import enviar_mensagem_inicial, verificar_mensagens_e_comprovantes
from telegram_utils import enviar_notificacao_final
import random

# Configurar o logging
logging.basicConfig(filename='cobrancas.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 1. Criar a tabela no banco de dados
criar_tabela()
logging.info("Tabela 'pagamentos' criada no banco de dados.")

# 2. Agendar a verificação de mensagens e o envio de cobranças
def job():
    logging.info("Iniciando verificação de pagamentos...")

    # Verificar se todos os usuários já pagaram
    if verificar_todos_pagamentos():
        enviar_notificacao_final()  # Envia notificação final pelo Telegram
        logging.info("Todos os pagamentos foram recebidos. Encerrando a execução.")
        return  # Encerra a função job()

    # Cobrar apenas quem não pagou
    for usuario in usuarios:
        if not usuario_pagou(usuario['id_usuario']):
            enviar_mensagem_inicial(usuario)
            logging.info(f"Mensagem de cobrança enviada para {usuario['nome']}.")
            time.sleep(random.randint(60, 300))  # Espera entre 1 e 5 minutos

    # Verificar novas mensagens e comprovantes
    verificar_mensagens_e_comprovantes()
    logging.info("Verificação de mensagens e comprovantes concluída.")

# Agendar a execução da função job() a cada hora entre 08:00 e 17:00 de segunda a sexta
for dia in range(0, 5):  # 0 = segunda-feira, 1 = terça-feira, ..., 4 = sexta-feira
    for hora in range(8, 18):  # 8 = 08:00, 9 = 09:00, ..., 17 = 17:00
        schedule.every().day.at(f"{hora:02d}:00").do(job)

# Executar o agendamento
while True:
    schedule.run_pending()
    time.sleep(1)