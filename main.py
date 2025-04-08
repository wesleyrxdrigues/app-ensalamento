import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from itertools import combinations
import csv
from database import conectar_banco, criar_tabela_salas, criar_tabela_periodos, alterar_tabela_salas_adicionar_bloco

# --- Variáveis Globais ---
entry_nome_sala = None
entry_capacidade_sala = None
entry_bloco_sala = None
tree_salas = None
sala_id_para_editar = None

entry_nome_periodo = None
entry_num_alunos = None
entry_num_alunos_especiais = None
tree_periodos = None

combo_periodo1 = None
combo_sala_periodo1 = None
combo_periodo2 = None
combo_sala_periodo2 = None
combo_periodo3 = None
combo_sala_periodo3 = None
combo_periodo4 = None
combo_sala_periodo4 = None
combo_sala_reposicao = None

resultado_alocacao_global = {}

# --- Funções de Banco de Dados (Importadas) ---
# (As funções conectar_banco, criar_tabela_salas, criar_tabela_periodos,
# alterar_tabela_salas_adicionar_bloco estão no arquivo database.py)

def obter_salas():
    print("OBTER SALAS EXECUTADO")
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_sala, nome_sala, capacidade, bloco, tipo_sala FROM salas ORDER BY nome_sala")
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao obter salas: {e}")
        return []
    finally:
        conn.close()

def adicionar_sala():
    global entry_nome_sala, entry_capacidade_sala, entry_bloco_sala, tree_salas, sala_id_para_editar, var_sala_especial

    nome = entry_nome_sala.get()
    capacidade_str = entry_capacidade_sala.get()
    bloco = entry_bloco_sala.get()
    tipo_sala = "Especial" if var_sala_especial.get() else "Comum" # Obtém o valor do checkbox

    if not nome or not capacidade_str or not bloco:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    try:
        capacidade = int(capacidade_str)
        if capacidade <= 0:
            raise ValueError("A capacidade deve ser um número positivo.")
    except ValueError:
        messagebox.showerror("Erro", "A capacidade deve ser um número inteiro positivo.")
        return

    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        if sala_id_para_editar is not None:
            # Modo de Edição
            cursor.execute("UPDATE salas SET nome_sala=?, capacidade=?, bloco=?, tipo_sala=? WHERE id_sala=?",
                           (nome, capacidade, bloco, tipo_sala, sala_id_para_editar))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Sala '{nome}' atualizada com sucesso!")
            cancelar_edicao_sala()
        else:
            # Modo de Adição
            try:
                cursor.execute("INSERT INTO salas (nome_sala, capacidade, bloco, tipo_sala) VALUES (?, ?, ?, ?)", (nome, capacidade, bloco, tipo_sala))
                conn.commit()
                messagebox.showinfo("Sucesso", "Sala adicionada com sucesso!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", f"A sala '{nome}' já está cadastrada.")

        atualizar_lista_salas()
        entry_nome_sala.delete(0, tk.END)
        entry_capacidade_sala.delete(0, tk.END)
        entry_bloco_sala.delete(0, tk.END)
        var_sala_especial.set(False) # Reseta o checkbox

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar sala: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def salvar_edicao_sala():
    # A lógica de salvar a edição foi movida para a função adicionar_sala
    adicionar_sala()

def atualizar_lista_salas():
    for item in tree_salas.get_children():
        tree_salas.delete(item)
    salas = obter_salas_com_id()
    for sala in salas:
        tree_salas.insert("", tk.END, values=sala) # A tupla 'sala' já inclui o tipo

def obter_salas_com_id():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_sala, nome_sala, capacidade, bloco, tipo_sala FROM salas ORDER BY nome_sala")
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao obter salas: {e}")
        return []
    finally:
        conn.close()

def janela_cadastro_salas():
    global entry_nome_sala, entry_capacidade_sala, entry_bloco_sala, tree_salas, btn_editar_sala, btn_adicionar_sala, btn_cancelar_edicao, var_sala_especial

    janela_salas = tk.Toplevel(root)
    janela_salas.title("Cadastro de Salas")

    frame_entrada = ttk.LabelFrame(janela_salas, text="Adicionar/Editar Sala")
    frame_entrada.pack(padx=10, pady=10, fill="x")

    lbl_nome_sala = ttk.Label(frame_entrada, text="Nome da Sala:")
    lbl_nome_sala.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nome_sala = ttk.Entry(frame_entrada)
    entry_nome_sala.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    lbl_capacidade_sala = ttk.Label(frame_entrada, text="Capacidade:")
    lbl_capacidade_sala.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_capacidade_sala = ttk.Entry(frame_entrada)
    entry_capacidade_sala.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    lbl_bloco_sala = ttk.Label(frame_entrada, text="Bloco:")
    lbl_bloco_sala.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_bloco_sala = ttk.Entry(frame_entrada)
    entry_bloco_sala.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # Checkbox para sala especial
    var_sala_especial = tk.BooleanVar()
    chk_sala_especial = ttk.Checkbutton(frame_entrada, text="Sala para Alunos Especiais", variable=var_sala_especial)
    chk_sala_especial.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    btn_adicionar_sala = ttk.Button(frame_entrada, text="Adicionar Sala", command=adicionar_sala)
    btn_adicionar_sala.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    btn_cancelar_edicao = ttk.Button(frame_entrada, text="Cancelar Edição", command=cancelar_edicao_sala, state=tk.DISABLED)
    btn_cancelar_edicao.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    frame_lista = ttk.LabelFrame(janela_salas, text="Lista de Salas Cadastradas")
    frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

    tree_salas = ttk.Treeview(frame_lista, columns=("ID", "Nome", "Capacidade", "Bloco", "Tipo"), show="headings")
    tree_salas.heading("ID", text="ID")
    tree_salas.heading("Nome", text="Nome da Sala")
    tree_salas.heading("Capacidade", text="Capacidade")
    tree_salas.heading("Bloco", text="Bloco")
    tree_salas.heading("Tipo", text="Tipo")
    tree_salas.column("ID", width=0, stretch=tk.NO)
    tree_salas.column("Nome", width=150)
    tree_salas.column("Capacidade", width=100)
    tree_salas.column("Bloco", width=80)
    tree_salas.column("Tipo", width=100)
    tree_salas.pack(fill="both", expand=True)
    tree_salas.bind("<<TreeviewSelect>>", selecionar_sala_para_editar)

    btn_editar_sala = ttk.Button(frame_lista, text="Editar Sala", command=abrir_edicao_sala, state=tk.DISABLED)
    btn_editar_sala.pack(pady=5, fill="x")

    atualizar_lista_salas()
    janela_salas.mainloop()

def selecionar_sala_para_editar(event):
    global sala_id_para_editar
    selected_item = tree_salas.selection()
    if selected_item:
        btn_editar_sala.config(state=tk.NORMAL)
        sala_id_para_editar = tree_salas.item(selected_item[0], "values")[0] # Pega o ID da sala
    else:
        btn_editar_sala.config(state=tk.DISABLED)
        sala_id_para_editar = None

def abrir_edicao_sala():
    global sala_id_para_editar, var_sala_especial
    if sala_id_para_editar is not None:
        selected_item = tree_salas.selection()[0]
        values = tree_salas.item(selected_item, "values")
        entry_nome_sala.delete(0, tk.END)
        entry_nome_sala.insert(0, values[1])
        entry_capacidade_sala.delete(0, tk.END)
        entry_capacidade_sala.insert(0, values[2])
        entry_bloco_sala.delete(0, tk.END)
        entry_bloco_sala.insert(0, values[3])
        var_sala_especial.set(True if values[4] == "Especial" else False) # Define o estado do checkbox

        btn_adicionar_sala.config(text="Salvar Edições", command=salvar_edicao_sala)
        btn_editar_sala.config(state=tk.DISABLED)
        btn_cancelar_edicao.config(state=tk.NORMAL)

def cancelar_edicao_sala():
    global sala_id_para_editar
    entry_nome_sala.delete(0, tk.END)
    entry_capacidade_sala.delete(0, tk.END)
    entry_bloco_sala.delete(0, tk.END)
    btn_adicionar_sala.config(text="Adicionar Sala", command=adicionar_sala)
    btn_editar_sala.config(state=tk.DISABLED)
    btn_cancelar_edicao.config(state=tk.DISABLED)
    sala_id_para_editar = None

def obter_periodos():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nome_periodo, numero_alunos, num_alunos_especiais FROM periodos ORDER BY nome_periodo")
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao obter períodos: {e}")
        return []
    finally:
        conn.close()

def janela_cadastro_periodos():
    global entry_nome_periodo, entry_num_alunos, entry_num_alunos_especiais, tree_periodos, btn_editar_periodo, btn_adicionar_periodo, btn_cancelar_edicao_periodo, periodo_id_para_editar

    janela_periodos = tk.Toplevel(root)
    janela_periodos.title("Cadastro de Períodos")

    frame_entrada = ttk.LabelFrame(janela_periodos, text="Adicionar Novo Período")
    frame_entrada.pack(padx=10, pady=10, fill="x")

    lbl_nome_periodo = ttk.Label(frame_entrada, text="Nome do Período:")
    lbl_nome_periodo.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nome_periodo = ttk.Entry(frame_entrada)
    entry_nome_periodo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    lbl_num_alunos = ttk.Label(frame_entrada, text="Número de Alunos:")
    lbl_num_alunos.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_num_alunos = ttk.Entry(frame_entrada)
    entry_num_alunos.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    lbl_num_alunos_especiais = ttk.Label(frame_entrada, text="Alunos Especiais:")
    lbl_num_alunos_especiais.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_num_alunos_especiais = ttk.Entry(frame_entrada)
    entry_num_alunos_especiais.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    btn_adicionar_periodo = ttk.Button(frame_entrada, text="Adicionar Período", command=adicionar_periodo) # Renomeei
    btn_adicionar_periodo.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    btn_cancelar_edicao_periodo = ttk.Button(frame_entrada, text="Cancelar Edição", command=cancelar_edicao_periodo, state=tk.DISABLED) # Novo botão
    btn_cancelar_edicao_periodo.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    # Frame para a lista de períodos
    frame_lista = ttk.LabelFrame(janela_periodos, text="Lista de Períodos Cadastrados")
    frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

    tree_periodos = ttk.Treeview(frame_lista, columns=("ID", "Nome", "Alunos", "Especiais"), show="headings") # Adicione ID
    tree_periodos.heading("ID", text="ID")
    tree_periodos.heading("Nome", text="Nome do Período")
    tree_periodos.heading("Alunos", text="Número de Alunos")
    tree_periodos.heading("Especiais", text="Alunos Especiais")
    tree_periodos.column("ID", width=0, stretch=tk.NO) # Oculta ID
    tree_periodos.column("Nome", width=150)
    tree_periodos.column("Alunos", width=100)
    tree_periodos.column("Especiais", width=100)
    tree_periodos.pack(fill="both", expand=True)

    tree_periodos.bind("<<TreeviewSelect>>", selecionar_periodo_para_editar) # Bind da seleção

    btn_editar_periodo = ttk.Button(frame_lista, text="Editar Período", command=abrir_edicao_periodo, state=tk.DISABLED) # Novo botão
    btn_editar_periodo.pack(pady=5, fill="x")

    atualizar_lista_periodos()
    # janela_periodos.mainloop()

def selecionar_periodo_para_editar(event):
    global periodo_id_para_editar
    selected_item = tree_periodos.selection()
    if selected_item:
        btn_editar_periodo.config(state=tk.NORMAL)
        periodo_id_para_editar = tree_periodos.item(selected_item[0], "values")[0] # Pega o ID do período
    else:
        btn_editar_periodo.config(state=tk.DISABLED)
        periodo_id_para_editar = None

def abrir_edicao_periodo():
    global periodo_id_para_editar
    if periodo_id_para_editar is not None:
        selected_item = tree_periodos.selection()[0]
        values = tree_periodos.item(selected_item, "values")
        entry_nome_periodo.delete(0, tk.END)
        entry_nome_periodo.insert(0, values[1])
        entry_num_alunos.delete(0, tk.END)
        entry_num_alunos.insert(0, values[2])
        entry_num_alunos_especiais.delete(0, tk.END)
        entry_num_alunos_especiais.insert(0, values[3])

        btn_adicionar_periodo.config(text="Salvar Edições", command=salvar_edicao_periodo)
        btn_editar_periodo.config(state=tk.DISABLED)
        btn_cancelar_edicao_periodo.config(state=tk.NORMAL)

def cancelar_edicao_periodo():
    global periodo_id_para_editar
    entry_nome_periodo.delete(0, tk.END)
    entry_num_alunos.delete(0, tk.END)
    entry_num_alunos_especiais.delete(0, tk.END)
    btn_adicionar_periodo.config(text="Adicionar Período", command=adicionar_periodo)
    btn_editar_periodo.config(state=tk.DISABLED)
    btn_cancelar_edicao_periodo.config(state=tk.DISABLED)
    periodo_id_para_editar = None



def adicionar_periodo():
    global entry_nome_periodo, entry_num_alunos, entry_num_alunos_especiais, tree_periodos, periodo_id_para_editar

    nome = entry_nome_periodo.get()
    num_alunos_str = entry_num_alunos.get()
    num_alunos_especiais_str = entry_num_alunos_especiais.get()

    if not nome or not num_alunos_str:
        messagebox.showerror("Erro", "Por favor, preencha o nome e o número de alunos.")
        return

    try:
        num_alunos = int(num_alunos_str)
        if num_alunos < 0:
            raise ValueError("O número de alunos não pode ser negativo.")
        num_alunos_especiais = int(num_alunos_especiais_str) if num_alunos_especiais_str else 0
        if num_alunos_especiais < 0:
            raise ValueError("O número de alunos especiais não pode ser negativo.")
    except ValueError:
        messagebox.showerror("Erro", "O número de alunos deve ser um número inteiro não negativo.")
        return

    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        if periodo_id_para_editar is not None:
            # Modo de Edição
            cursor.execute("UPDATE periodos SET nome_periodo=?, numero_alunos=?, num_alunos_especiais=? WHERE id_periodo=?",
                           (nome, num_alunos, num_alunos_especiais, periodo_id_para_editar))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Período '{nome}' atualizado com sucesso!")
            cancelar_edicao_periodo() # Volta ao modo de adição
        else:
            # Modo de Adição
            try:
                cursor.execute("INSERT INTO periodos (nome_periodo, numero_alunos, num_alunos_especiais) VALUES (?, ?, ?)", (nome, num_alunos, num_alunos_especiais))
                conn.commit()
                messagebox.showinfo("Sucesso", "Período adicionado com sucesso!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", f"O período '{nome}' já está cadastrado.")

        atualizar_lista_periodos()
        entry_nome_periodo.delete(0, tk.END)
        entry_num_alunos.delete(0, tk.END)
        entry_num_alunos_especiais.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar período: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def salvar_edicao_periodo():
    # A lógica de salvar a edição foi movida para a função adicionar_periodo
    adicionar_periodo()

def atualizar_lista_periodos():
    # Limpa a lista atual
    for item in tree_periodos.get_children():
        tree_periodos.delete(item)

    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_periodo, nome_periodo, numero_alunos, num_alunos_especiais FROM periodos") # Incluindo o ID
        periodos = cursor.fetchall()
        for periodo in periodos:
            tree_periodos.insert("", tk.END, values=periodo) # Insere a tupla completa (incluindo o ID)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao carregar os períodos: {e}")
    finally:
        conn.close()

def on_double_click_periodo(event):
    item = tree_periodos.selection()[0]
    periodo_id = tree_periodos.item(item, "values")[0]
    # Aqui você pode implementar a lógica para editar o período, se necessário
    messagebox.showinfo("Info", f"ID do período selecionado: {periodo_id}")

def remover_periodo():
    selected_item = tree_periodos.selection()
    if not selected_item:
        messagebox.showinfo("Atenção", "Selecione um período para remover.")
        return
    periodo_id = tree_periodos.item(selected_item[0], "values")[0]
    nome_periodo = tree_periodos.item(selected_item[0], "values")[1]

    if messagebox.askyesno("Confirmação", f"Deseja remover o período '{nome_periodo}'?"):
        conn = conectar_banco()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM periodos WHERE id_periodo=?", (periodo_id,))
            conn.commit()
            atualizar_lista_periodos()
            messagebox.showinfo("Sucesso", f"Período '{nome_periodo}' removido com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover período: {e}")
        finally:
            conn.close()

# --- Funções para Alocação ---
def realizar_alocacao():
    global resultado_alocacao_global
    conn = conectar_banco()
    cursor = conn.cursor()

    alocacoes_resultado = {}

    try:
        # Limpar tabela de alocações anteriores
        cursor.execute("DELETE FROM alocacoes")
        conn.commit()

        cursor.execute("SELECT id_periodo, nome_periodo, numero_alunos FROM periodos ORDER BY numero_alunos DESC")
        periodos = cursor.fetchall()

        cursor.execute("SELECT id_sala, nome_sala, capacidade FROM salas ORDER BY capacidade DESC")
        salas_originais = cursor.fetchall()

        salas_disponiveis = {sala[0]: {"nome": sala[1], "capacidade": sala[2], "ocupada_por": None} for sala in salas_originais}

        for periodo_id, nome_periodo, num_alunos in periodos:
            alocado = False
            salas_para_alocar_ids = []
            capacidade_necessaria = num_alunos

            # 1. Tentar alocar em uma única sala vazia
            for sala_id, info_sala in salas_disponiveis.items():
                if info_sala["ocupada_por"] is None and info_sala["capacidade"] >= capacidade_necessaria:
                    salas_para_alocar_ids = [sala_id]
                    salas_disponiveis[sala_id]["ocupada_por"] = nome_periodo
                    alocado = True
                    break

            # 2. Se não couber em uma sala, tentar combinações de salas vazias
            if not alocado:
                salas_vazias = [(sid, sinfo["nome"], sinfo["capacidade"]) for sid, sinfo in salas_disponiveis.items() if sinfo["ocupada_por"] is None and sinfo["capacidade"] > 0]
                melhor_combinacao = None
                menor_num_salas = float('inf')
                menor_excedente = float('inf')

                for i in range(1, len(salas_vazias) + 1):
                    for combinacao in combinations(salas_vazias, i):
                        capacidade_total = sum(sala[2] for sala in combinacao)
                        if capacidade_total >= capacidade_necessaria:
                            excedente = capacidade_total - capacidade_necessaria
                            if len(combinacao) < menor_num_salas or (len(combinacao) == menor_num_salas and excedente < menor_excedente):
                                menor_num_salas = len(combinacao)
                                menor_excedente = excedente
                                melhor_combinacao = combinacao

                if melhor_combinacao:
                    salas_para_alocar_ids = [sala[0] for sala in melhor_combinacao]
                    capacidade_alocada = 0
                    for sala_id in salas_para_alocar_ids:
                        salas_disponiveis[sala_id]["ocupada_por"] = nome_periodo + " (Parcial)" # Marcar como parcialmente ocupada
                        capacidade_alocada += salas_disponiveis[sala_id]["capacidade"]
                        if capacidade_alocada >= capacidade_necessaria:
                            break # Suficiente salas para este periodo

                    if capacidade_alocada >= capacidade_necessaria:
                        alocado = True
                    else:
                        # Desfazer alocação parcial se não atingiu a capacidade total
                        for sala_id in salas_para_alocar_ids:
                            salas_disponiveis[sala_id]["ocupada_por"] = None
                        alocado = False


            # Registrar a alocação
            alocacoes_resultado[nome_periodo] = []
            if alocado:
                for sala_id in salas_para_alocar_ids:
                    sala_nome = salas_disponiveis[sala_id]["nome"]
                    alocacoes_resultado[nome_periodo].append(sala_nome)
                    cursor.execute("INSERT INTO alocacoes (nome_periodo, id_sala) VALUES (?, ?)", (nome_periodo, sala_id))
                conn.commit()
            else:
                alocacoes_resultado[nome_periodo] = ["NÃO ALOCADO"]
                messagebox.showerror("Erro de Alocação", f"Não foi possível alocar o período '{nome_periodo}' com {num_alunos} alunos nas salas disponíveis sem misturar períodos.")

        exibir_resultado_alocacao(alocacoes_resultado)
        resultado_alocacao_global = alocacoes_resultado
        return alocacoes_resultado

    except Exception as e:
        messagebox.showerror("Erro",f"Ocorreu um erro durante a alocação: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def exibir_resultado_alocacao(alocacoes):
    janela_resultado = tk.Toplevel(root)
    janela_resultado.title("Resultado da Alocação")

    frame_resultado = ttk.LabelFrame(janela_resultado, text="Alocação dos Períodos nas Salas")
    frame_resultado.pack(padx=10, pady=10, fill="both", expand=True)

    tree_resultado = ttk.Treeview(frame_resultado, columns=("Periodo", "Sala"), show="headings")
    tree_resultado.heading("Periodo", text="Período")
    tree_resultado.heading("Sala", text="Sala Alocada")
    tree_resultado.column("Periodo", width=150)
    tree_resultado.column("Sala", width=200)
    tree_resultado.pack(fill="both", expand=True)

    for periodo, salas in alocacoes.items():
        if salas == ["NÃO ALOCADO"]:
            tree_resultado.insert("", tk.END, values=(periodo, "NÃO FOI POSSÍVEL ALOCAR"))
        else:
            for sala in salas:
                tree_resultado.insert("", tk.END, values=(periodo, sala))

def janela_alocacao():
    global combo_periodo1, combo_sala_periodo1, combo_periodo2, combo_sala_periodo2, \
           combo_periodo3, combo_sala_periodo3, combo_periodo4, combo_sala_periodo4, \
           combo_sala_reposicao

    janela_alocar = tk.Toplevel(root)
    janela_alocar.title("Alocação de Períodos")

    # Frame para a seleção de períodos e salas
    frame_selecao = ttk.LabelFrame(janela_alocar, text="Selecionar Períodos e Salas para Alocação")
    frame_selecao.pack(padx=10, pady=10, fill="x")

    # --- Widgets para o Período 1 ---
    lbl_periodo1 = ttk.Label(frame_selecao, text="Período 1:")
    lbl_periodo1.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_periodo1 = ttk.Combobox(frame_selecao)
    combo_periodo1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    lbl_sala_periodo1 = ttk.Label(frame_selecao, text="Sala:")
    lbl_sala_periodo1.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    combo_sala_periodo1 = ttk.Combobox(frame_selecao)
    combo_sala_periodo1.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    # --- Widgets para o Período 2 ---
    lbl_periodo2 = ttk.Label(frame_selecao, text="Período 2:")
    lbl_periodo2.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    combo_periodo2 = ttk.Combobox(frame_selecao)
    combo_periodo2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    lbl_sala_periodo2 = ttk.Label(frame_selecao, text="Sala:")
    lbl_sala_periodo2.grid(row=1, column=2, padx=5, pady=5, sticky="w")
    combo_sala_periodo2 = ttk.Combobox(frame_selecao)
    combo_sala_periodo2.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

    # --- Widgets para o Período 3 ---
    lbl_periodo3 = ttk.Label(frame_selecao, text="Período 3:")
    lbl_periodo3.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    combo_periodo3 = ttk.Combobox(frame_selecao)
    combo_periodo3.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    lbl_sala_periodo3 = ttk.Label(frame_selecao, text="Sala:")
    lbl_sala_periodo3.grid(row=2, column=2, padx=5, pady=5, sticky="w")
    combo_sala_periodo3 = ttk.Combobox(frame_selecao)
    combo_sala_periodo3.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

    # --- Widgets para o Período 4 ---
    lbl_periodo4 = ttk.Label(frame_selecao, text="Período 4:")
    lbl_periodo4.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    combo_periodo4 = ttk.Combobox(frame_selecao)
    combo_periodo4.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    lbl_sala_periodo4 = ttk.Label(frame_selecao, text="Sala:")
    lbl_sala_periodo4.grid(row=3, column=2, padx=5, pady=5, sticky="w")
    combo_sala_periodo4 = ttk.Combobox(frame_selecao)
    combo_sala_periodo4.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

    # --- Widgets para Sala de Reposição ---
    lbl_sala_reposicao = ttk.Label(frame_selecao, text="Sala Reposição:")
    lbl_sala_reposicao.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    combo_sala_reposicao = ttk.Combobox(frame_selecao)
    combo_sala_reposicao.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    # Frame para a lista de Salas
    frame_salas_list = ttk.LabelFrame(janela_alocar, text="Salas Cadastradas")
    frame_salas_list.pack(padx=10, pady=10, fill="both", expand=True)

    tree_salas_alocacao = ttk.Treeview(frame_salas_list, columns=("Nome", "Capacidade", "Bloco"), show="headings")
    tree_salas_alocacao.heading("Nome", text="Nome da Sala")
    tree_salas_alocacao.heading("Capacidade", text="Capacidade")
    tree_salas_alocacao.heading("Bloco", text="Bloco")
    tree_salas_alocacao.column("Nome", width=150)
    tree_salas_alocacao.column("Capacidade", width=100)
    tree_salas_alocacao.column("Bloco", width=80)
    tree_salas_alocacao.pack(fill="both", expand=True)

    salas = obter_salas()
    if salas:
        sala_nomes = [f"{nome} (Cap: {capacidade}, Bloco: {bloco})" for id_sala, nome, capacidade, bloco, tipo in salas]
        combo_sala_periodo1['values'] = sala_nomes
        combo_sala_periodo2['values'] = sala_nomes
        combo_sala_periodo3['values'] = sala_nomes
        combo_sala_periodo4['values'] = sala_nomes
        combo_sala_reposicao['values'] = sala_nomes
        for _, nome, capacidade, bloco, _ in salas:
                tree_salas_alocacao.insert("", tk.END, values=(nome, capacidade, bloco))
    else:
        messagebox.showinfo("Informação", "Nenhuma sala cadastrada.")

    # Frame para a lista de Períodos
    frame_periodos_list = ttk.LabelFrame(janela_alocar, text="Períodos Cadastrados")
    frame_periodos_list.pack(padx=10, pady=10, fill="both", expand=True)

    tree_periodos_alocacao = ttk.Treeview(frame_periodos_list, columns=("Nome", "Alunos"), show="headings")
    tree_periodos_alocacao.heading("Nome", text="Nome do Período")
    tree_periodos_alocacao.heading("Alunos", text="Número de Alunos")
    tree_periodos_alocacao.column("Nome", width=150)
    tree_periodos_alocacao.column("Alunos", width=100)
    tree_periodos_alocacao.pack(fill="both", expand=True)

    periodos_data = obter_periodos()
    if periodos_data:
        periodos_nomes = [nome for nome, _, _ in periodos_data]
        combo_periodo1['values'] = periodos_nomes
        combo_periodo2['values'] = periodos_nomes
        combo_periodo3['values'] = periodos_nomes
        combo_periodo4['values'] = periodos_nomes
        for nome, alunos, _ in periodos_data:
            tree_periodos_alocacao.insert("", tk.END, values=(nome, alunos))
    else:
        messagebox.showinfo("Informação", "Nenhum período cadastrado.")

    btn_alocar = ttk.Button(janela_alocar, text="Realizar Alocação Manual e Automática", command=realizar_alocacao_completa)
    btn_alocar.pack(pady=10)

def realizar_alocacao_completa():
    periodo1_selecionado = combo_periodo1.get()
    sala1_selecionada_display = combo_sala_periodo1.get()
    periodo2_selecionado = combo_periodo2.get()
    sala2_selecionada_display = combo_sala_periodo2.get()
    periodo3_selecionado = combo_periodo3.get()
    sala3_selecionada_display = combo_sala_periodo3.get()
    periodo4_selecionado = combo_periodo4.get()
    sala4_selecionada_display = combo_sala_periodo4.get()
    sala_reposicao_selecionada_display = combo_sala_reposicao.get()

    alocacoes_manuais = {
        periodo1_selecionado: sala1_selecionada_display,
        periodo2_selecionado: sala2_selecionada_display,
        periodo3_selecionado: sala3_selecionada_display,
        periodo4_selecionado: sala4_selecionada_display,
    }

    conn = conectar_banco()
    cursor = conn.cursor()
    alocacoes_final = {}
    salas_ocupadas_ids = set()
    salas_especiais_disponiveis_ids = set() # Controlar salas especiais já alocadas

    try:
        cursor.execute("DELETE FROM alocacoes") # Limpa alocações anteriores
        conn.commit()

        salas_data = obter_salas()
        periodos_data = obter_periodos()

        salas_dict = {sala[0]: {'nome': sala[1], 'capacidade': sala[2], 'bloco': sala[3], 'tipo': sala[4], 'id': sala[0]} for sala in salas_data}
        periodos_dict = {periodo[0]: {'alunos': periodo[1], 'especiais': periodo[2], 'id': periodo[0]} for periodo in periodos_data}

        salas_especiais_disponiveis = {s_id: s_info for s_id, s_info in salas_dict.items() if s_info['tipo'] == 'Especial'}
        salas_comuns_disponiveis = {s_id: s_info for s_id, s_info in salas_dict.items() if s_info['tipo'] == 'Comum'}

        # --- ALOCAÇÃO DE ALUNOS ESPECIAIS ---
        for nome_periodo, info_periodo in periodos_dict.items():
            num_alunos_especiais = info_periodo['especiais']
            if num_alunos_especiais > 0:
                for i in range(num_alunos_especiais):
                    if salas_especiais_disponiveis:
                        sala_id_especial = next(iter(salas_especiais_disponiveis))
                        alocacoes_final[f"{nome_periodo} (Especial {i+1})"] = sala_id_especial
                        salas_ocupadas_ids.add(sala_id_especial)
                        salas_especiais_disponiveis_ids.add(sala_id_especial)
                        del salas_especiais_disponiveis[sala_id_especial]
                        print(f"Alocação Automática (Especial): Período '{nome_periodo}', Aluno {i+1} -> Sala ID '{sala_id_especial}'")
                    else:
                        messagebox.showwarning("Atenção", f"Não há salas especiais suficientes para todos os alunos especiais do período '{nome_periodo}'.")
                        break

        # --- ALOCAÇÃO MANUAL ---
        sala_ids_por_nome = {sala['nome']: sala['id'] for sala in salas_dict.values()}
        for periodo, sala_display in alocacoes_manuais.items():
            if periodo and sala_display:
                nome_sala_manual = sala_display.split(" (")[0]
                if nome_sala_manual in sala_ids_por_nome:
                    id_sala_manual = sala_ids_por_nome[nome_sala_manual]
                    if id_sala_manual not in salas_ocupadas_ids:
                        alocacoes_final[periodo] = id_sala_manual
                        salas_ocupadas_ids.add(id_sala_manual)
                        print(f"Alocação Manual: Período '{periodo}' -> Sala ID '{id_sala_manual}'")
                    else:
                        messagebox.showerror("Erro", f"A sala '{nome_sala_manual}' já está ocupada.")
                        conn.close()
                        return
                else:
                    messagebox.showerror("Erro", f"Sala '{nome_sala_manual}' não encontrada.")
                    conn.close()
                    return

        # --- ENSALAMENTO AUTOMÁTICO PARA OS PERÍODOS RESTANTES (REGULARES) ---
        periodos_para_alocar_regulares = []
        for nome, info in periodos_dict.items():
            num_alunos_regulares = info['alunos'] - info.get('especiais', 0)
            if nome not in alocacoes_final and num_alunos_regulares > 0:
                periodos_para_alocar_regulares.append((nome, num_alunos_regulares, info['id']))

        salas_disponiveis_regulares = {s_id: s_info for s_id, s_info in salas_comuns_disponiveis.items() if s_id not in salas_ocupadas_ids}

        periodos_para_alocar_regulares.sort(key=lambda x: x[1], reverse=True) # Aloca primeiro as turmas maiores

        for nome_periodo, num_alunos_regulares, periodo_id in periodos_para_alocar_regulares:
            alocado_periodo = False
            # Tentar alocar em uma única sala comum
            melhor_sala_comum = None
            menor_vagas_comum = float('inf')
            for sala_id, sala_info in salas_disponiveis_regulares.items():
                if sala_info['capacidade'] >= num_alunos_regulares:
                    vagas_ociosas = sala_info['capacidade'] - num_alunos_regulares
                    if vagas_ociosas < menor_vagas_comum:
                        menor_vagas_comum = vagas_ociosas
                        melhor_sala_comum = sala_info

            if melhor_sala_comum:
                alocacoes_final[nome_periodo] = melhor_sala_comum['id']
                salas_ocupadas_ids.add(melhor_sala_comum['id'])
                del salas_disponiveis_regulares[melhor_sala_comum['id']]
                print(f"Alocação Automática (Regular): Período '{nome_periodo}' -> Sala ID '{melhor_sala_comum['id']}'")
                alocado_periodo = True
            else:
                # Tentar dividir em duas salas comuns
                melhor_sala1_comum = None
                melhor_sala2_comum = None
                menor_vagas_combinadas_comum = float('inf')
                salas_list_regulares = list(salas_disponiveis_regulares.values())

                for i in range(len(salas_list_regulares)):
                    for j in range(i + 1, len(salas_list_regulares)):
                        sala1_comum = salas_list_regulares[i]
                        sala2_comum = salas_list_regulares[j]
                        capacidade_combinada_comum = sala1_comum['capacidade'] + sala2_comum['capacidade']

                        if capacidade_combinada_comum >= num_alunos_regulares:
                            vagas_ociosas_combinadas_comum = capacidade_combinada_comum - num_alunos_regulares
                            if vagas_ociosas_combinadas_comum < menor_vagas_combinadas_comum:
                                menor_vagas_combinadas_comum = vagas_ociosas_combinadas_comum
                                melhor_sala1_comum = sala1_comum
                                melhor_sala2_comum = sala2_comum

                if melhor_sala1_comum and melhor_sala2_comum:
                    alocacoes_final[f"{nome_periodo} (Parte 1)"] = melhor_sala1_comum['id']
                    alocacoes_final[f"{nome_periodo} (Parte 2)"] = melhor_sala2_comum['id']
                    salas_ocupadas_ids.add(melhor_sala1_comum['id'])
                    salas_ocupadas_ids.add(melhor_sala2_comum['id'])
                    if melhor_sala1_comum['id'] in salas_disponiveis_regulares:
                        del salas_disponiveis_regulares[melhor_sala1_comum['id']]
                    if melhor_sala2_comum['id'] in salas_disponiveis_regulares:
                        del salas_disponiveis_regulares[melhor_sala2_comum['id']]
                    print(f"Alocação Automática (Regular Dividida): Período '{nome_periodo}' -> Sala ID '{melhor_sala1_comum['id']}', Sala ID '{melhor_sala2_comum['id']}'")
                    alocado_periodo = True

            if not alocado_periodo:
                messagebox.showerror("Erro", f"Não foi possível alocar o período '{nome_periodo}' com {num_alunos_regulares} alunos regulares.")
                conn.rollback()
                conn.close()
                return

        # Salvar todas as alocações no banco de dados
        cursor.execute("DELETE FROM alocacoes") # Limpa novamente para garantir
        for periodo, id_sala in alocacoes_final.items():
            try:
                cursor.execute("INSERT INTO alocacoes (nome_periodo, id_sala) VALUES (?, ?)", (periodo, id_sala))
                conn.commit()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao salvar alocação do período '{periodo}': {e}")
                conn.close()
                return

        messagebox.showinfo("Sucesso", "Alocação realizada com sucesso!")
        exibir_resultados_alocacao()

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a alocação: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def exibir_resultados_alocacao():
    janela_resultados = tk.Toplevel(root)
    janela_resultados.title("Resultados da Alocação")

    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT nome_periodo, id_sala FROM alocacoes")
        alocacoes = cursor.fetchall()

        if alocacoes:
            tree_resultados = ttk.Treeview(janela_resultados, columns=("Período", "Sala"), show="headings")
            tree_resultados.heading("Período", text="Período")
            tree_resultados.heading("Sala", text="Sala")
            tree_resultados.column("Período", width=150)
            tree_resultados.column("Sala", width=150)
            tree_resultados.pack(padx=10, pady=10, fill="both", expand=True)

            for periodo, id_sala in alocacoes:
                cursor.execute("SELECT nome_sala FROM salas WHERE id_sala=?", (id_sala,))
                sala_resultado = cursor.fetchone()
                nome_sala = sala_resultado[0] if sala_resultado else "Sala não encontrada"
                tree_resultados.insert("", tk.END, values=(periodo, nome_sala))
        else:
            lbl_nenhuma_alocacao = ttk.Label(janela_resultados, text="Nenhuma alocação realizada.")
            lbl_nenhuma_alocacao.pack(padx=10, pady=10)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar os resultados da alocação: {e}")
    finally:
        if conn:
            conn.close()

def gerar_relatorio_alocacao():
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT nome_periodo FROM periodos ORDER BY nome_periodo")
        periodos = [row[0] for row in cursor.fetchall()]

        alocacoes_relatorio = {}

        cursor.execute("SELECT a.nome_periodo, GROUP_CONCAT(s.nome_sala, ', ') AS salas_alocadas "
                        "FROM alocacoes a "
                        "JOIN salas s ON a.id_sala = s.id_sala "
                        "GROUP BY a.nome_periodo")
        resultados = cursor.fetchall()
        for periodo, salas in resultados:
            alocacoes_relatorio[periodo] = salas

        janela_relatorio = tk.Toplevel(root)
        janela_relatorio.title("Relatório de Alocação")

        frame_relatorio = ttk.LabelFrame(janela_relatorio, text="Alocação dos Períodos")
        frame_relatorio.pack(padx=10, pady=10, fill="both", expand=True)

        texto_relatorio = tk.Text(frame_relatorio, height=15, width=60)
        texto_relatorio.pack(fill="both", expand=True)

        for periodo in periodos:
            salas_alocadas = alocacoes_relatorio.get(periodo, "NÃO ALOCADO")
            texto_relatorio.insert(tk.END, f"Período: {periodo} -> Salas: {salas_alocadas}\n")

        texto_relatorio.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o relatório: {e}")
    finally:
        if conn:
            conn.close()

def exportar_para_csv(tipo_dados):
    filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("Arquivo CSV", "*.csv"), ("Todos os arquivos", "*.*")])
    if not filename:
        return

    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if tipo_dados == "salas":
                cursor.execute("SELECT nome_sala, capacidade, bloco FROM salas")
                writer.writerow(["Nome da Sala", "Capacidade", "Bloco"])
                writer.writerows(cursor.fetchall())
                messagebox.showinfo("Sucesso", "Dados das salas exportados para CSV.")
            elif tipo_dados == "periodos":
                cursor.execute("SELECT nome_periodo, numero_alunos, num_alunos_especiais FROM periodos")
                writer.writerow(["Nome do Período", "Número de Alunos", "Alunos Especiais"])
                writer.writerows(cursor.fetchall())
                messagebox.showinfo("Sucesso", "Dados dos períodos exportados para CSV.")
            else:
                messagebox.showerror("Erro", "Tipo de dados inválido para exportação.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao exportar para CSV: {e}")
    finally:
        if conn:
            conn.close()

def janela_relatorios_exportacao():
    janela_rex = tk.Toplevel(root)
    janela_rex.title("Relatórios e Exportação")

    btn_relatorio = ttk.Button(janela_rex, text="Gerar Relatório de Alocação", command=gerar_relatorio_alocacao)
    btn_relatorio.pack(pady=10, padx=10, fill="x")

    btn_exportar_salas = ttk.Button(janela_rex, text="Exportar Salas para CSV", command=lambda: exportar_para_csv("salas"))
    btn_exportar_salas.pack(pady=5, padx=10, fill="x")

    btn_exportar_periodos = ttk.Button(janela_rex, text="Exportar Períodos para CSV", command=lambda: exportar_para_csv("periodos"))
    btn_exportar_periodos.pack(pady=5, padx=10, fill="x")

def janela_visualizacao_grafica():
    messagebox.showinfo("Em Construção", "A visualização gráfica estará disponível em uma versão futura.")

if __name__ == "__main__":
    conectar_banco()
    criar_tabela_salas()
    criar_tabela_periodos()
    alterar_tabela_salas_adicionar_bloco()
    from database import alterar_tabela_periodos_adicionar_alunos_especiais
    alterar_tabela_periodos_adicionar_alunos_especiais()
    from database import alterar_tabela_salas_adicionar_tipo # Importe aqui
    alterar_tabela_salas_adicionar_tipo() # Execute esta linha UMA VEZ

    

    root = tk.Tk()
    root.title("Gerenciador de Provas")

    menu_bar = tk.Menu(root)

    menu_cadastro = tk.Menu(menu_bar, tearoff=0)
    menu_cadastro.add_command(label="Salas", command=janela_cadastro_salas)
    menu_cadastro.add_command(label="Períodos", command=janela_cadastro_periodos)
    menu_bar.add_cascade(label="Cadastro", menu=menu_cadastro)

    menu_alocacao = tk.Menu(menu_bar, tearoff=0)
    menu_alocacao.add_command(label="Alocar Períodos", command=janela_alocacao)
    menu_bar.add_cascade(label="Alocação", menu=menu_alocacao)

    menu_relatorios = tk.Menu(menu_bar, tearoff=0)
    menu_relatorios.add_command(label="Relatórios e Exportação", command=janela_relatorios_exportacao)
    menu_relatorios.add_command(label="Visualização Gráfica", command=janela_visualizacao_grafica)
    menu_bar.add_cascade(label="Relatórios", menu=menu_relatorios)

    root.config(menu=menu_bar)
    root.mainloop()
