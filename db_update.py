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


if __name__ == "__main__":
    main()
