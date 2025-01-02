from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import random
from datetime import datetime
from db_utils import salvar_pagamento
from config import usuarios, plano, valor, pix
from telegram_utils import gerar_tabela_pagamentos, enviar_notificacao_telegram
import re
import logging

# Caminho para o diretório do perfil do Chrome
perfil_chrome = 'C:\\Users\\matheus.ribeiro\\AppData\\Local\\Google\\Chrome\\User Data\\Default'

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
    chrome_options.add_argument("--headless")  # Adicione esta linha se quiser rodar o Chrome em modo headless

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def enviar_mensagem_inicial(usuario):
    """
    Envia a mensagem inicial de cobrança para o usuário no grupo "Eu".
    """
    driver = criar_driver()
    driver.get('https://web.whatsapp.com/')
    time.sleep(40)

    contato = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//span[@title='Eu']")))
    contato.click()

    # Escrever e enviar a mensagem
    mensagem = f"""Oi, {usuario['nome']}! 
Referente ao {plano} no valor de R${usuario['valor']}, 
favor realizar o pagamento via PIX: {pix}.
Após o pagamento, envie o comprovante por aqui."""  # Remove emojis complexos, se houver

    caixa_texto_xpath = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p'
    caixa_texto = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, caixa_texto_xpath))
    )

    # Enviar a mensagem inteira de uma vez
    caixa_texto.send_keys(mensagem)
    time.sleep(random.uniform(0.5, 1.0))  # Intervalo aleatório entre 500ms e 1s para simular digitação

    botao_enviar = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button/span'))
    )
    botao_enviar.click()

    time.sleep(random.randint(5, 15))

    data_atual = datetime.now().strftime("%Y-%m-%d")
    salvar_pagamento(usuario['id_usuario'], usuario['valor'], 1, 2024, data_atual, "pendente")

def extrair_id_usuario(mensagem):
    """
    Extrai o ID do usuário da mensagem.
    """
    try:
        id_usuario = int(mensagem.split(":")[0].replace("US", ""))
        return id_usuario
    except (ValueError, IndexError):
        return None

import logging

def verificar_comprovante(mensagem):
    """
    Verifica se a mensagem contém um comprovante de pagamento (imagem ou PDF).
    """
    logging.info("Verificando a mensagem para comprovantes.")

    try:
        # Verifica se há uma imagem na mensagem
        if mensagem.find_element(By.CSS_SELECTOR, "img[src*='blob']"):
            logging.info("Imagem encontrada na mensagem.")
            return True
    except NoSuchElementException:
        logging.info("Nenhuma imagem encontrada na mensagem.")

    try:
        # Verifica se há um link para um arquivo PDF na mensagem
        if mensagem.find_element(By.CSS_SELECTOR, "a.x13faqbe._ao3e"):
            logging.info("PDF encontrado na mensagem.")
            return True
    except NoSuchElementException:
        logging.info("Nenhum PDF encontrado na mensagem.")

    logging.info("Nenhum comprovante encontrado na mensagem.")
    return False


def verificar_mensagens_e_comprovantes():
    """
    Verifica as últimas mensagens no grupo "Eu" e atualiza o status dos pagamentos.
    """
    driver = criar_driver()
    driver.get('https://web.whatsapp.com/')

    time.sleep(40)

    contato = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"//span[@title='Eu']"))
    )
    contato.click()

    # Verificar mensagens por 1 minuto
    end_time = time.time() + 60  # 1 minuto (60 segundos)
    while time.time() < end_time:
        mensagens = driver.find_elements(By.CSS_SELECTOR, "div[class*='message-in']")[-5:]

        for mensagem in mensagens:
            id_usuario = extrair_id_usuario(mensagem.text)
            print(f"Verificando mensagem do usuário ID: {id_usuario}")

            if id_usuario is not None:
                if verificar_comprovante(mensagem):
                    data_hora_atual = datetime.now()
                    data_pagamento = data_hora_atual.strftime("%Y-%m-%d")
                    salvar_pagamento(id_usuario, valor, 1, 2024, data_pagamento, "pago")
                    print(f"Pagamento confirmado para o usuário ID: {id_usuario}")

                    # Gerar a tabela de pagamentos
                    tabela = gerar_tabela_pagamentos()

                    # Enviar a tabela para o Telegram
                    enviar_notificacao_telegram(f"Pagamento atualizado:\n`\n{tabela}\n`")
                else:
                    data_atual = datetime.now().strftime("%Y-%m-%d")
                    salvar_pagamento(id_usuario, valor, 1, 2024, data_atual, "pendente")
                    print(f"Pagamento pendente para o usuário ID: {id_usuario}")

        time.sleep(10)  # Espera 10 segundos antes de verificar novamente

    time.sleep(random.randint(5, 15))
