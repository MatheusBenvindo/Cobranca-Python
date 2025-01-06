from whatsapp_utils import (
    criar_tabela,
    criar_driver,
    enviar_mensagem_inicial,
    verificar_mensagens_e_comprovantes,
)
from config import usuarios
import time


def main():
    # Criar a tabela de pagamentos no banco de dados
    criar_tabela()

    # Criar o driver para a verificação de mensagens
    driver = criar_driver()

    # Inicializar o campo status para cada usuário com base no banco de dados
    for usuario in usuarios:
        if "status" not in usuario:
            usuario["status"] = "pendente"

    # Enviar a mensagem inicial para cada usuário
    for usuario in usuarios:
        enviar_mensagem_inicial(driver, usuario)

    # Verificar mensagens e comprovantes para todos os usuários
    verificar_mensagens_e_comprovantes(driver)

    # Manter o driver aberto para inspeção
    print("Verificação concluída. Usuários pagaram, finalizando script.")
    while True:
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    main()
