import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from services.user_service import UserService

class WorkerThread(QThread):
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)
    
    def __init__(self, worker_function, *args, **kwargs):
        super().__init__()
        self.worker_function = worker_function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.worker_function(*self.args, **self.kwargs)
            self.finished_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))

class APIWorker(QObject):
    data_loaded = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    login_verified = pyqtSignal(dict, str)
    user_registered = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
        self.threads = []
        
        # Conectar sinais do user_service
        self.user_service.user_authenticated.connect(self._on_login_result)
        self.user_service.user_registered.connect(self._on_register_result)
    
    def load_data(self):
        # Para compatibilidade, emite sinal vazio
        self.data_loaded.emit(None)
    
    def verify_login(self, username, password):
        def worker():
            self.user_service.verificar_login(username, password)
        
        thread = WorkerThread(worker)
        thread.start()
        self.threads.append(thread)
    
    def _on_login_result(self, user_data, error_message):
        if user_data and not error_message:
            self.login_verified.emit(user_data, "")
        else:
            self.login_verified.emit({}, error_message)
    
    def register_user(self, user_data):
        def worker():
            self.user_service.cadastrar_usuario(user_data)
        
        thread = WorkerThread(worker)
        thread.start()
        self.threads.append(thread)
    
    def _on_register_result(self, success, message):
        self.user_registered.emit(success, message)