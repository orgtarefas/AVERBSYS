from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QProgressBar, QDialog)  
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from utils.styles import get_login_styles

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
            self.setWindowIcon(QIcon('assets/logo.png'))
        except:
            print("Logo não encontrada. Verifique o caminho: assets/logo.png")
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # LOGO COMPLETA (COM NOME) NO CENTRO
        try:
            logo_label = QLabel()
            pixmap = QPixmap('assets/logo_completa.png')  # Logo com nome
            # Redimensionar a logo
            pixmap = pixmap.scaled(300, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("margin-bottom: 20px;")
            layout.addWidget(logo_label)
        except Exception as e:
            print(f"Logo completa não encontrada. Verifique o caminho: assets/logo_completa.png - {e}")
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
            pixmap = QPixmap('assets/sobre.png')
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


    def mostrar_informacoes(self):
        """Mostra informações dos desenvolvedores e links com logo"""
        # Criar uma janela personalizada
        dialog = QDialog(self)
        dialog.setWindowTitle("Sobre o Sistema")
        
        # DEFINIR ÍCONE NA JANELA DE SOBRE (MESMO logo.png)
        try:
            dialog.setWindowIcon(QIcon('assets/logo.png'))
        except:
            print("Logo não encontrada para janela sobre. Verifique o caminho: assets/logo.png")
        
        dialog.setFixedSize(450, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #2c3e50;
            }
            QLabel#titulo {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0px;
            }
            QLabel#info {
                font-size: 12px;
                color: #7f8c8d;
                margin: 3px 0px;
            }
            QLabel#link {
                font-size: 12px;
                color: #3498db;
                margin: 3px 0px;
            }
            QLabel#link:hover {
                color: #2980b9;
                text-decoration: underline;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # LOGO NO TOPO (MESMO logo.png)
        try:
            logo_label = QLabel()
            pixmap = QPixmap('assets/logo.png')
            pixmap = pixmap.scaled(200, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        except Exception as e:
            print(f"Logo não encontrada para janela sobre: {e}")
            # Fallback: texto
            titulo_logo = QLabel("AVERBSYS")
            titulo_logo.setAlignment(Qt.AlignCenter)
            titulo_logo.setObjectName("titulo")
            layout.addWidget(titulo_logo)
        
        # Linha divisória
        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        linha.setFrameShadow(QFrame.Sunken)
        linha.setStyleSheet("background-color: #ecf0f1; margin: 10px 0px;")
        layout.addWidget(linha)
        
        # Título
        titulo = QLabel("Sistema de Propostas")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        # Versão
        versao = QLabel("Versão 0.1")
        versao.setAlignment(Qt.AlignCenter)
        versao.setObjectName("info")
        layout.addWidget(versao)
        
        layout.addSpacing(5)
        
        # Equipe de desenvolvimento
        equipe_titulo = QLabel("Equipe de Desenvolvimento:")
        equipe_titulo.setObjectName("titulo")
        equipe_titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 15px 0px 10px 0px;")  # MAIOR
        layout.addWidget(equipe_titulo)

        equipe_layout = QVBoxLayout()
        equipe_layout.setSpacing(8)  # MAIS ESPAÇAMENTO

        membros = [
            "Front End: Daniela Santana",
            "Dev: Thiago Carvalho", 
            "Back End: Evandro Messias",
            "QA: Mateus Ferreira"
        ]

        for membro in membros:
            label = QLabel(f"• {membro}")
            label.setStyleSheet("font-size: 14px; color: #5a6c7d; margin: 5px 0px; padding: 2px;")  # MAIOR
            equipe_layout.addWidget(label)

        layout.addLayout(equipe_layout)
        layout.addSpacing(15)  # MAIS ESPAÇAMENTO
        
        # Links futuros
        links_titulo = QLabel("Links Futuros:")
        links_titulo.setObjectName("titulo")
        links_titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 15px 0px 10px 0px;")  # MESMO TAMANHO
        layout.addWidget(links_titulo)

        links_layout = QVBoxLayout()
        links_layout.setSpacing(8)  # MAIS ESPAÇAMENTO

        # Link Documentação
        doc_label = QLabel('• <a href="https://docs.averbsys.com" style="color: #3498db; text-decoration: none; font-size: 14px;">📚 Documentação</a>')  # MAIOR
        doc_label.setTextFormat(Qt.RichText)
        doc_label.setOpenExternalLinks(True)
        doc_label.setObjectName("link")
        links_layout.addWidget(doc_label)

        # Link Manual
        manual_label = QLabel('• <a href="https://manual.averbsys.com" style="color: #3498db; text-decoration: none; font-size: 14px;">📖 Manual de Uso</a>')  # MAIOR
        manual_label.setTextFormat(Qt.RichText)
        manual_label.setOpenExternalLinks(True)
        manual_label.setObjectName("link")
        links_layout.addWidget(manual_label)

        layout.addLayout(links_layout)
        
        # Nota sobre links
        nota = QLabel("<i>Links serão disponibilizados em breve</i>")
        nota.setAlignment(Qt.AlignCenter)
        nota.setObjectName("info")
        nota.setStyleSheet("font-size: 10px; margin-top: 10px;")
        layout.addWidget(nota)
        
        layout.addStretch()
        
        # Botão Fechar
        botao_layout = QHBoxLayout()
        botao_layout.addStretch()
        
        fechar_button = QPushButton("Fechar")
        fechar_button.clicked.connect(dialog.accept)
        botao_layout.addWidget(fechar_button)
        
        botao_layout.addStretch()
        layout.addLayout(botao_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()

    
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