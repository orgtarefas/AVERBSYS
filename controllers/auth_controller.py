from PyQt5.QtWidgets import (QMessageBox)
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from views.login_window import LoginWindow
from views.home_window import HomeWindow
from views.register_window import RegisterWindow
from views.propostas_window import PropostasWindow
from views.manutencao_usuarios_window import ManutencaoUsuariosWindow

class AuthController(QObject):
    login_success = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    register_success = pyqtSignal()
    register_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # Inicializar views
        self.login_window = LoginWindow()
        self.home_window = HomeWindow()
        self.register_window = RegisterWindow()
        self.propostas_window = None
        self.manutencao_window = None
        
        # ⭐⭐ CONECTAR SINAIS DAS VIEWS
        self.login_window.login_attempt.connect(self.handle_login)
        self.home_window.logout_request.connect(self.show_login)
        self.register_window.register_attempt.connect(self.handle_register)
        self.register_window.back_to_propostas.connect(self.voltar_para_propostas_from_register)
        
        # ⭐⭐ CONECTAR PRÓPRIOS SINAIS
        self.login_success.connect(self.on_login_success)
        self.login_failed.connect(self.on_login_failed)
        self.register_success.connect(self.on_register_success)
        self.register_failed.connect(self.on_register_failed)
        
        print("✅ AuthController inicializado (sinais conectados)")
    
    def handle_login(self, username, password):
        """Processa tentativa de login"""
        print(f"🔐 AuthController: Tentativa de login para: {username}")
        self.login_window.set_loading(True)
        
        # ⭐⭐ CRIAR NOVA INSTÂNCIA DO UserService (não reutilizar)
        from services.user_service import UserService
        user_service = UserService()
        
        print(f"🔗 Conectando sinais do UserService...")
        
        # ⭐⭐ CONECTAR SINAL ANTES DE CHAMAR O MÉTODO
        user_service.user_authenticated.connect(self.on_login_verified)
        print("✅ Sinal user_authenticated conectado ao AuthController")
        
        # ⭐⭐ CHAMAR VERIFICAÇÃO DE LOGIN
        print("🚀 Chamando verificar_login no UserService...")
        user_service.verificar_login(username, password)
        
    def on_login_verified(self, user_data, error_message):
        """Callback de verificação de login"""
        print(f"📨 AuthController: Sinal recebido - user_data: {bool(user_data)}, error: {error_message}")
        
        # ⭐⭐ DESCONECTAR O SINAL PARA EVITAR MÚLTIPLAS CHAMADAS
        try:
            self.sender().user_authenticated.disconnect(self.on_login_verified)
            print("🔌 Sinal desconectado após uso")
        except:
            pass
        
        self.login_window.set_loading(False)
        
        if user_data and not error_message:
            print(f"✅ AuthController: Login válido - {user_data['nome_completo']}")
            print(f"🎯 Emitindo sinal login_success...")
            self.login_success.emit(user_data)
        elif error_message:
            print(f"❌ AuthController: Erro no login - {error_message}")
            self.login_failed.emit(error_message)
        else:
            print("❌ AuthController: Erro desconhecido no login")
            self.login_failed.emit("Erro desconhecido no login")
    
    def on_login_success(self, user_data):
        """Callback de login bem-sucedido - REDIRECIONA PARA PROPOSTAS"""
        print(f"✅ Usuário {user_data['nome_completo']} logado com sucesso!")
        
        try:
            # ⭐⭐ IMPORTAÇÃO TARDIA para evitar circular
            from views.propostas_window import PropostasWindow
            
            # Criar tela de propostas com dados do usuário
            self.propostas_window = PropostasWindow(user_data)
            
            # Conectar sinais da tela de propostas
            self.propostas_window.logout_request.connect(self.logout)
            self.propostas_window.abrir_manutencao_usuarios.connect(self.abrir_manutencao_usuarios)
            self.propostas_window.abrir_cadastro_usuario.connect(self.show_register_from_propostas)
            
            # Esconder outras telas e mostrar propostas
            self._hide_all_windows()
            self.propostas_window.show()
            
            print("🎯 Tela de propostas aberta com sucesso!")
            
        except Exception as e:
            print(f"❌ ERRO ao abrir tela de propostas: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Erro", f"Erro ao abrir sistema: {str(e)}")
    
    def on_login_failed(self, error_message):
        """Callback de login falhou"""
        print(f"❌ Login falhou: {error_message}")
        self.login_window.show_error(error_message)
        self.login_window.set_loading(False)
    
    def show_login(self):
        """Mostra a tela de login e esconde outras"""
        print("🔐 Mostrando tela de login...")
        self._hide_all_windows()
        
        # Garantir que os dados são recarregados
        self.login_window.load_saved_credentials()
        
        self.login_window.show()
        self.login_window.set_loading(False)
        print("✅ Tela de login mostrada")
    
    def show_register_from_propostas(self):
        """Mostra a tela de registro a partir da tela de propostas"""
        if self.propostas_window:
            self.propostas_window.hide()
        
        self.register_window.show()
        self.register_window.set_loading(False)
        self.register_window.clear_form()
    
    def voltar_para_propostas_from_register(self):
        """Volta para propostas a partir do cadastro"""
        self.register_window.hide()
        if self.propostas_window:
            self.propostas_window.show()
    
    def handle_register(self, user_data):
        """Processa tentativa de registro"""
        print(f"👤 Tentativa de registro: {user_data['login']}")
        self.register_window.set_loading(True)
        # ⭐⭐ NOTA: Você precisará ajustar o UserService para registro também
        # self.user_service.cadastrar_usuario(user_data)
    
    def abrir_manutencao_usuarios(self):
        """Abre tela de manutenção de usuários"""
        print("👥 Abrindo manutenção de usuários...")
        
        # Verificação de segurança
        perfil = self.propostas_window.user_data['perfil']
        if perfil not in ['Dev', 'Gerente', 'Supervisor']:
            QMessageBox.warning(self.propostas_window, "Acesso Negado", 
                            "Apenas usuários com perfil 'Dev', 'Gerente' ou 'Supervisor' podem acessar esta funcionalidade.")
            return
        
        try:
            # ⭐⭐ IMPORTAÇÃO TARDIA para evitar circular
            from views.manutencao_usuarios_window import ManutencaoUsuariosWindow
            
            self.manutencao_window = ManutencaoUsuariosWindow(self.propostas_window.user_data)
            self.manutencao_window.fechar_request.connect(self.voltar_para_propostas)
            
            if self.propostas_window:
                self.propostas_window.hide()
            
            self.manutencao_window.show()
            print("✅ Tela de manutenção aberta")
            
        except Exception as e:
            print(f"❌ ERRO ao abrir manutenção: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.propostas_window, "Erro", f"Erro ao abrir manutenção: {str(e)}")
    
    def voltar_para_propostas(self):
        """Volta para tela de propostas"""
        if self.manutencao_window:
            self.manutencao_window.close()
            self.manutencao_window = None
        
        if self.propostas_window:
            self.propostas_window.show()
    
    def on_register_success(self):
        """Callback de registro bem-sucedido"""
        self.register_window.show_success("Usuário cadastrado com sucesso!")
        self.register_window.set_loading(False)
        
        # Voltar para a tela de propostas após cadastro bem-sucedido
        QTimer.singleShot(1500, self.voltar_para_propostas_from_register)
    
    def on_register_failed(self, error_message):
        """Callback de registro falhou"""
        self.register_window.show_error(error_message)
        self.register_window.set_loading(False)
    
    def logout(self):
        """Realiza logout do sistema"""
        print("🚪 Realizando logout...")
        
        # Fechar todas as janelas
        self._hide_all_windows()
        
        # Resetar dados
        self.propostas_window = None
        self.manutencao_window = None
        
        # Mostrar tela de login
        self.show_login()
        
        # Recarregar as credenciais salvas
        self.login_window.load_saved_credentials()
        
        print("✅ Logout realizado com sucesso")
    
    def _hide_all_windows(self):
        """Esconde todas as janelas"""
        self.login_window.hide()
        self.home_window.hide()
        self.register_window.hide()
        
        if self.propostas_window:
            self.propostas_window.hide()
        
        if self.manutencao_window:
            self.manutencao_window.hide()