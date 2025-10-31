from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QComboBox,
                             QMessageBox, QProgressBar)
from PyQt5.QtCore import pyqtSignal, Qt
from utils.styles import get_register_styles

class RegisterWindow(QWidget):
    register_attempt = pyqtSignal(dict)
    back_to_login = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sistema - Cadastro")
        self.setStyleSheet(get_register_styles())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Cadastro de Novo Usuário")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")
        
        # Frame do formulário
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Campos de entrada
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome Completo")
        self.nome_input.setObjectName("inputField")
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Login")
        self.login_input.setObjectName("inputField")
        
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Senha")
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setObjectName("inputField")
        
        self.confirm_senha_input = QLineEdit()
        self.confirm_senha_input.setPlaceholderText("Confirmar Senha")
        self.confirm_senha_input.setEchoMode(QLineEdit.Password)
        self.confirm_senha_input.setObjectName("inputField")
        
        # Combo box para perfil
        self.perfil_combo = QComboBox()
        self.perfil_combo.addItems(["Analista", "Gerente", "Dev", "Supervisor"])
        self.perfil_combo.setObjectName("comboBox")
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.register_button = QPushButton("Cadastrar")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.attempt_register)
        
        self.back_button = QPushButton("Voltar ao Login")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.back_to_login.emit)
        
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.register_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        
        # Adicionar ao layout do formulário
        form_layout.addWidget(QLabel("Nome Completo:"))
        form_layout.addWidget(self.nome_input)
        form_layout.addWidget(QLabel("Login:"))
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(QLabel("Senha:"))
        form_layout.addWidget(self.senha_input)
        form_layout.addWidget(QLabel("Confirmar Senha:"))
        form_layout.addWidget(self.confirm_senha_input)
        form_layout.addWidget(QLabel("Perfil:"))
        form_layout.addWidget(self.perfil_combo)
        form_layout.addLayout(buttons_layout)
        form_layout.addWidget(self.progress_bar)
        
        form_frame.setLayout(form_layout)
        
        # Adicionar ao layout principal
        layout.addWidget(title)
        layout.addWidget(form_frame)
        
        self.setLayout(layout)
        self.resize(500, 600)
    
    def attempt_register(self):
        nome = self.nome_input.text().strip()
        login = self.login_input.text().strip()
        senha = self.senha_input.text()
        confirm_senha = self.confirm_senha_input.text()
        perfil = self.perfil_combo.currentText()
        
        # Validações
        if not all([nome, login, senha, confirm_senha]):
            self.show_error("Por favor, preencha todos os campos")
            return
        
        if senha != confirm_senha:
            self.show_error("As senhas não coincidem")
            return
        
        if len(senha) < 4:
            self.show_error("A senha deve ter pelo menos 4 caracteres")
            return
        
        user_data = {
            'nome_completo': nome,
            'login': login,
            'senha': senha,
            'perfil': perfil
        }
        
        self.set_loading(True)
        self.register_attempt.emit(user_data)
    
    def set_loading(self, loading):
        self.register_button.setEnabled(not loading)
        self.back_button.setEnabled(not loading)
        self.progress_bar.setVisible(loading)
    
    def show_error(self, message):
        self.set_loading(False)
        QMessageBox.warning(self, "Erro no Cadastro", message)
    
    def show_success(self, message):
        self.set_loading(False)
        QMessageBox.information(self, "Sucesso", message)
        self.clear_form()
    
    def clear_form(self):
        self.nome_input.clear()
        self.login_input.clear()
        self.senha_input.clear()
        self.confirm_senha_input.clear()
        self.perfil_combo.setCurrentIndex(0)