from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from utils.styles import get_home_styles

class HomeWindow(QWidget):
    logout_request = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sistema - Home")
        self.setStyleSheet(get_home_styles())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout()
        
        self.welcome_label = QLabel("Bem-vindo ao Sistema")
        self.welcome_label.setObjectName("welcomeLabel")
        
        self.logout_button = QPushButton("Sair")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.clicked.connect(self.logout_request.emit)
        
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_button)
        header.setLayout(header_layout)
        
        # User info
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QGridLayout()
        info_layout.setSpacing(10)
        
        self.name_label = QLabel("Nome: -")
        self.login_label = QLabel("Login: -")
        self.perfil_label = QLabel("Perfil: -")
        self.status_label = QLabel("Status: -")
        
        info_layout.addWidget(QLabel("Nome Completo:"), 0, 0)
        info_layout.addWidget(self.name_label, 0, 1)
        info_layout.addWidget(QLabel("Login:"), 1, 0)
        info_layout.addWidget(self.login_label, 1, 1)
        info_layout.addWidget(QLabel("Perfil:"), 2, 0)
        info_layout.addWidget(self.perfil_label, 2, 1)
        info_layout.addWidget(QLabel("Status:"), 3, 0)
        info_layout.addWidget(self.status_label, 3, 1)
        
        info_frame.setLayout(info_layout)
        
        # Content area
        content_label = QLabel("Área Principal do Sistema")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setObjectName("contentLabel")
        
        layout.addWidget(header)
        layout.addWidget(info_frame)
        layout.addWidget(content_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.resize(800, 600)
    
    def set_user_data(self, user_data):
        self.user_data = user_data
        self.update_display()
    
    def update_display(self):
        if self.user_data:
            self.welcome_label.setText(f"Bem-vindo, {self.user_data['nome_completo']}!")
            self.name_label.setText(self.user_data['nome_completo'])
            self.login_label.setText(self.user_data['login'])
            self.perfil_label.setText(self.user_data['perfil'])
            self.status_label.setText(self.user_data['status'])