from models.categoria import Categoria
from models.importacao import Importacao
from models.transacao import Transacao
from services.database import conectar_banco


def salvar_importacao_db(nome_arquivo, data_importacao, mes_referencia, id_usuario=1): #Salva os dados da importação do arquivo no banco.
    #Retorna o id_importacao gerado automaticamente.

    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        id_importacao = Importacao.criar(
            cursor, 
            id_usuario, 
            nome_arquivo, 
            data_importacao, 
            mes_referencia
        )
        
        conexao.commit()
        return id_importacao
        
    finally:
        cursor.close()
        conexao.close()


def salvar_categoria_db(nome_categoria): #Busca o ID de uma categoria no banco.
    #Se não existir, cria e retorna o novo ID.

    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # Tenta buscar a categoria pelo nome
        id_categoria = Categoria.buscar_por_nome(cursor, nome_categoria)
        
        # Se não encontrou, cria a categoria
        if id_categoria is None:
            id_categoria = Categoria.criar(cursor, nome_categoria)
            conexao.commit()
        
        return id_categoria
        
    finally:
        cursor.close()
        conexao.close()


def salvar_transacao_db(id_importacao, id_categoria, descricao, valor,data_transacao, tipo, fitid):  #Salva uma transação individual no banco.

    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        Transacao.criar(
            cursor, 
            id_importacao, 
            id_categoria, 
            descricao, 
            valor, 
            data_transacao, 
            tipo, 
            fitid
        )
        
        conexao.commit()
        
    except Exception as e:
        print(f"   [ERRO] Ao salvar transação: {e}")
        conexao.rollback()  # Desfaz a transação em caso de erro
    finally:
        cursor.close()
        conexao.close()