import os
import sys
import datetime as dt
import sqlite3
import tkinter as tk
from tkinter import messagebox as tk_mb
from tkinter import ttk

db_main = 'databasement/database_main.db'
sql_create_table = 'sql_files/create_table.sql'
sql_inserter = 'sql_files/inserter.sql'
sql_deleter = 'sql_files/deleter.sql'

def get_turno_atual():
    hora = dt.datetime.now().hour
    if 6 <= hora < 14:
        return "T1"
    elif 14 <= hora < 22:
        return "T2"
    else:
        return "T3" 

#inicio do codigo de verificação de caminhos e arquivos.
def check_paths_and_files():
    try:
        #banco de dados path e arquivos serão verificados
        if not os.path.exists('databasement'):
            os.makedirs('databasement')

        if not os.path.exists(db_main):
            open(db_main, 'a').close()

        #sql path e files serão verificados
        if not os.path.exists('sql_files'):
            os.makedirs('sql_files')

        if not os.path.exists(sql_create_table):
            with open(sql_create_table, 'w') as f:
                f.write("""
                    CREATE TABLE IF NOT EXISTS buffer (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_position TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        turn TEXT NOT NULL,
                        type_position TEXT NOT NULL,
                        category_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        insert_by TEXT NOT NULL,
                        status TEXT NOT NULL);
                    
                    CREATE TABLE IF NOT EXISTS category(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL UNIQUE);

                    CREATE TABLE IF NOT EXISTS buffer_history(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        day DATE NOT NULL,
                        quantity INTEGER NOT NULL);
                """)

        if not os.path.exists(sql_inserter):
            with open(sql_inserter, 'w') as f:
                f.write("""
                """)
            
        if not os.path.exists(sql_deleter):
            with open(sql_deleter, 'w') as f:
                f.write("""
                """)
            
    except Exception as e:
        print(f"Error checking paths and files: {e}")
        sys.exit(1)

check_paths_and_files()
# fim do código para verificar se os diretórios e arquivos existentes.


try:
    conn = sqlite3.connect(db_main)
    cursor = conn.cursor()

    with open(sql_create_table, 'r') as f:
        tb_script = f.read()
        cursor.executescript(tb_script)


except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)


try:
    class main_app(tk.Tk):

        def __init__(self):

            super().__init__()
            self.title("Buffer Management System")
            self.geometry("800x500")
            self.resizable(False, False)
            self.protocol("WM_DELETE_WINDOW", self.on_closing)

            ttk_nb = ttk.Notebook(self)
            ttk_nb.pack(expand=True, fill="both")

            # --- Aba 1: Visualizar ---
            frame_view = ttk.Frame(ttk_nb)
            ttk_nb.add(frame_view, text="Visualizar")

            tree_frame = ttk.Frame(frame_view)
            tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

            columns = ("id", "id_position", "timestamp", "turn", "type_position", "category_id", "quantity", "insert_by", "status")

            h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
            h_scroll.pack(side="bottom", fill="x")

            v_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
            v_scroll.pack(side="right", fill="y")

            self.tree = ttk.Treeview(
                tree_frame, 
                columns=columns, 
                show="headings", 
                height=15,
                xscrollcommand=h_scroll.set, 
                yscrollcommand=v_scroll.set)
            
            self.tree.pack(fill="both", expand=True)
            h_scroll.config(command=self.tree.xview)
            v_scroll.config(command=self.tree.yview)

            for col in columns:
                self.tree.heading(col, text=col.replace("_", " ").title(), anchor="center")
                self.tree.column(col, width=130, minwidth=60, stretch=False, anchor="center")

            tk.Button(frame_view, text="Atualizar", command=self.carregar_dados).pack(pady=5)

            self.inserir_categorias_padrao()

            # --- Aba 2: Adicionar ---
            frame_add = ttk.Frame(ttk_nb)
            ttk_nb.add(frame_add, text="Adicionar")

            tk.Label(frame_add, text="ID Position:").pack(pady=2)
            self.id_position = tk.Entry(frame_add, width=30)
            self.id_position.pack(pady=2)

            tk.Label(frame_add, text="Turno:").pack(pady=2)
            self.turn = tk.Label(frame_add, text=get_turno_atual(), 
                                relief="sunken", width=30, anchor="center")
            self.turn.pack(pady=2)   

            tk.Label(frame_add, text="Type Position:").pack(pady=2)
            self.type_position_var = tk.StringVar()
            self.type_position_combo = ttk.Combobox(
                frame_add,
                width=28,
                textvariable=self.type_position_var,
                values=["Scuttler", "Pallet", "Gaiola", "Saca"],
                state="readonly"
            )
            self.type_position_combo.pack(pady=2)

            tk.Label(frame_add, text="Categoria:").pack(pady=2)

            self.category_var = tk.StringVar()

            self.category_combo = ttk.Combobox(
                frame_add,
                width=28,
                textvariable=self.category_var,
                state="readonly"
            )
            self.category_combo.pack(pady=2)

            tk.Label(frame_add, text="Insert By:").pack(pady=2)
            self.insert_by = tk.Entry(frame_add, width=30)
            self.insert_by.pack(pady=2)
            
            tk.Button(frame_add, text="Adicionar", 
                    command=self.adicionar_registro).pack(side="left", expand=True, padx=10)
            tk.Button(frame_add, text="Limpar", 
                    command=self.limpar_campos).pack(side="right", expand=True, padx=10)

            self.carregar_categorias()
            self.carregar_dados()
  
        def limpar_campos(self):
            self.id_position.delete(0, tk.END)
            self.insert_by.delete(0, tk.END)

            self.type_position_var.set("")
            self.category_var.set("")

        def adicionar_registro(self):
            try:
                nome_categoria = self.category_var.get()
                tipo_posicao = self.type_position_var.get()

                if not nome_categoria:
                    tk_mb.showwarning("Aviso", "Selecione uma categoria")
                    return

                if not tipo_posicao:
                    tk_mb.showwarning("Aviso", "Selecione o tipo de posição")
                    return

                category_id = self.category_map[nome_categoria]

                cursor.execute("""
                    INSERT INTO buffer (id_position, turn, type_position, category_id, quantity, insert_by, status)
                    VALUES (?, ?, ?, ?, 1, ?, 'AGUARDANDO')
                """, (
                    self.id_position.get(),
                    self.turn.cget('text'),
                    tipo_posicao,
                    category_id,
                    self.insert_by.get()
                ))

                conn.commit()
                tk_mb.showinfo("Sucesso", "Registro adicionado com sucesso!")
                self.limpar_campos()

            except Exception as e:
                tk_mb.showerror("Erro", f"Erro ao adicionar: {e}")

        def carregar_dados(self):
            # Limpa a tabela
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Busca no banco
            try:
                cursor.execute("SELECT * FROM buffer")
                rows = cursor.fetchall()
                for row in rows:
                    self.tree.insert("", "end", values=row)
            except Exception as e:
                tk_mb.showerror("Erro", f"Erro ao carregar dados: {e}")

        def carregar_categorias(self):
            cursor.execute("SELECT id, category FROM category")
            rows = cursor.fetchall()

            self.category_map = {nome: id_ for id_, nome in rows}

            self.category_combo["values"] = list(self.category_map.keys())

        def inserir_categorias_padrao(self):
            categorias = [
                "Tratativa", "Liquidation", "STN", "Fora de Perfil",
                "Quarentena", "LAM-02", "CTE", "Devolução 3PL",
                "Devolução Azul", "SPP Pacotinho", "SPP Volumoso", "Inventario"
            ]

            for cat in categorias:
                cursor.execute("""
                    INSERT OR IGNORE INTO category (category)
                    VALUES (?)
                """, (cat,))
            
            conn.commit()

        def on_closing(self):
            conn.commit()
            conn.close()
            self.destroy()

    main_app().mainloop()

except Exception as e:
    print(f"Error initializing the application: {e}")
    sys.exit(1)