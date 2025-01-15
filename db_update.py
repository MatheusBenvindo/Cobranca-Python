import sqlite3
from datetime import datetime


def inserir_pagamento_manual(id_usuario, valor, mes, ano, data_pagamento, status):
    """
    Insere um pagamento manualmente na tabela `pagamentos`.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO pagamentos (id_usuario, valor, mes, ano, data_pagamento, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (id_usuario, valor, mes, ano, data_pagamento, status),
    )

    conn.commit()
    conn.close()
    print(
        f"Pagamento inserido manualmente para o usuário ID: {id_usuario}, mês: {mes}, ano: {ano}, status: {status}"
    )


def atualizar_pagamento_manual(id_usuario, valor, mes, ano, status):
    """
    Atualiza o valor e o status de um pagamento existente na tabela `pagamentos`.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE pagamentos SET valor = ?, status = ? 
           WHERE id_usuario = ? AND mes = ? AND ano = ?""",
        (valor, status, id_usuario, mes, ano),
    )

    conn.commit()
    conn.close()
    print(
        f"Pagamento atualizado manualmente para o usuário ID: {id_usuario}, mês: {mes}, ano: {ano}, valor: {valor}, status: {status}"
    )


def visualizar_pagamentos():
    """
    Exibe todos os pagamentos na tabela `pagamentos`.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pagamentos")
    pagamentos = cursor.fetchall()

    for pagamento in pagamentos:
        print(pagamento)

    conn.close()


def main():
    # Chamar a função para visualizar os pagamentos
    visualizar_pagamentos()

    # Atualizar pagamentos para o usuário ID 3 do mês 1 ao 12 para "pago" e valor 7.0
    id_usuario = 3
    valor = 7.0  # Valor do pagamento
    ano = 2025
    status = "pago"

    for mes in range(1, 13):
        atualizar_pagamento_manual(id_usuario, valor, mes, ano, status)

    # Visualizar pagamentos após atualização
    visualizar_pagamentos()


if __name__ == "__main__":
    main()
