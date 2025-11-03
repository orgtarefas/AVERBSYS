import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_service import UserService
from PyQt5.QtCore import QCoreApplication

def test_cadastro():
    def on_registered(success, message):
        print(f"📢 Resultado: {success} - {message}")
        if success:
            print("🎉 USUÁRIO CRIADO NO FIREBASE COM SUCESSO!")
        app.quit()
    
    app = QCoreApplication(sys.argv)
    
    try:
        user_service = UserService()
        user_service.user_registered.connect(on_registered)
        
        # Dados de teste
        user_data = {
            'login': 'evandro.messias',
            'senha': 'Aej451590@@',
            'perfil': 'Supervisor',
            'nome_completo': 'Evandro Messias'
        }
        
        print("🚀 Iniciando cadastro no Firebase...")
        user_service.cadastrar_usuario(user_data)
        
        app.exec_()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        app.quit()

if __name__ == "__main__":
    test_cadastro()