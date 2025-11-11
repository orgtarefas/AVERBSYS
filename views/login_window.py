from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QProgressBar, QDialog)  
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from utils.styles import get_login_styles
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LoginWindow(QWidget):
    login_attempt = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
       # self.setWindowTitle("AVERBSYS")
        self.setStyleSheet(get_login_styles())
        
        # DEFINIR ÍCONE DA JANELA
        try:
            self.setWindowIcon(QIcon(resource_path('assets/logo.png')))
        except:
            print("Logo não encontrada. Verifique o caminho: assets/logo.png")
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # LOGO COMPLETA (COM NOME) NO CENTRO
        try:
            logo_label = QLabel()
            pixmap = QPixmap(resource_path('assets/logo_completa.png'))
            pixmap = pixmap.scaled(300, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("margin-bottom: 20px;")
            layout.addWidget(logo_label)
        except Exception as e:
            print(f"Logo completa não encontrada: {e}")
            # Fallback: usar logo simplificada + texto
            try:
                logo_fallback_label = QLabel()
                pixmap_fallback = QPixmap('assets/logo.png')
                pixmap_fallback = pixmap_fallback.scaled(200, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_fallback_label.setPixmap(pixmap_fallback)
                logo_fallback_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_fallback_label)
                
                title_fallback = QLabel("")
                title_fallback.setAlignment(Qt.AlignCenter)
                title_fallback.setObjectName("title")
                layout.addWidget(title_fallback)
            except:
                # Último fallback: apenas texto
                title_fallback = QLabel("")
                title_fallback.setAlignment(Qt.AlignCenter)
                title_fallback.setObjectName("title")
                layout.addWidget(title_fallback)
        
        
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
        form_layout.addWidget(self.progress_bar)
        
        form_frame.setLayout(form_layout)
        
        # Adicionar ao layout principal
        layout.addWidget(form_frame)
        

    # === BOTÃO "?" NO CANTO INFERIOR DIREITO ===
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()  # Empurra para a direita
        
        try:
            sobre_button = QPushButton()
            pixmap = QPixmap(resource_path('assets/sobre.png'))
            pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            sobre_button.setIcon(QIcon(pixmap))
            sobre_button.setIconSize(pixmap.size())
            sobre_button.setFixedSize(30, 30)
            sobre_button.setObjectName("sobreButton")
            sobre_button.clicked.connect(self.mostrar_informacoes)
            sobre_button.setToolTip("Informações do sistema")
            sobre_button.setText("")
            bottom_layout.addWidget(sobre_button)
        except Exception as e:
            print(f"Imagem sobre.png não encontrada. Verifique o caminho: assets/sobre.png - {e}")
            # Fallback: botão com "?" simples
            sobre_button = QPushButton("?")
            sobre_button.setFixedSize(30, 30)
            sobre_button.setObjectName("sobreButton")
            sobre_button.clicked.connect(self.mostrar_informacoes)
            sobre_button.setToolTip("Informações do sistema")
            bottom_layout.addWidget(sobre_button)

        layout.addLayout(bottom_layout)
        # === FIM DO BOTÃO "?" ===
        
        self.setLayout(layout)
        self.resize(400, 550)
        self.center_window()


    def center_window(self):
        """Centraliza a janela na tela"""
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )        


    def mostrar_informacoes(self):
        """Mostra informações do sistema"""
        dialog = QDialog(self)
        dialog.setWindowTitle(" ")
        
        # REMOVER o botão "?" da janela
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        try:
            dialog.setWindowIcon(QIcon(resource_path('assets/logo.png')))
        except:
            pass
        
        dialog.setFixedSize(350, 280)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: Arial, sans-serif;
            }
            QLabel {
                color: #333333;
            }
            QLabel#titulo {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#subtitulo {
                font-size: 12px;
                font-weight: bold;
                color: #34495e;
                margin-top: 10px;
            }
            QLabel#info {
                font-size: 11px;
                color: #555555;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(20, 20, 20, 15)
        
        # Título e versão
        titulo = QLabel("AVERBSYS")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        versao = QLabel("Versão 0.1")
        versao.setObjectName("info")
        versao.setAlignment(Qt.AlignCenter)
        layout.addWidget(versao)
        
        layout.addSpacing(12)
        
        # Desenvolvedores
        dev_titulo = QLabel("Equipe de Desenvolvimento:")
        dev_titulo.setObjectName("subtitulo")
        layout.addWidget(dev_titulo)
        
        desenvolvedores = [
            "• Daniela Santana - Front End",
            "• Thiago Carvalho - Dev.", 
            "• Evandro Messias - Back End",
            "• Mateus Ferreira - Q.A.",
            "• Ariadna Oliveira - Creator"
        ]
        
        for dev in desenvolvedores:
            label = QLabel(dev)
            label.setObjectName("info")
            layout.addWidget(label)
        
        layout.addSpacing(10)
                
        dialog.setLayout(layout)
        dialog.exec_()

    
    
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
        # REMOVER: self.register_button.setEnabled(not loading)
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