# Quando for usar MySQL:

import sqlite3 # import mysql.connector
from config import Config




def conectar_banco(): #Conecta ao banco de dados e retorna a conexão.
    #Atualmente usa SQLite, depois você muda para MySQL.

    # SQLITE (AGORA)
    conexao = sqlite3.connect(Config.DB_NAME)
    conexao.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conexao
    
    # MYSQL (DEPOIS)
    # conexao = mysql.connector.connect(
    #     host='localhost',
    #     user='seu_usuario',
    #     password='sua_senha',
    #     database='nome_do_banco'
    # )
    # return conexao


def criar_tabelas(): #Cria as tabelas no banco se elas ainda não existirem.
    #Executada automaticamente na inicialização do app.

    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Tabela: categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_categoria TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabela: importacoes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS importacoes (
            id_importacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            nome_arquivo TEXT NOT NULL,
            data_importacao DATE NOT NULL,
            mes_referencia VARCHAR(7)
        )
    ''')
    
    # Tabela: transacoes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id_transacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_importacao INTEGER NOT NULL,
            id_categoria INTEGER,
            descricao TEXT,
            valor REAL NOT NULL,
            data_transacao DATE,
            tipo TEXT NOT NULL,
            fitid TEXT,
            FOREIGN KEY (id_importacao) REFERENCES importacoes(id_importacao),
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        )
    ''')
    
    # Tabela: configuracoes (chave/valor para orçamento e futuras configurações)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    ''')
    # Garante valor padrão para orçamento
    cursor.execute(
        "INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES ('orcamento_mensal', '0')"
    )

    conexao.commit()
    cursor.close()
    conexao.close()


def inicializar_categorias(categorias_dict): #Garante que todas as categorias padrão existam no banco.

    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    categorias_padrao = list(categorias_dict.keys()) + ['Outros']
    
    print("\n" + "="*60)
    print("📦 VERIFICANDO CATEGORIAS NO BANCO")
    print("="*60)
    
    for nome in categorias_padrao:
        # Verifica se já existe
        cursor.execute(
            'SELECT id_categoria FROM categorias WHERE nome_categoria = ?',
            (nome,)
        )
        
        # Se não existir, cria
        if cursor.fetchone() is None:
            cursor.execute(
                'INSERT INTO categorias (nome_categoria) VALUES (?)',
                (nome,)
            )
            print(f"✅ Categoria '{nome}' criada")
        else:
            print(f"⚠️  Categoria '{nome}' já existe")
    
    conexao.commit()
    cursor.close()
    conexao.close()
    print("="*60 + "\n")