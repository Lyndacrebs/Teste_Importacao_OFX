# Modelo da tabela importacoes


class Importacao: #Representa uma importação de arquivo OFX.
    #Cada arquivo enviado gera um registro nesta tabela.

    
    @staticmethod
    def criar(cursor, id_usuario, nome_arquivo, data_importacao, mes_referencia): #Cria um novo registro de importação.
        #Retorna o ID da importação criada.

        cursor.execute('''
            INSERT INTO importacoes 
            (id_usuario, nome_arquivo, data_importacao, mes_referencia)
            VALUES (?, ?, ?, ?)
        ''', (id_usuario, nome_arquivo, data_importacao, mes_referencia))
        
        return cursor.lastrowid