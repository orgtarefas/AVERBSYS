import firebase_admin
from firebase_admin import credentials, firestore
import os

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
                # Verificar se o arquivo de credenciais existe
                cred_path = "serviceAccountKey.json"
                
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Arquivo {cred_path} não encontrado na raiz do projeto!")
                
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