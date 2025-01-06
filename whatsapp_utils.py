from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import random
from datetime import datetime
from db_utils import salvar_pagamento, criar_tabela, usuario_pagou
from config import usuarios, plano, valor, pix
from telegram_utils import (
    gerar_tabela_pagamentos,
    enviar_notificacao_telegram,
    enviar_notificacao_final,
)
import logging
import re

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

perfil_chrome = (
    "C:\\Users\\matheus.ribeiro\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
)


def criar_driver():
    """
    Cria uma instância do driver do Chrome com as opções de perfil.
    """
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={perfil_chrome}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def abrir_conversa_whatsapp_web(driver, numero):
    """
    Abre uma conversa no WhatsApp Web a partir do número de telefone,
    mantendo a interação no navegador.
    """
    link = f"https://web.whatsapp.com/send?phone={numero}"
    driver.get(link)

    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
        )
    except TimeoutException:
        print("Erro: Tempo limite excedido ao tentar abrir a conversa no WhatsApp Web.")
        return

    print("Conversa aberta no WhatsApp Web com sucesso.")


def enviar_mensagem_inicial(driver, usuario):
    """
    Envia a mensagem inicial de cobrança para o usuário no WhatsApp Web.
    """
    abrir_conversa_whatsapp_web(driver, f"55{usuario['numero']}")

    mensagem = f"""Oi, {usuario['nome']} (ID: {usuario['id_usuario']}) 
    !, tudo bem?
    Referente ao {plano} no valor de R${usuario['valor']}, 
    favor realizar o pagamento via PIX: {pix}.
    Após o pagamento, envie o comprovante por aqui."""

    linhas_mensagem = mensagem.split("\n")

    caixa_texto_xpath = (
        '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p'
    )

    try:
        caixa_texto = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, caixa_texto_xpath))
        )
        print("Caixa de texto encontrada.")
    except TimeoutException:
        print("Erro: Tempo limite excedido ao procurar a caixa de texto.")
        return

    for linha in linhas_mensagem:
        caixa_texto.send_keys(linha.strip())
        time.sleep(random.uniform(1.0, 2.0))

    try:
        botao_enviar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button/span',
                )
            )
        )
        print("Botão de enviar encontrado.")
        botao_enviar.click()
    except TimeoutException:
        print("Erro: Tempo limite excedido ao procurar o botão de enviar.")
        return

    time.sleep(random.randint(5, 15))

    data_atual = datetime.now().strftime("%Y-%m-%d")
    salvar_pagamento(
        usuario["id_usuario"],
        usuario["valor"],
        datetime.now().month,
        datetime.now().year,
        data_atual,
        "pendente",
    )
    print(
        f"Mensagem enviada para o usuário {usuario['nome']} (ID: {usuario['id_usuario']})."
    )


def extrair_id_usuario(mensagem):
    """
    Extrai o ID do usuário da mensagem com base no nome e número de telefone.
    """
    try:
        for usuario in usuarios:
            if f"ID: {usuario['id_usuario']}" in mensagem:
                return usuario["id_usuario"]
        return None
    except Exception as e:
        logging.error(f"Erro ao extrair ID do usuário: {e}")
        return None


def verificar_documento(mensagem):
    """Verifica se a mensagem contém um documento PDF recebido."""
    try:
        # Verificar se a mensagem é recebida
        if "message-in" in mensagem.get_attribute("class"):
            tem_icone_download = bool(
                mensagem.find_elements(By.CSS_SELECTOR, "svg[title='audio-download']")
            )
            tem_icone_pdf = bool(
                mensagem.find_elements(By.CSS_SELECTOR, "div.icon-doc-pdf")
            )
            tem_link_pdf = False

            links = mensagem.find_elements(By.CSS_SELECTOR, "span._ao3e")
            for link in links:
                if link.text.endswith(".pdf"):
                    tem_link_pdf = True
                    break

            # Verificar se há ícones ou links indicando um documento PDF
            if tem_icone_download or tem_icone_pdf or tem_link_pdf:
                return True
        return False
    except Exception as e:
        logging.error(f"Erro ao verificar documento: {e}")
        return False


def enviar_mensagem_agradecimento(driver, usuario):
    """
    Envia uma mensagem de agradecimento ao usuário no WhatsApp Web.
    """
    abrir_conversa_whatsapp_web(driver, f"55{usuario['numero']}")

    mensagem = "Matt Bot agradece e deseja um ótimo dia a você."

    caixa_texto_xpath = (
        '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p'
    )

    try:
        caixa_texto = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, caixa_texto_xpath))
        )
        caixa_texto.send_keys(mensagem)
        time.sleep(random.uniform(1.0, 2.0))
    except TimeoutException:
        print("Erro: Tempo limite excedido ao procurar a caixa de texto.")
        return

    try:
        botao_enviar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button/span',
                )
            )
        )
        botao_enviar.click()
    except TimeoutException:
        print("Erro: Tempo limite excedido ao procurar o botão de enviar.")
        return

    time.sleep(random.randint(5, 15))
    print(
        f"Mensagem de agradecimento enviada para o usuário {usuario['nome']} (ID: {usuario['id_usuario']})."
    )


def verificar_mensagens_e_comprovantes(driver):
    """
    Verifica as últimas mensagens e atualiza o status dos pagamentos.
    """
    driver.get("https://web.whatsapp.com/")
    print("Aguardando 40 segundos para o carregamento do WhatsApp Web...")
    time.sleep(40)

    while True:
        todos_pagamentos_confirmados = True

        for usuario in usuarios:
            if usuario_pagou(usuario["id_usuario"]):
                usuario["status"] = "pago"
            else:
                usuario["status"] = "pendente"
                todos_pagamentos_confirmados = False

            if usuario["status"] == "pago":
                continue

            abrir_conversa_whatsapp_web(driver, f"55{usuario['numero']}")
            print(
                f"Verificando mensagens para o usuário {usuario['nome']} (ID: {usuario['id_usuario']})..."
            )

            print("Aguardando 20 segundos antes de iniciar a verificação...")
            time.sleep(20)

            try:
                logging.info("Procurando mensagens...")
                mensagens = driver.find_elements(
                    By.CSS_SELECTOR, "div.message-in, div.message-out"
                )[-7:]
                logging.info(f"Mensagens encontradas: {len(mensagens)}")

                if not mensagens:
                    logging.info("Nenhuma mensagem encontrada.")
                    time.sleep(60)
                    continue

                for mensagem in mensagens:
                    if verificar_documento(mensagem):  # Usar a função modificada
                        data_hora_atual = datetime.now()
                        data_pagamento = data_hora_atual.strftime("%Y-%m-%d")
                        salvar_pagamento(
                            usuario["id_usuario"],
                            usuario["valor"],
                            data_hora_atual.month,
                            data_hora_atual.year,
                            data_pagamento,
                            "pago",
                        )
                        logging.info(
                            f"Pagamento confirmado para usuário {usuario['nome']} (ID: {usuario['id_usuario']})"
                        )

                        enviar_mensagem_agradecimento(driver, usuario)

                        tabela = gerar_tabela_pagamentos()

                        enviar_notificacao_telegram(
                            f"Pagamento atualizado:\n`\n{tabela}\n`"
                        )

                        usuario["status"] = "pago"
                        break
                    else:
                        data_atual = datetime.now().strftime("%Y-%m-%d")
                        salvar_pagamento(
                            usuario["id_usuario"],
                            usuario["valor"],
                            datetime.now().month,
                            datetime.now().year,
                            data_atual,
                            "pendente",
                        )
                        logging.info(
                            f"Pagamento pendente para usuário {usuario['nome']} (ID: {usuario['id_usuario']})"
                        )
            except Exception as e:
                logging.error(f"Erro ao verificar mensagens: {e}")
                try:
                    driver.get("https://web.whatsapp.com/")
                    print("Reabrindo WhatsApp Web...")
                    time.sleep(40)
                except Exception as re:
                    logging.error(f"Erro ao reabrir o WhatsApp Web: {re}")
                    break

            time.sleep(60)

        if todos_pagamentos_confirmados:
            enviar_notificacao_final()
            break

        logging.info(
            "Verificação de mensagens concluída. Aguardando 1 minuto antes de reiniciar a verificação."
        )
        time.sleep(60)
