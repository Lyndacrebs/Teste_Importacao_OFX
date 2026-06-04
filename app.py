from flask import Flask
from config import Config
from services.database import criar_tabelas, inicializar_categorias
from services.categorizador import CATEGORIAS
from routes.importacao import importacao_bp
import os


def create_app():
    """
    Factory function para criar e configurar o app Flask.
    """
    app = Flask(__name__, static_folder='static')
    
    # Carrega configurações
    app.secret_key = Config.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    
    # Inicializa pasta de uploads
    Config.init_app(app)
    
    # Cria tabelas do banco de dados
    criar_tabelas()
    
    # Inicializa categorias no banco
    inicializar_categorias(CATEGORIAS)
    
    # Registra blueprints (rotas)
    app.register_blueprint(importacao_bp)
    
    return app


# Cria a aplicação
app = create_app()


# ==========================================
# INÍCIO DO SERVIDOR
# ==========================================
if __name__ == "__main__":
    app.run(debug=True, port=5001)
    # debug=True: mostra erros detalhados e recarrega ao salvar
    # port=5001: usa a porta 5001 (para não conflitar com outras coisas)