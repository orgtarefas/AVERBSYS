from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from views.login_window import LoginWindow
from views.home_window import HomeWindow
from views.register_window import RegisterWindow
from models.database import DatabaseManager
from workers.api_worker import APIWorker

class AuthController(QObject):
    login_success = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    register_success = pyqtSignal()
    register_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.propostas_window = None
        self.manutencao_window = None
        self.db_manager = DatabaseManager()
        self.api_worker = APIWorker()
        
        # ⭐⭐ CORREÇÃO: Inicializar views como None
        self.login_window = None
        self.home_window = None
        self.register_window = None
        
        # Conectar sinais do worker
        self.api_worker.data_loaded.connect(self.on_data_loaded)
        self.api_worker.error_occurred.connect(self.on_api_error)
        self.api_worker.login_verified.connect(self.on_login_verified)
        self.api_worker.user_registered.connect(self.on_user_registered)
        
        # Conectar próprios sinais
        self.login_success.connect(self.on_login_success)
        self.login_failed.connect(self.on_login_failed)
        self.register_success.connect(self.on_register_success)
        self.register_failed.connect(self.on_register_failed)
        
        # Carregar dados iniciais
        self.api_worker.load_data()
    
    def show_login(self):
        """Mostra a tela de login e esconde outras"""
        print("🔐 Mostrando tela de login...")
        self._hide_all_windows()
        
        # ⭐⭐ CORREÇÃO: Criar login_window apenas quando necessário
        if self.login_window is None:
            self.login_window = LoginWindow()
            self.login_window.login_attempt.connect(self.handle_login)
        
        # Garantir que os dados são recarregados
        self.login_window.load_saved_credentials()
        
        self.login_window.show()
        self.login_window.set_loading(False)
        print("✅ Tela de login mostrada")
    
    def show_register_from_propostas(self):
        """Mostra a tela de registro a partir da tela de propostas"""
        print("📝 Mostrando tela de registro a partir de propostas...")
        if self.propostas_window:
            self.propostas_window.hide()
        
        # ⭐⭐ CORREÇÃO: Criar register_window apenas quando necessário
        if self.register_window is None:
            self.register_window = RegisterWindow()
            self.register_window.register_attempt.connect(self.handle_register)
            self.register_window.back_to_propostas.connect(self.voltar_para_propostas_from_register)
        
        self.register_window.show()
        self.register_window.set_loading(False)
        self.register_window.clear_form()
    
    def voltar_para_propostas_from_register(self):
        """Volta para propostas a partir do cadastro"""
        print("↩️ Voltando para propostas a partir do cadastro...")
        if self.register_window:
            self.register_window.hide()
        if self.propostas_window:
            self.propostas_window.show()
    
    def handle_login(self, username, password):
        """Processa tentativa de login"""
        print(f"🔐 Processando login para: {username}")
        
        # ⭐⭐ CORREÇÃO: Validação básica antes de enviar para API
        if not username or not password:
            self.login_window.show_error("Por favor, preencha usuário e senha")
            self.login_window.set_loading(False)
            return
        
        if len(username.strip()) < 3:
            self.login_window.show_error("Usuário deve ter pelo menos 3 caracteres")
            self.login_window.set_loading(False)
            return
        
        self.api_worker.verify_login(username.strip(), password)
    
    def handle_register(self, user_data):
        """Processa tentativa de registro"""
        print(f"📝 Processando registro para: {user_data.get('nome_completo', 'Novo usuário')}")
        
        # ⭐⭐ CORREÇÃO: Validação básica dos dados
        required_fields = ['nome_completo', 'login', 'password', 'perfil']
        for field in required_fields:
            if not user_data.get(field):
                self.register_window.show_error(f"Campo {field} é obrigatório")
                self.register_window.set_loading(False)
                return
        
        self.api_worker.register_user(user_data)
    
    def on_data_loaded(self, data):
        """Callback quando dados são carregados"""
        self.db_manager.set_data(data)
        print("✅ Dados carregados com sucesso!")
    
    def on_api_error(self, error_message):
        """Callback de erro da API"""
        print(f"❌ API Error: {error_message}")
        # Mostrar erro na janela apropriada
        if self.login_window and self.login_window.isVisible():
            self.login_window.show_error(f"Erro de conexão: {error_message}")
            self.login_window.set_loading(False)
        elif self.register_window and self.register_window.isVisible():
            self.register_window.show_error(f"Erro de conexão: {error_message}")
            self.register_window.set_loading(False)
    
    def on_login_verified(self, user_data, error_message):
        """Callback de verificação de login"""
        print(f"🔍 Login verificado - Sucesso: {user_data is not None}, Erro: {error_message}")
        
        if user_data and not error_message:
            # ⭐⭐ CORREÇÃO: Verificar se usuário está ativo
            if not user_data.get('ativo', True):
                self.login_failed.emit("Usuário inativo. Contate o administrador.")
            else:
                self.login_success.emit(user_data)
        elif error_message:
            self.login_failed.emit(error_message)
        else:
            self.login_failed.emit("Credenciais inválidas")
    
    def on_user_registered(self, success, message):
        """Callback de registro de usuário"""
        print(f"📝 Registro concluído - Sucesso: {success}, Mensagem: {message}")
        if success:
            self.register_success.emit()
        else:
            self.register_failed.emit(message)
    
    def on_login_success(self, user_data):
        """Callback quando o login é bem-sucedido"""
        print(f"✅ Usuário {user_data['nome_completo']} logado com sucesso!")
        
        # Fecha a janela de login
        if self.login_window:
            self.login_window.hide()
        
        # ⭐⭐ CORREÇÃO: Importação tardia para evitar circular
        from views.propostas_window import PropostasWindow
        
        # Criar a janela de propostas APENAS se não existir ou se o usuário mudou
        if self.propostas_window is None:
            print("🆕 Criando nova janela de propostas...")
            self.propostas_window = PropostasWindow(user_data)
            
            # Conectar sinais da janela de propostas
            self.propostas_window.logout_request.connect(self.on_logout_requested)
            self.propostas_window.abrir_manutencao_usuarios.connect(self.abrir_manutencao_usuarios)
            self.propostas_window.abrir_cadastro_usuario.connect(self.show_register_from_propostas)
        else:
            print("🔄 Atualizando janela de propostas existente...")
            # Atualizar dados do usuário
            self.propostas_window.user_data = user_data
        
        # Mostrar a janela de propostas
        self.propostas_window.show()
        self.propostas_window.raise_()  # Traz para frente
        self.propostas_window.activateWindow()  # Foca a janela
        print("🎯 Janela de propostas mostrada com sucesso")
    
    def on_logout_requested(self):
        """Callback quando usuário solicita logout das propostas"""
        print("🚪 Logout solicitado da janela de propostas")
        self.logout()
    
    def abrir_manutencao_usuarios(self):
        """Abre tela de manutenção de usuários"""
        print("👥 Abrindo manutenção de usuários...")
        
        # Verificação de segurança
        perfil = self.propostas_window.user_data['perfil']
        if perfil not in ['Dev', 'Gerente', 'Supervisor']:
            QMessageBox.warning(self.propostas_window, "Acesso Negado", 
                            "Apenas usuários com perfil 'Dev', 'Gerente' ou 'Supervisor' podem acessar esta funcionalidade.")
            return
        
        # ⭐⭐ CORREÇÃO: Importação tardia
        from views.manutencao_usuarios_window import ManutencaoUsuariosWindow
        
        # Criar janela de manutenção se não existir
        if self.manutencao_window is None:
            self.manutencao_window = ManutencaoUsuariosWindow(self.propostas_window.user_data)
            self.manutencao_window.fechar_request.connect(self.voltar_para_propostas)
        
        # Esconder propostas e mostrar manutenção
        if self.propostas_window:
            self.propostas_window.hide()
        
        self.manutencao_window.show()
        self.manutencao_window.raise_()
        self.manutencao_window.activateWindow()
        print("✅ Tela de manutenção de usuários aberta")
    
    def voltar_para_propostas(self):
        """Volta para tela de propostas"""
        print("↩️ Voltando para tela de propostas...")
        if self.manutencao_window:
            self.manutencao_window.hide()
        
        if self.propostas_window:
            self.propostas_window.show()
            self.propostas_window.raise_()
            self.propostas_window.activateWindow()
    
    def on_login_failed(self, error_message):
        """Callback de login falhou"""
        print(f"❌ Login falhou: {error_message}")
        if self.login_window:
            self.login_window.show_error(error_message)
            self.login_window.set_loading(False)
    
    def on_register_success(self):
        """Callback de registro bem-sucedido"""
        print("✅ Registro bem-sucedido")
        if self.register_window:
            self.register_window.show_success("Usuário cadastrado com sucesso!")
            self.register_window.set_loading(False)
            
            # Voltar para a tela de propostas após cadastro bem-sucedido
            QTimer.singleShot(1500, self.voltar_para_propostas_from_register)
    
    def on_register_failed(self, error_message):
        """Callback de registro falhou"""
        print(f"❌ Registro falhou: {error_message}")
        if self.register_window:
            self.register_window.show_error(error_message)
            self.register_window.set_loading(False)
    
    def logout(self):
        """Realiza logout do sistema"""
        print("🚪 Realizando logout...")
        
        # Fechar e destruir a janela de propostas
        if self.propostas_window:
            print("🔒 Fechando janela de propostas...")
            self.propostas_window.close()
            self.propostas_window.deleteLater()  # ⭐⭐ CORREÇÃO: Garantir destruição
            self.propostas_window = None
        
        # Fechar janela de manutenção
        if self.manutencao_window:
            print("🔒 Fechando janela de manutenção...")
            self.manutencao_window.close()
            self.manutencao_window.deleteLater()
            self.manutencao_window = None
        
        # Fechar outras janelas
        if self.register_window:
            self.register_window.hide()
        
        # ⭐⭐ CORREÇÃO: Limpar dados sensíveis
        self.db_manager.clear_sensitive_data()
        
        # Mostrar tela de login
        self.show_login()
        
        print("✅ Logout concluído com sucesso")
    
    def _hide_all_windows(self):
        """Esconde todas as janelas"""
        if self.login_window:
            self.login_window.hide()
        
        if self.home_window:
            self.home_window.hide()
        
        if self.register_window:
            self.register_window.hide()
        
        if self.propostas_window:
            self.propostas_window.hide()
        
        if self.manutencao_window:
            self.manutencao_window.hide()