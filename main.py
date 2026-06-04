from flask import Flask, render_template, request, redirect, flash
# Flask: cria o servidor web
# render_template: envia arquivos HTML para o navegador
# request: pega os dados enviados pelo usuário (como o arquivo)
# redirect: redireciona o usuário para outra página
# flash permite enviar mensagens do backend para o frontend

from werkzeug.utils import secure_filename
# secure_filename: limpa o nome do arquivo para evitar ataques
import os
# os: permite trabalhar com pastas e arquivos do sistema

from ofxparse import OfxParser  
# biblioteca para ler OFX

import sqlite3
# sqlite3: biblioteca para conectar e manipular banco de dados SQLite
# Quando for usar MySQL, você vai trocar para: import mysql.connector

from datetime import datetime
# datetime: para trabalhar com datas e horários








# ============================================
# CONFIGURAÇÃO DO FLASK
# ============================================

app = Flask(__name__, static_folder='static')  # Cria a aplicação Flask
# static_folder='static': diz que CSS, JS e imagens estão na pasta 'static/'

app.secret_key = 'chave_secreta_123'  # O Flask usa a secret_key para criptografar os cookies do navegador.

UPLOAD_FOLDER = 'uploads'  # Define o nome da pasta onde os uploads serão salvos

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Salva essa configuração no app para usar depois

# Define quais extensões são permitidas (apenas OFX)
ALLOWED_EXTENSIONS = {'ofx'}


def allowed_file(filename):  # Verifica se o arquivo tem uma extensão permitida.
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if not os.path.exists(UPLOAD_FOLDER):  # Cria a pasta 'uploads' automaticamente se ela não existir
    os.makedirs(UPLOAD_FOLDER)
# Isso evita erro na primeira vez que rodar o código







# ============================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================


DB_NAME = 'meu_banco.db'

# Quando for usar MySQL, você vai mudar para algo assim:
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'seu_usuario',
#     'password': 'sua_senha',
#     'database': 'nome_do_banco'
# }


def conectar_banco():
    """
    Conecta ao banco de dados e retorna a conexão.
    Atualmente usa SQLite, depois você muda para MySQL.
    """
    # ===== SQLITE (AGORA) =====
    conexao = sqlite3.connect(DB_NAME)
    conexao.row_factory = sqlite3.Row  # Permite acessar colunas por nome (ex: resultado['id'])
    return conexao
    
    # ===== MYSQL (DEPOIS) =====
    # conexao = mysql.connector.connect(**DB_CONFIG)
    # return conexao


def criar_tabelas():
    """
    Cria as tabelas no banco se elas ainda não existirem.
    Essa função é executada automaticamente quando o app inicia.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Tabela: categorias (armazena os nomes das categorias)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_categoria TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabela: importacoes (registra cada arquivo OFX importado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS importacoes (
            id_importacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            nome_arquivo TEXT NOT NULL,
            data_importacao DATE NOT NULL,
            mes_referencia VARCHAR(7)
        )
    ''')
    
    # Tabela: transacoes (armazena cada transação do extrato)
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
    
    conexao.commit()
    cursor.close()
    conexao.close()


# Cria as tabelas automaticamente quando o app inicia
criar_tabelas()


def inicializar_categorias():
    """
    Garante que todas as categorias padrão existam no banco.
    Verifica se existe antes de tentar criar.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    categorias_padrao = list(CATEGORIAS.keys()) + ['Outros']
    
    print("\n" + "="*60)
    print("📦 VERIFICANDO CATEGORIAS NO BANCO")
    print("="*60)
    
    for nome in categorias_padrao:
        # 1. Verifica se já existe
        cursor.execute(
            'SELECT id_categoria FROM categorias WHERE nome_categoria = ?',
            (nome,)
        )
        
        # 2. Se não existir, cria
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










# ============================================
# FUNÇÕES DE SALVAMENTO NO BANCO
# ============================================

def salvar_categoria(nome_categoria):
    """
    Busca o ID de uma categoria no banco.
    Se não existir, cria e retorna o novo ID.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # 1. Tenta buscar a categoria pelo nome
        cursor.execute(
            'SELECT id_categoria FROM categorias WHERE nome_categoria = ?',
            (nome_categoria,)
        )
        resultado = cursor.fetchone()
        
        # 2. Se encontrou, retorna o ID
        if resultado:
            return resultado['id_categoria']
        
        # 3. Se não encontrou, cria a categoria
        cursor.execute(
            'INSERT INTO categorias (nome_categoria) VALUES (?)',
            (nome_categoria,)
        )
        conexao.commit()
        
        # 4. Retorna o ID que foi criado automaticamente
        return cursor.lastrowid
        
    finally:
        cursor.close()
        conexao.close()


def salvar_importacao(nome_arquivo, data_importacao, mes_referencia, id_usuario=1):
    """
    Salva os dados da importação do arquivo no banco.
    Retorna o id_importacao gerado automaticamente.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # INSERT SEM o id_importacao (o banco cria sozinho com AUTOINCREMENT)
        cursor.execute('''
            INSERT INTO importacoes (id_usuario, nome_arquivo, data_importacao, mes_referencia)
            VALUES (?, ?, ?, ?)
        ''', (id_usuario, nome_arquivo, data_importacao, mes_referencia))
        
        conexao.commit()
        
        # Pega o ID que o banco acabou de criar automaticamente
        return cursor.lastrowid
        
    finally:
        cursor.close()
        conexao.close()


def salvar_transacao(id_importacao, id_categoria, descricao, valor, data_transacao, tipo, fitid):
    """
    Salva uma transação individual no banco.
    O id_transacao é gerado automaticamente pelo banco.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # INSERT SEM o id_transacao (o banco cria sozinho com AUTOINCREMENT)
        cursor.execute('''
            INSERT INTO transacoes 
            (id_importacao, id_categoria, descricao, valor, data_transacao, tipo, fitid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id_importacao, id_categoria, descricao, valor, data_transacao, tipo, fitid))
        
        conexao.commit()
        
    except Exception as e:
        print(f"   [ERRO] Ao salvar transação: {e}")
        conexao.rollback()  # Desfaz a transação em caso de erro
    finally:
        cursor.close()
        conexao.close()









# ============================================
# SISTEMA DE CATEGORIZAÇÃO
# ============================================

# Dicionário de categorias com palavras-chave
# Cada categoria tem uma lista de palavras que, se encontradas na descrição,
# atribui essa categoria à transação


def determinar_tipo_transacao(valor):
    """
    Retorna 'Entrada' se valor positivo, 'Saída' se negativo.
    """
    if valor > 0:
        return 'Entrada'
    else:
        return 'Saída'


CATEGORIAS = {
    # ENTRADAS
    'Salário': ['salario', 'salário', 'pagamento salario', 'folha'],
    'Extras': ['bonus', 'bônus', 'comissao', 'comissão', 'adicional', 'extra'],
    'Rendimentos': ['rendimento', 'dividendo', 'juros sobre capital', 'renda'],
    
    # SAÍDAS - ESSENCIAIS
    'Moradia': ['aluguel', 'financiamento', 'condominio', 'condomínio', 'iptu'],
    'Contas Fixas': ['telefone', 'telsp', 'celul', 'celular', 'vivo', 'tim', 'claro', 'oi', 'streaming', 'luz', 'agua', 'água', 'gas', 'gás', 'internet', 'netflix', 'spotify', 'tv', 'fatura', 'boleto', 'assinatura'],
    'Transferências': ['transferência', 'transferencia', 'pix', 'ted', 'doc'],
    'Supermercado': ['supermercado', 'mercado', 'extra', 'pao de acucar', 'pão de açúcar', 'carrefour', 'atacadao', 'atacadão', 'shibata', 'rossi', 'açai atacadista', 'açaí atacadista', 'compras'],
    'Saúde': ['farmacia', 'farmácia', 'droga', 'consulta', 'medico', 'médico', 'plano de saude', 'plano de saúde', 'hospital', 'clinica', 'clínica'],
    'Transporte': ['uber', '99 taxi', '99 pop', '99 moto', 'cabify', 'combustivel', 'combustível', 'posto', 'estacionamento', 'pedagio', 'pedágio', 'onibus', 'ônibus', 'metro', 'metrô'],
    
    # SAÍDAS - VARIÁVEIS
    'Educação': ['curso', 'livro', 'faculdade', 'universidade', 'escola', 'material escolar', 'udemy', 'alura'],
    'Lazer e Entretenimento': ['restaurante', 'cinema', 'bar', 'show', 'ifood', 'rappi', 'pizza', 'hamburger', 'hambúrguer', 'cafe', 'ingresso', 'cinema', 'café'],
    'Viagens e Turismo': ['hotel', 'passagem', 'hospedagem', 'airbnb', 'booking', 'gol', 'latam', 'azul'],
    'Cuidados Pessoais': ['salao', 'salão', 'barbearia', 'vestuario', 'vestuário', 'roupa', 'calcado', 'calçado', 'cosmetico', 'cosmético'],
}


inicializar_categorias() #chamadndo a função pra criar as categorias no banco



def categorizar_transacao(descricao):
    """
    Recebe a descrição da transação e retorna a categoria correspondente.
    Se não encontrar match, retorna 'Outros'.
    """
    if not descricao:
        return 'Outros'
    
    # Converte para minúsculo para comparação 
    descricao_lower = descricao.lower()
    
    # Percorre cada categoria e suas palavras-chave
    for categoria, palavras_chave in CATEGORIAS.items():
        # a variável categoria recebe o nome da categoria e palavras_chave recebe a lista de palavras daquela categoria
        for palavra in palavras_chave:
            if palavra in descricao_lower:
                return categoria
    
    # Se não encontrou nenhuma palavra-chave
    return 'Outros'









# ============================================
# ROTAS - URLs que o Flask vai responder
# ============================================

@app.route("/")  # Rota da página inicial: quando acessar http://127.0.0.1:5001/
def index():
    return render_template('index.html')  # render_template procura o arquivo em: templates/index.html


@app.route('/upload', methods=['POST'])  # Rota do upload: quando o formulário enviar para /upload via POST
def upload():

    # 1️⃣ Verifica se veio um arquivo na requisição
    if 'file' not in request.files:  # request.files é um dicionário com todos os arquivos enviados

        flash('❌ Nenhum arquivo foi enviado.', 'erro')
        return redirect('/')  # Se não tiver arquivo, volta pra página inicial
    
    # 2️⃣ Pega o arquivo enviado (o nome 'file' deve bater com o name="" do input no html)
    file = request.files['file']
    
    # 3️⃣ Verifica se o usuário selecionou um arquivo (não deixou vazio)
    if file.filename == '':
        return redirect('/')
    
    # 4️⃣ Limpa o nome do arquivo para segurança
    # Remove caracteres perigosos como / \ .. etc.
    filename = secure_filename(file.filename)

    # 5️⃣ validação de tipo de arquivo
    if not allowed_file(filename):

        print(f'❌ O arquivo "{filename}" não é um OFX válido. Apenas arquivos .ofx são permitidos.')

        flash(f'O arquivo "{filename}" não é um OFX válido. Apenas arquivos .ofx são permitidos.', 'erro')
        
        return redirect('/')  # Volta para a tela inicial sem salvar nada

    # 6️⃣ Cria o caminho completo: "uploads/meu_arquivo.pdf" e salva o arquivo no disco
    filepath = os.path.join(UPLOAD_FOLDER, filename)  # ← Cria a variável
    file.save(filepath)











# ==========================================
# LEITURA OFX E CATEGORIZAÇÃO
# ==========================================
    # Verifica se o arquivo é .ofx antes de tentar ler
    if filename.lower().endswith('.ofx'):
        print("🔍 Tentando ler arquivo OFX...")
        try:
            # Abre o arquivo OFX que acabou de ser salvo
            with open(filepath, 'rb') as ofx_file:
                print("📖 Arquivo aberto com sucesso!")
                ofx = OfxParser.parse(ofx_file)
                print("✅ OFX parseado com sucesso!")

            
            conta = ofx.account    # Acessa a conta (geralmente só tem uma no arquivo)

            extrato = conta.statement  # Acessa o extrato




            # ==========================================
            # SALVAR IMPORTAÇÃO NO BANCO
            # ==========================================
            
            # Prepara os dados da importação
            data_importacao = datetime.now().strftime('%Y-%m-%d')  # Data de hoje no formato AAAA-MM-DD
            mes_referencia = datetime.now().strftime('%Y-%m')  # Mês/ano no formato AAAA-MM
            
            # Salva a importação no banco e pega o ID gerado
            id_importacao = salvar_importacao(
                nome_arquivo=filename,
                data_importacao=data_importacao,
                mes_referencia=mes_referencia,
                id_usuario=1  # ← Quando tiver login, muda para o ID do usuário logado
            )
            
            print(f"💾 Importação salva no banco com ID: {id_importacao}")


            # Contadores para resumo
            total_entradas = 0
            total_saidas = 0
            transacoes_por_categoria = {}


            print("\n" + "="*80)
            print(f"📄 ARQUIVO: {filename}")
            print("="*80)
            print(f"🏦 Banco: {conta.institution.organization if conta.institution else 'N/A'}")
            print(f"💳 Conta: {conta.account_id}")
            print(f"💰 Saldo: R$ {extrato.balance}")
            print("="*80)
            print(f"{'📋 TRANSAÇÕES CATEGORIZADAS':^80}")
            print("="*80)
            print(f"{'DATA':<12} {'DESCRIÇÃO':<45} {'VALOR':>10} {'TIPO':<10} {'CATEGORIA':<20}")
            print("-"*80)


            # Percorre todas as transações do extrato
            for transaction in extrato.transactions:
                # Pega a descrição (memo é mais detalhado, payee é o nome)
                descricao = transaction.memo or transaction.payee or "Sem descrição"
                
                # Formata o valor com 2 casas decimais
                valor = float(transaction.amount)

                # Determina o tipo
                tipo = determinar_tipo_transacao(valor)
            
                # Categoriza
                categoria_nome = categorizar_transacao(descricao)

                # Formata a data (se existir)
                data = transaction.date.strftime('%d/%m/%Y') if transaction.date else 'N/A'
                
                # Imprime formatado
                print(f"{data:<12} {descricao:<45} R$ {valor:>8.2f} {tipo:<10} {categoria_nome:<20}")




                # ==========================================
                # SALVAR TRANSAÇÃO NO BANCO
                # ==========================================
                
                # Busca ou cria a categoria no banco e pega o ID
                id_categoria = salvar_categoria(categoria_nome)
                
                # Formata a data para o banco (AAAA-MM-DD)
                data_transacao = transaction.date.strftime('%Y-%m-%d') if transaction.date else None
                
                # Pega o fitid (identificador único da transação no OFX)
                fitid = getattr(transaction, 'fitid', None)
                
                # Salva a transação no banco
                salvar_transacao(
                    id_importacao=id_importacao,
                    id_categoria=id_categoria,
                    descricao=descricao,
                    valor=valor,
                    data_transacao=data_transacao,
                    tipo=tipo,
                    fitid=fitid
                )


                # Atualiza contadores
                if valor > 0:
                    total_entradas += valor
                else:
                    total_saidas += abs(valor)  # abs deixa o valor positivo


                # Conta transações por categoria
                if categoria_nome not in transacoes_por_categoria:  # Verifica se essa categoria ainda não existe no dicionário
                    transacoes_por_categoria[categoria_nome] = {'qtd': 0, 'valor': 0}  # cria uma nova entrada no dicionário principal, começando do zero.
            
                transacoes_por_categoria[categoria_nome]['qtd'] += 1  # Incrementa a quantidade de transações dessa categoria
                transacoes_por_categoria[categoria_nome]['valor'] += abs(valor)
                # Soma o valor dessa transação ao total da categoria.


            # Resumo por categoria
            print("\n" + "="*80)
            print(f"{'RESUMO POR CATEGORIA':^80}")
            print("="*80)
        
            for categoria, dados in sorted(transacoes_por_categoria.items()):
                print(f"{categoria:<30} {dados['qtd']} transações    R$ {dados['valor']:>10.2f}")

            print(f"{'TOTAL ENTRADAS:':<30} R$ {total_entradas:>10.2f}")
            print(f"{'TOTAL SAÍDAS:':<30} R$ {total_saidas:>10.2f}")
            print(f"{'SALDO FINAL:':<30} R$ {extrato.balance:>10.2f}")
            print("="*80 + "\n")

            print(f'✅ Arquivo "{filename}" processado com sucesso! transações salvas no banco.')

            flash(f'✅ Arquivo "{filename}" processado com sucesso! transações salvas no banco.', 'sucesso')

        except Exception as e:
            print(f"❌ Erro ao ler OFX: {type(e).__name__}")
            print(f"❌ Detalhes: {e}")
            import traceback
            traceback.print_exc()
            flash(f'❌ Erro ao processar o arquivo.', 'erro')
    
    else:
        print(f"⚠️  Arquivo {filename} não é um OFX. Apenas salvo.")
    
    # 3️⃣ Volta para a página inicial
    return redirect('/')









# ==========================================
# INÍCIO DO SERVIDOR
# ==========================================
# Este bloco só roda se o arquivo for executado diretamente
# (não se for importado por outro arquivo)

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # mostra erros detalhados e recarrega ao salvar o arquivo

    # usa a porta 5001 (para não conflitar com outras coisas)