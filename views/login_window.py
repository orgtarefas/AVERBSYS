from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QProgressBar)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from utils.styles import get_login_styles

class LoginWindow(QWidget):
    login_attempt = pyqtSignal(str, str)
    register_request = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("ABERBSYS")
        self.setStyleSheet(get_login_styles())
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("ABERBSYS")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")
        
        # Frame do formulário
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Campos de entrada
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuário")
        self.username_input.setObjectName("inputField")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("inputField")
        
        # Botões
        self.login_button = QPushButton("Entrar")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.attempt_login)
        
        self.register_button = QPushButton("Cadastrar Novo Usuário")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.register_request.emit)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Progresso indeterminado
        
        # Adicionar ao layout do formulário
        form_layout.addWidget(QLabel("Usuário:"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Senha:"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.register_button)
        form_layout.addWidget(self.progress_bar)
        
        form_frame.setLayout(form_layout)
        
        # Adicionar ao layout principal
        layout.addWidget(title)
        layout.addWidget(form_frame)
        
        self.setLayout(layout)
        self.resize(400, 500)
        self.center_window()
    
    def center_window(self):
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("Por favor, preencha todos os campos")
            return
        
        self.set_loading(True)
        self.login_attempt.emit(username, password)
    
    def set_loading(self, loading):
        self.login_button.setEnabled(not loading)
        self.register_button.setEnabled(not loading)
        self.progress_bar.setVisible(loading)
    
    def show_error(self, message):
        self.set_loading(False)
        QMessageBox.warning(self, "Erro no Login", message)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.attempt_login()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Limpeza quando a janela for fechada"""
        self.set_loading(False)
        super().closeEvent(event)