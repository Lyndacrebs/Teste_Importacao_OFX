import os

# Configurações do Flask
class Config:
    SECRET_KEY = 'chave_secreta_123'
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'ofx'}
    
    # Configurações do Banco de Dados
    DB_NAME = 'meu_banco.db'
    
    @staticmethod
    def init_app(app):
        """Inicializa configurações do app"""
        # Cria pasta de uploads se não existir
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)