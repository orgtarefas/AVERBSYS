from PyQt5.QtCore import QObject, pyqtSignal
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
        self.db_manager = DatabaseManager()
        self.api_worker = APIWorker()
        
        # Conectar sinais do worker
        self.api_worker.data_loaded.connect(self.on_data_loaded)
        self.api_worker.error_occurred.connect(self.on_api_error)
        self.api_worker.login_verified.connect(self.on_login_verified)
        self.api_worker.user_registered.connect(self.on_user_registered)
        
        # Inicializar views
        self.login_window = LoginWindow()
        self.home_window = HomeWindow()
        self.register_window = RegisterWindow()
        
        # Conectar sinais das views
        self.login_window.login_attempt.connect(self.handle_login)
        self.login_window.register_request.connect(self.show_register)
        self.home_window.logout_request.connect(self.show_login)
        self.register_window.register_attempt.connect(self.handle_register)
        self.register_window.back_to_login.connect(self.show_login)
        
        # Conectar próprios sinais
        self.login_success.connect(self.on_login_success)
        self.login_failed.connect(self.on_login_failed)
        self.register_success.connect(self.on_register_success)
        self.register_failed.connect(self.on_register_failed)
        
        # Carregar dados iniciais
        self.api_worker.load_data()
    
    def show_login(self):
        self.home_window.hide()
        self.register_window.hide()
        self.login_window.show()
        self.login_window.set_loading(False)
    
    def show_register(self):
        self.login_window.hide()
        self.register_window.show()
        self.register_window.set_loading(False)
    
    def handle_login(self, username, password):
        self.api_worker.verify_login(username, password)
    
    def handle_register(self, user_data):
        self.api_worker.register_user(user_data)
    
    def on_data_loaded(self, data):
        self.db_manager.set_data(data)
        print("Dados carregados com sucesso!")
    
    def on_api_error(self, error_message):
        print(f"API Error: {error_message}")
        # Mostrar erro na janela apropriada
        if self.login_window.isVisible():
            self.login_window.show_error(f"Erro: {error_message}")
        elif self.register_window.isVisible():
            self.register_window.show_error(f"Erro: {error_message}")
    
    def on_login_verified(self, user_data, error_message):
        if user_data and not error_message:  # Sucesso: user_data preenchido e error_message vazio
            self.login_success.emit(user_data)
        elif error_message:  # Erro: error_message preenchido
            self.login_failed.emit(error_message)
        else:  # Caso inesperado
            self.login_failed.emit("Erro desconhecido no login")
    
    def on_user_registered(self, success, message):
        if success:
            self.register_success.emit()
        else:
            self.register_failed.emit(message)
    
    def on_login_success(self, user_data):
        self.home_window.set_user_data(user_data)
        self.login_window.hide()
        self.login_window.set_loading(False)
        self.home_window.show()
    
    def on_login_failed(self, error_message):
        self.login_window.show_error(error_message)
        self.login_window.set_loading(False)
    
    def on_register_success(self):
        self.register_window.show_success("Usuário cadastrado com sucesso!")
        self.register_window.set_loading(False)
    
    def on_register_failed(self, error_message):
        self.register_window.show_error(error_message)
        self.register_window.set_loading(False)