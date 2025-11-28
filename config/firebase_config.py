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
                
                # ⭐⭐ CONFIGURAÇÃO PARA 2 BANCOS
                # Banco PRINCIPAL (contratos) - serviceAccountKey.json
                cred_paths_principal = [
                    resource_path('serviceAccountKey.json'),
                    'serviceAccountKey.json',
                    os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
                ]
                
                # Banco de LOGIN - serviceAccountKey2.json  
                cred_paths_login = [
                    resource_path('serviceAccountKey2.json'),
                    'serviceAccountKey2.json',
                    os.path.join(os.path.dirname(__file__), 'serviceAccountKey2.json')
                ]
                
                # Encontrar credenciais do banco principal
                cred_path_principal = None
                for path in cred_paths_principal:
                    if os.path.exists(path):
                        cred_path_principal = path
                        print(f"✅ Arquivo PRINCIPAL encontrado em: {path}")
                        break
                
                # Encontrar credenciais do banco de login
                cred_path_login = None
                for path in cred_paths_login:
                    if os.path.exists(path):
                        cred_path_login = path
                        print(f"✅ Arquivo LOGIN encontrado em: {path}")
                        break
                
                if not cred_path_principal:
                    raise FileNotFoundError("Arquivo serviceAccountKey.json não encontrado!")
                if not cred_path_login:
                    raise FileNotFoundError("Arquivo serviceAccountKey2.json não encontrado!")
                
                # ⭐⭐ INICIALIZAR 2 APPS DO FIREBASE
                # App PRINCIPAL (contratos)
                if not firebase_admin._apps:
                    cred_principal = credentials.Certificate(cred_path_principal)
                    firebase_admin.initialize_app(cred_principal, name='principal')
                    print("✅ Firebase PRINCIPAL inicializado!")
                
                # App LOGIN
                cred_login = credentials.Certificate(cred_path_login)
                self.app_login = firebase_admin.initialize_app(cred_login, name='login')
                print("✅ Firebase LOGIN inicializado!")
                
                # Criar clientes para cada banco
                self.db_principal = firestore.client(app=firebase_admin.get_app('principal'))
                self.db_login = firestore.client(app=self.app_login)
                
                self._initialized = True
                print("✅ Ambos os bancos configurados com sucesso!")
                
            except Exception as e:
                print(f"❌ Erro ao conectar Firebase: {e}")
                raise

    def get_db_principal(self):
        """Retorna cliente do banco PRINCIPAL (contratos)"""
        return self.db_principal

    def get_db_login(self):
        """Retorna cliente do banco de LOGIN"""
        return self.db_login