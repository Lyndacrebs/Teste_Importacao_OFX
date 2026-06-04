from ofxparse import OfxParser


def ler_arquivo_ofx(caminho_arquivo): #Lê e parseia um arquivo OFX.
    #Retorna o objeto OFX parseado.

    print("🔍 Tentando ler arquivo OFX...")
    
    with open(caminho_arquivo, 'rb') as ofx_file:
        print("📖 Arquivo aberto com sucesso!")
        ofx = OfxParser.parse(ofx_file)
        print("✅ OFX parseado com sucesso!")
    
    return ofx


def extrair_transacoes(ofx): #Extrai todas as transações do objeto OFX.
    #Retorna uma lista de dicionários com os dados das transações.

    conta = ofx.account
    extrato = conta.statement
    transacoes = []
    
    for transaction in extrato.transactions: # Percorre todas as transações do extrato
        
        transacao = {
            'descricao': transaction.memo or transaction.payee or "Sem descrição", # Pega a descrição (memo é mais detalhado, payee é o nome)
            'valor': float(transaction.amount),  # Formata o valor com 2 casas decimais
            'data': transaction.date.strftime('%d/%m/%Y') if transaction.date else 'N/A',
            'data_transacao': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
            'fitid': getattr(transaction, 'fitid', None)
        }
        transacoes.append(transacao)
    
    return transacoes


def obter_info_conta(ofx): # Obtém informações da conta bancária.
    conta = ofx.account # Acessa a conta (geralmente só tem uma no arquivo)
    extrato = conta.statement # Acessa o extrato
    
    return {
        'banco': conta.institution.organization if conta.institution else 'N/A',
        'conta': conta.account_id,
        'saldo': extrato.balance
    } 