import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_conexao():
    try:
        print("🔗 Testando conexão com Firebase...")
        
        # Importar depois de ajustar o path
        from config.firebase_config import FirebaseManager
        
        firebase = FirebaseManager()
        db = firebase.get_db()
        
        # Testar se consegue acessar a collection
        usuarios_ref = db.collection('usuarios')
        print("✅ Conexão com Firebase estabelecida!")
        print("✅ Collection 'usuarios' acessível!")
        
        # Contar usuários existentes
        usuarios = list(usuarios_ref.limit(10).get())
        print(f"📊 Usuários existentes: {len(usuarios)}")
        
        # Mostrar usuários se existirem
        for usuario in usuarios:
            user_data = usuario.to_dict()
            print(f"👤 {user_data.get('login', 'N/A')} - {user_data.get('nome_completo', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    test_conexao()