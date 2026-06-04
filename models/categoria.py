# Modelo da tabela categorias


class Categoria: #Representa uma categoria de transação.
    #Usado para buscar/inserir categorias no banco.

    
    @staticmethod
    def buscar_por_nome(cursor, nome_categoria): #Busca uma categoria pelo nome.
        #Retorna o ID se existir, None caso contrário.

        cursor.execute(
            'SELECT id_categoria FROM categorias WHERE nome_categoria = ?',
            (nome_categoria,)
        )
        resultado = cursor.fetchone()
        return resultado['id_categoria'] if resultado else None
    
    @staticmethod
    def criar(cursor, nome_categoria): #Cria uma nova categoria no banco.
        #Retorna o ID da categoria criada.

        cursor.execute(
            'INSERT INTO categorias (nome_categoria) VALUES (?)',
            (nome_categoria,)
        )
        return cursor.lastrowid