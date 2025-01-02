import logging
from config import usuarios
from db_utils import criar_tabela, usuario_pagou, verificar_todos_pagamentos
from whatsapp_utils import enviar_mensagem_inicial, verificar_mensagens_e_comprovantes
from telegram_utils import enviar_notificacao_final, gerar_tabela_pagamentos, enviar_notificacao_telegram

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Criando tabela no banco de dados.")
criar_tabela()

# Verificar mensagens e comprovantes
logging.info("Verificando mensagens e comprovantes.")
verificar_mensagens_e_comprovantes()

# Gerar e enviar a tabela de pagamentos
logging.info("Gerando e enviando a tabela de pagamentos.")
tabela = gerar_tabela_pagamentos()
enviar_notificacao_telegram(f"Tabela de pagamentos:\n`{tabela}`")

# Verificar se todos os usuários pagaram
logging.info("Verificando se todos os usuários pagaram.")
if verificar_todos_pagamentos():
    logging.info("Todos os usuários pagaram. Enviando notificação final.")
    enviar_notificacao_final()
else:
    logging.info("Nem todos os usuários pagaram.")