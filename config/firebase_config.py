import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

class FirebaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            try:
                # Função para obter o caminho correto no executável
                def resource_path(relative_path):
                    try:
                        base_path = sys._MEIPASS
                    except Exception:
                        base_path = os.path.abspath(".")
                    return os.path.join(base_path, relative_path)
                
                # Tentar diferentes caminhos para o arquivo de credenciais
                cred_paths = [
                    resource_path('serviceAccountKey.json'),  # No executável
                    'serviceAccountKey.json',  # No desenvolvimento
                    os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
                ]
                
                cred_path = None
                for path in cred_paths:
                    if os.path.exists(path):
                        cred_path = path
                        print(f"✅ Arquivo de credenciais encontrado em: {path}")
                        break
                
                if not cred_path:
                    raise FileNotFoundError("Arquivo serviceAccountKey.json não encontrado em nenhum dos caminhos!")
                
                # Inicializar Firebase apenas se não estiver inicializado
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase inicializado com sucesso!")
                
                self.db = firestore.client()
                self._initialized = True
                
            except Exception as e:
                print(f"❌ Erro ao conectar Firebase: {e}")
                raise

    def get_db(self):
        return self.db