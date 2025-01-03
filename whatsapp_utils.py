from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import random
from datetime import datetime
from db_utils import salvar_pagamento, criar_tabela
from config import usuarios, plano, valor, pix
from telegram_utils import gerar_tabela_pagamentos, enviar_notificacao_telegram
import logging
import re

# Configurar o logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Caminho para o diretório do perfil do Chrome
perfil_chrome = (
    "C:\\Users\\matheus.ribeiro\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
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
    # Removemos a linha de execução em modo headless para exibir o navegador
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def enviar_mensagem_inicial(driver, usuario):
    """
    Envia a mensagem inicial de cobrança para o usuário no grupo "Eu".
    """
    driver.get("https://web.whatsapp.com/")
    print("Aguardando 40 segundos para o carregamento do WhatsApp Web...")
    time.sleep(40)

    try:
        contato = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[@title='Eu']"))
        )
        print("Elemento 'Eu' encontrado e clicável.")
        contato.click()
    except TimeoutException:
        print("Erro: Tempo limite excedido ao procurar o elemento 'Eu'.")
        return

    # Escrever e enviar a mensagem
    mensagem = f"""Oi, {usuario['nome']} (ID: {usuario['id_usuario']}) 
    !, tudo bem?
    Referente ao {plano} no valor de R${usuario['valor']}, 
    favor realizar o pagamento via PIX: {pix}.
    Após o pagamento, envie o comprovante por aqui."""

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

    # Enviar a mensagem inteira de uma vez
    caixa_texto.send_keys(mensagem)
    time.sleep(
        random.uniform(0.5, 1.0)
    )  # Intervalo aleatório entre 500ms e 1s para simular digitação

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
        usuario["id_usuario"], usuario["valor"], 1, 2024, data_atual, "pendente"
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
    """Verifica se a mensagem contém um documento."""
    tem_icone_download = bool(
        mensagem.find_elements(By.CSS_SELECTOR, "svg[title='audio-download']")
    )
    tem_icone_pdf = bool(mensagem.find_elements(By.CSS_SELECTOR, "div.icon-doc-pdf"))
    tem_link_pdf = False

    # Verificar se há um link com texto terminando em ".pdf"
    links = mensagem.find_elements(By.CSS_SELECTOR, "span._ao3e")
    for link in links:
        if link.text.endswith(".pdf"):
            tem_link_pdf = True
            break

    # Verificar pelo XPath fornecido
    tem_xpath_pdf = bool(
        mensagem.find_elements(
            By.XPATH,
            '//*[@id="main"]/div[3]/div/div[2]/div[3]/div[41]/div/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[1]/div',
        )
    )

    return tem_icone_download or tem_icone_pdf or tem_link_pdf or tem_xpath_pdf


def verificar_mensagens_e_comprovantes(driver):
    """
    Verifica as últimas mensagens e atualiza o status dos pagamentos.
    """
    driver.get("https://web.whatsapp.com/")
    print("Aguardando 40 segundos para o carregamento do WhatsApp Web...")
    time.sleep(40)

    try:
        contato = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[@title='Eu']"))
        )
        print("Elemento 'Eu' encontrado e clicável.")
        contato.click()
    except TimeoutException:
        print("Erro: Tempo limite excedido ao procurar o elemento 'Eu'.")
        return

    # Aguardar 20 segundos antes de iniciar a verificação
    print("Aguardando 20 segundos antes de iniciar a verificação...")
    time.sleep(20)

    logging.info("Iniciando verificação de mensagens a cada 10 segundos.")
    tentativas_sem_mensagens = 0  # Contador de tentativas sem mensagens
    max_tentativas_sem_mensagens = (
        5  # Máximo de tentativas sem mensagens antes de sair do loop
    )

    usuario_atual_id = None  # Variável para armazenar o ID do usuário atual

    while tentativas_sem_mensagens < max_tentativas_sem_mensagens:
        try:
            logging.info("Procurando mensagens...")
            # Capturar as últimas 7 mensagens
            mensagens = driver.find_elements(
                By.CSS_SELECTOR, "div.message-in, div.message-out"
            )[-7:]
            logging.info(f"Mensagens encontradas: {len(mensagens)}")

            if not mensagens:
                logging.info("Nenhuma mensagem encontrada.")
                tentativas_sem_mensagens += 1
                time.sleep(10)
                continue

            tentativas_sem_mensagens = (
                0  # Resetar o contador se mensagens forem encontradas
            )

            for mensagem in mensagens:
                if (
                    not usuario_atual_id
                ):  # Procurar o ID do usuário apenas se não estiver definido
                    usuario_atual_id = extrair_id_usuario(mensagem.text)
                    if usuario_atual_id:
                        logging.info(f"Usuário atual ID encontrado: {usuario_atual_id}")

                if usuario_atual_id:
                    logging.info(
                        f"Verificando comprovante para o usuário ID: {usuario_atual_id}"
                    )
                    if verificar_documento(mensagem):
                        data_hora_atual = datetime.now()
                        data_pagamento = data_hora_atual.strftime("%Y-%m-%d")
                        salvar_pagamento(
                            usuario_atual_id, valor, 1, 2024, data_pagamento, "pago"
                        )
                        logging.info(
                            f"Pagamento confirmado para usuário ID: {usuario_atual_id}"
                        )

                        # Gerar a tabela de pagamentos
                        tabela = gerar_tabela_pagamentos()

                        # Enviar a tabela para o Telegram
                        enviar_notificacao_telegram(
                            f"Pagamento atualizado:\n`\n{tabela}\n`"
                        )
                        usuario_atual_id = None  # Resetar o ID do usuário após o pagamento ser confirmado
                    else:
                        data_atual = datetime.now().strftime("%Y-%m-%d")
                        salvar_pagamento(
                            usuario_atual_id, valor, 1, 2024, data_atual, "pendente"
                        )
                        logging.info(
                            f"Pagamento pendente para usuário ID: {usuario_atual_id}"
                        )
                else:
                    logging.info(
                        f"ID do usuário não encontrado na mensagem: {mensagem.text}"
                    )
        except Exception as e:
            logging.error(f"Erro ao verificar mensagens: {e}")
            # Reabrir a aba do WhatsApp Web se ela foi fechada
            try:
                driver.get("https://web.whatsapp.com/")
                print("Reabrindo WhatsApp Web...")
                time.sleep(40)
            except Exception as re:
                logging.error(f"Erro ao reabrir o WhatsApp Web: {re}")
                break  # Se não conseguir reabrir o WhatsApp, sair do loop

        time.sleep(10)  # Espera 10 segundos antes de verificar novamente

    logging.info("Verificação de mensagens concluída.")


def main():
    # Criar a tabela de pagamentos no banco de dados
    criar_tabela()

    # Criar o driver para a verificação de mensagens
    driver = criar_driver()

    # Verificar mensagens e comprovantes para todos os usuários
    verificar_mensagens_e_comprovantes(driver)

    # Manter o driver aberto para inspeção
    print("Verificação concluída. Mantenha o navegador aberto para inspeção.")
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
