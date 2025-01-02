import sqlite3
from config import usuarios
from datetime import datetime

def criar_tabela():
    """
    Cria a tabela `pagamentos` no banco de dados se ela não existir.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS pagamentos (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_usuario INTEGER,
                        valor REAL,
                        mes INTEGER,
                        ano INTEGER,
                        data_pagamento TEXT,
                        status TEXT)''')

    conn.commit()
    conn.close()

def salvar_pagamento(id_usuario, valor, mes, ano, data_pagamento, status):
    """
    Insere um novo pagamento na tabela `pagamentos` ou atualiza o status de um pagamento existente.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    cursor.execute('''SELECT ID FROM pagamentos 
                      WHERE id_usuario = ? AND mes = ? AND ano = ?''', 
                      (id_usuario, mes, ano))
    pagamento_existente = cursor.fetchone()

    if pagamento_existente:
        cursor.execute('''UPDATE pagamentos SET status = ?, data_pagamento = ? 
                          WHERE ID = ?''', 
                          (status, data_pagamento, pagamento_existente[0]))
    else:
        cursor.execute('''INSERT INTO pagamentos (id_usuario, valor, mes, ano, data_pagamento, status)
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                          (id_usuario, valor, mes, ano, data_pagamento, status))

    conn.commit()
    conn.close()

def obter_pagamentos():
    """
    Retorna uma lista com todos os pagamentos da tabela `pagamentos`.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM pagamentos''')
    pagamentos = cursor.fetchall()

    conn.close()
    return pagamentos

def verificar_todos_pagamentos():
    """
    Verifica se todos os usuários realizaram o pagamento.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    cursor.execute('''SELECT DISTINCT id_usuario FROM pagamentos WHERE status = 'pago' ''')
    usuarios_que_pagaram = [row[0] for row in cursor.fetchall()]

    conn.close()
    return set(usuarios_que_pagaram) == set([usuario['id_usuario'] for usuario in usuarios])

def usuario_pagou(id_usuario):
    """
    Verifica se o usuário já realizou o pagamento para o mês/ano atual.
    """
    conn = sqlite3.connect("pagamentos.db")
    cursor = conn.cursor()

    mes_atual = datetime.now().month
    ano_atual = datetime.now().year

    cursor.execute('''SELECT status FROM pagamentos 
                      WHERE id_usuario = ? AND mes = ? AND ano = ?''', 
                      (id_usuario, mes_atual, ano_atual))
    
    status = cursor.fetchone()

    conn.close()
    return status is not None and status[0] == "pago"