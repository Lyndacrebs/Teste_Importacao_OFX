from flask import Blueprint, request, redirect, flash, render_template
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import Config
from services.leitor_ofx import ler_arquivo_ofx, extrair_transacoes, obter_info_conta
from services.categorizador import categorizar_transacao, determinar_tipo_transacao, CATEGORIAS
from services.salvar_transacoes import (
    salvar_importacao_db, 
    salvar_categoria_db, 
    salvar_transacao_db
)
from services.database import inicializar_categorias

# Cria um Blueprint (grupo de rotas)
importacao_bp = Blueprint('importacao', __name__)


def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@importacao_bp.route('/')
def index():
    """Rota da página inicial."""
    return render_template('index.html')


@importacao_bp.route('/upload', methods=['POST'])
def upload():
    """
    Rota de upload de arquivos OFX.
    Processa o arquivo, categoriza as transações e salva no banco.
    """
    
    # 1. Verifica se veio um arquivo na requisição
    if 'file' not in request.files: # request.files é um dicionário com todos os arquivos enviados
        flash('❌ Nenhum arquivo foi enviado.', 'erro')
        return redirect('/') # Se não tiver arquivo, volta pra página inicial
    
    # 2️. Pega o arquivo enviado (o nome 'file' deve bater com o name="" do input no html)
    file = request.files['file']
    
    # 3️. Verifica se o usuário selecionou um arquivo (não deixou vazio)
    if file.filename == '':
        return redirect('/')
    
    # 4️. Limpa o nome do arquivo para segurança
    # Remove caracteres perigosos como / \ .. etc.
    filename = secure_filename(file.filename)
    
    # 5️. Validação de tipo de arquivo
    if not allowed_file(filename):
        print(f'❌ O arquivo "{filename}" não é um OFX válido.')
        flash(f'O arquivo "{filename}" não é um OFX válido.', 'erro')
        return redirect('/') # Volta para a tela inicial sem salvar nada
    
    # 6️. Cria o caminho completo: "uploads/meu_arquivo.pdf" e salva o arquivo no disco
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename) # ← Cria a variável
    file.save(filepath)
    
    # 7️. Processa o arquivo OFX
    if filename.lower().endswith('.ofx'):
        try:
            # Lê o arquivo OFX
            ofx = ler_arquivo_ofx(filepath)
            
            # Extrai informações da conta
            info_conta = obter_info_conta(ofx)
            
            # Extrai transações
            transacoes = extrair_transacoes(ofx)
            
            # Salva a importação no banco
            data_importacao = datetime.now().strftime('%Y-%m-%d')
            mes_referencia = datetime.now().strftime('%Y-%m')
            
            id_importacao = salvar_importacao_db(
                nome_arquivo=filename,
                data_importacao=data_importacao,
                mes_referencia=mes_referencia,
                id_usuario=1
            )
            
            print(f"💾 Importação salva no banco com ID: {id_importacao}")
            
            # Contadores para resumo
            total_entradas = 0
            total_saidas = 0
            transacoes_por_categoria = {}
            
            # Imprime cabeçalho
            print("\n" + "="*80)
            print(f"📄 ARQUIVO: {filename}")
            print("="*80)
            print(f"🏦 Banco: {info_conta['banco']}")
            print(f"💳 Conta: {info_conta['conta']}")
            print(f"💰 Saldo: R$ {info_conta['saldo']}")
            print("="*80)
            print(f"{'📋 TRANSAÇÕES CATEGORIZADAS':^80}")
            print("="*80)
            print(f"{'DATA':<12} {'DESCRIÇÃO':<45} {'VALOR':>10} {'TIPO':<10} {'CATEGORIA':<20}")
            print("-"*80)
            
            # Percorre todas as transações do extrato
            for transacao in transacoes: # Pega a descrição (memo é mais detalhado, payee é o nome)
                descricao = transacao['descricao']
                valor = transacao['valor']
                tipo = determinar_tipo_transacao(valor)
                categoria_nome = categorizar_transacao(descricao)
                data = transacao['data']
                
                # Imprime transação
                print(f"{data:<12} {descricao:<45} R$ {valor:>8.2f} {tipo:<10} {categoria_nome:<20}")
                
                # Salva no banco
                id_categoria = salvar_categoria_db(categoria_nome)
                salvar_transacao_db(
                    id_importacao=id_importacao,
                    id_categoria=id_categoria,
                    descricao=descricao,
                    valor=valor,
                    data_transacao=transacao['data_transacao'],
                    tipo=tipo,
                    fitid=transacao['fitid']
                )
                
                # Atualiza contadores
                if valor > 0:
                    total_entradas += valor
                else:
                    total_saidas += abs(valor)
                
                # Conta transações por categoria
                if categoria_nome not in transacoes_por_categoria: # Verifica se essa categoria ainda não existe no dicionário
                    transacoes_por_categoria[categoria_nome] = {'qtd': 0, 'valor': 0}  # cria uma nova entrada no dicionário principal, começando do zero.
                
                transacoes_por_categoria[categoria_nome]['qtd'] += 1 # Incrementa a quantidade de transações dessa categoria
                transacoes_por_categoria[categoria_nome]['valor'] += abs(valor) # Soma o valor dessa transação ao total da categoria.
            
            # Imprime resumo
            print("\n" + "="*80)
            print(f"{'RESUMO POR CATEGORIA':^80}")
            print("="*80)
            
            for categoria, dados in sorted(transacoes_por_categoria.items()):
                print(f"{categoria:<30} {dados['qtd']} transações    R$ {dados['valor']:>10.2f}")
            
            print(f"{'TOTAL ENTRADAS:':<30} R$ {total_entradas:>10.2f}")
            print(f"{'TOTAL SAÍDAS:':<30} R$ {total_saidas:>10.2f}")
            print(f"{'SALDO FINAL:':<30} R$ {info_conta['saldo']:>10.2f}")
            print("="*80 + "\n")
            
            print(f'✅ Arquivo "{filename}" processado com sucesso! transações salvas no banco.')
            flash(f'✅ Arquivo "{filename}" processado com sucesso!', 'sucesso')
            
        except Exception as e:
            print(f"❌ Erro ao ler OFX: {type(e).__name__}")
            print(f"❌ Detalhes: {e}")
            import traceback
            traceback.print_exc()
            flash(f'❌ Erro ao processar o arquivo.', 'erro')
    else:
        print(f"⚠️  Arquivo {filename} não é um OFX. Apenas salvo.")
    
    return redirect('/')