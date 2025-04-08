import sqlite3

DATABASE_NAME = 'faculdade.db'  # Nome do nosso arquivo de banco de dados

def conectar_banco():
    return sqlite3.connect(DATABASE_NAME)

def criar_tabela_salas():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salas (
                id_sala INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_sala TEXT UNIQUE NOT NULL,
                capacidade INTEGER NOT NULL,
                bloco TEXT NOT NULL DEFAULT 'Bloco 01',
                apta_alunos_especiais INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()
        print("Tabela 'salas' criada ou já existe.")
    except Exception as e:
        print(f"Erro ao criar/verificar a tabela 'salas': {e}")
    finally:
        conn.close()

def alterar_tabela_salas_adicionar_bloco():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE salas ADD COLUMN bloco TEXT NOT NULL DEFAULT ''")
        conn.commit()
        print("Coluna 'bloco' adicionada à tabela 'salas'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("A coluna 'bloco' já existe na tabela 'salas'.")
        else:
            print(f"Erro ao adicionar a coluna 'bloco': {e}")
    finally:
        conn.close()

def criar_tabela_periodos():
    conn = conectar_banco() # Abre uma NOVA conexão
    cursor = conn.cursor() # Cria um NOVO cursor
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS periodos (
                id_periodo INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_periodo TEXT UNIQUE NOT NULL,
                numero_alunos INTEGER NOT NULL,
                num_alunos_especiais INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()
        print("Tabela 'periodos' criada ou já existe.")
    except Exception as e:
        print(f"Erro ao criar/verificar a tabela 'periodos': {e}")
    finally:
        conn.close()

def inserir_sala(nome_sala, capacidade, bloco='Bloco 01', apta_especial=0):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO salas (nome_sala, capacidade, bloco, apta_alunos_especiais) VALUES (?, ?, ?, ?)",
                       (nome_sala, capacidade, bloco, apta_especial))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Erro: Sala com o nome '{nome_sala}' já existe.")
        return False
    except Exception as e:
        print(f"Erro ao inserir sala: {e}")
        return False
    finally:
        conn.close()

def obter_salas():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_sala, nome_sala, capacidade, bloco, tipo_sala FROM salas ORDER BY nome_sala")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter salas no database.py: {e}") # Adicione um print aqui para debug
        return []
    finally:
        conn.close()

def obter_salas_aptas_especiais():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_sala, nome_sala, capacidade, bloco FROM salas WHERE apta_alunos_especiais = 1")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter salas aptas para alunos especiais: {e}")
        return []
    finally:
        conn.close()

def obter_consultorios():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_sala, nome_sala, capacidade, bloco FROM salas WHERE nome_sala LIKE 'Consultório %'")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter consultórios: {e}")
        return []
    finally:
        conn.close()

def inserir_periodo(nome_periodo, numero_alunos, num_alunos_especiais=0):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO periodos (nome_periodo, numero_alunos, num_alunos_especiais) VALUES (?, ?, ?)",
                       (nome_periodo, numero_alunos, num_alunos_especiais))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Erro: Período com o nome '{nome_periodo}' já existe.")
        return False
    except Exception as e:
        print(f"Erro ao inserir período: {e}")
        return False
    finally:
        conn.close()

# NO ARQUIVO database.py
def obter_periodos():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nome_periodo, numero_alunos, num_alunos_especiais FROM periodos ORDER BY nome_periodo")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter períodos no database.py: {e}") # Adicione um print aqui para debug
        return []
    finally:
        conn.close()

def obter_periodos_com_alunos_especiais():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_periodo, nome_periodo, numero_alunos, num_alunos_especiais FROM periodos WHERE num_alunos_especiais > 0")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter períodos com alunos especiais: {e}")
        return []
    finally:
        conn.close()

def alterar_tabela_salas_adicionar_tipo():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE salas ADD COLUMN tipo_sala TEXT DEFAULT 'Comum'") # 'Comum' ou 'Especial'
        conn.commit()
        print("Coluna 'tipo_sala' adicionada à tabela 'salas'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("A coluna 'tipo_sala' já existe na tabela 'salas'.")
        else:
            print(f"Erro ao alterar a tabela 'salas': {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()      

def alterar_tabela_periodos_adicionar_alunos_especiais():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE periodos ADD COLUMN num_alunos_especiais INTEGER DEFAULT 0")
        conn.commit()
        print("Coluna 'num_alunos_especiais' adicionada à tabela 'periodos'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("A coluna 'num_alunos_especiais' já existe na tabela 'periodos'.")
        else:
            print(f"Erro ao alterar a tabela 'periodos': {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def inserir_alocacao(nome_periodo, id_sala):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO alocacoes (nome_periodo, id_sala) VALUES (?, ?)", (nome_periodo, id_sala))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir alocação: {e}")
        return False
    finally:
        conn.close()

def obter_alocacoes():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nome_periodo, id_sala FROM alocacoes")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao obter alocações: {e}")
        return []
    finally:
        conn.close()

def limpar_alocacoes():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM alocacoes")
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao limpar alocações: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    criar_tabela_salas()
    alterar_tabela_salas_adicionar_bloco()
    # A linha abaixo foi removida:
    # alterar_tabela_salas_adicionar_aptidao_especial()
    criar_tabela_periodos()
    # A linha abaixo foi removida:
    # alterar_tabela_periodos_adicionar_alunos_especiais()
    print(f"Banco de dados '{DATABASE_NAME}' e tabelas 'salas' e 'periodos' verificadas/criadas com colunas adicionais.")
