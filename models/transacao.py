# Modelo da tabela transacoes


class Transacao: #Representa uma transação bancária.
    #Cada linha do extrato OFX vira uma transação.

    @staticmethod
    def criar(cursor, id_importacao, id_categoria, descricao, valor, 
    data_transacao, tipo, fitid): #Cria uma nova transação no banco.

        cursor.execute('''
            INSERT INTO transacoes 
            (id_importacao, id_categoria, descricao, valor, 
             data_transacao, tipo, fitid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id_importacao, id_categoria, descricao, valor, 
              data_transacao, tipo, fitid))