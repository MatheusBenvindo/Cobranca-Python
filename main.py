import logging
import os
from datetime import datetime
from whatsapp_utils import (
    criar_tabela,
    criar_driver,
    enviar_mensagem_inicial,
    verificar_mensagens_e_comprovantes,
)
from config import usuarios
import time
import calendar

# Definir o caminho do arquivo de log na área de trabalho
log_dir = r"C:\Users\matheus.ribeiro\OneDrive - Central das Cooperativas de Crédito e Economia do DF\Área de Trabalho"
log_file = os.path.join(log_dir, "cobranca_log.txt")

# Configurar o logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def is_weekday(date):
    return date.weekday() < 5  # Segunda a sexta-feira são os dias 0 a 4


def get_nth_weekday_of_month(year, month, n):
    weekdays = [
        day
        for day in range(1, 32)
        if datetime(year, month, day).weekday() < 5
        and datetime(year, month, day).month == month
    ]
    return weekdays[n - 1] if len(weekdays) >= n else None


def is_between_fifth_and_tenth_weekday(year, month, day):
    fifth_weekday = get_nth_weekday_of_month(year, month, 5)
    tenth_weekday = get_nth_weekday_of_month(year, month, 10)
    return fifth_weekday <= day <= tenth_weekday


def main():
    today = datetime.now()
    if is_weekday(today) and is_between_fifth_and_tenth_weekday(
        today.year, today.month, today.day
    ):
        logging.info("Iniciando a verificação de mensagens e comprovantes.")

        """Criar a tabela de pagamentos no banco de dados"""
        criar_tabela()

        driver = criar_driver()

        """Inicializa o campo status para cada usuário com base no banco de dados"""
        for usuario in usuarios:
            if "status" not in usuario:
                usuario["status"] = "pendente"

        for usuario in usuarios:
            enviar_mensagem_inicial(driver, usuario)

        verificar_mensagens_e_comprovantes(driver)

        logging.info("Verificação concluída. Usuários pagaram, finalizando script.")
        print("Verificação concluída. Usuários pagaram, finalizando script.")
        while True:
            time.sleep(10)
            driver.quit()
    else:
        logging.info(
            "Hoje não é um dia útil ou não está entre o quinto e o décimo dia útil do mês. O script não será executado."
        )
        print(
            "Hoje não é um dia útil ou não está entre o quinto e o décimo dia útil do mês. O script não será executado."
        )


if __name__ == "__main__":
    main()
