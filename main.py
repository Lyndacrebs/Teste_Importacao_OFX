from flask import Flask, render_template, request, redirect
# Flask: cria o servidor web
# render_template: envia arquivos HTML para o navegador
# request: pega os dados enviados pelo usuário (como o arquivo)
# redirect: redireciona o usuário para outra página

from werkzeug.utils import secure_filename
# secure_filename: limpa o nome do arquivo para evitar ataques
import os
# os: permite trabalhar com pastas e arquivos do sistema

from ofxparse import OfxParser  
#biblioteca para ler OFX

# ============================================
# CONFIGURAÇÃO DO FLASK
# ============================================

app = Flask(__name__, static_folder='static')# Cria a aplicação Flask
# static_folder='static': diz que CSS, JS e imagens estão na pasta 'static/'

UPLOAD_FOLDER = 'uploads' # Define o nome da pasta onde os uploads serão salvos

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Salva essa configuração no app para usar depois

if not os.path.exists(UPLOAD_FOLDER): # Cria a pasta 'uploads' automaticamente se ela não existir
    os.makedirs(UPLOAD_FOLDER)
# Isso evita erro na primeira vez que rodar o código


# ============================================
# ROTAS - URLs que o Flask vai responder
# ============================================

@app.route("/") # Rota da página inicial: quando acessar http://127.0.0.1:5001/
def index():
    return render_template('index.html')  # render_template procura o arquivo em: templates/index.html



@app.route('/upload', methods=['POST']) # Rota do upload: quando o formulário enviar para /upload via POST
def upload():

        # 1️⃣ Verifica se veio um arquivo na requisição
    if 'file' not in request.files: # request.files é um dicionário com todos os arquivos enviados
        return redirect('/')# Se não tiver arquivo, volta pra página inicial
    
    # 2️⃣ Pega o arquivo enviado (o nome 'file' deve bater com o name="" do input no html)
    file = request.files['file']
    
    # 3️⃣ Verifica se o usuário selecionou um arquivo (não deixou vazio)
    if file.filename == '':
        return redirect('/')
    
    # 4️⃣ Limpa o nome do arquivo para segurança
    # Remove caracteres perigosos como / \ .. etc.
    filename = secure_filename(file.filename)


    

    # 5️⃣ Cria o caminho completo: "uploads/meu_arquivo.pdf" e salva o arquivo no disco
    filepath = os.path.join(UPLOAD_FOLDER, filename)  # ← Cria a variável
    file.save(filepath)




# ==========================================
# LEITURA OFX
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

            
            account = ofx.account    # Acessa a conta (geralmente só tem uma no arquivo)

            statement = account.statement # Acessa o extrato


            # Percorre todas as transações do extrato
            for transaction in statement.transactions:
                # Pega a descrição (memo é mais detalhado, payee é o nome)
                descricao = transaction.memo or transaction.payee or "Sem descrição"
                
                # Formata o valor com 2 casas decimais
                valor = float(transaction.amount)
                
                # Imprime no formato que você pediu: "DESCRIÇÃO VALOR"
                print(f"{descricao.upper():<40} R$ {valor:>10.2f}")

        except Exception as e:
            print(f"❌ Erro ao ler OFX: {type(e).__name__}")
            print(f"❌ Detalhes: {e}")
            import traceback
            traceback.print_exc()
    
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
    app.run(debug=True, port=5001) #mostra erros detalhados e recarrega ao salvar o arquivo

    #usa a porta 5001 (para não conflitar com outras coisas)
