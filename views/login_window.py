from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QProgressBar, QDialog, QCheckBox)  
from PyQt5.QtCore import pyqtSignal, Qt, QSettings
from PyQt5.QtGui import QPixmap, QIcon
from utils.styles import get_login_styles
from services.proposta_service import PropostaService
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
        self.settings = QSettings("AVERBSYS", "LoginApp")
        self.proposta_service = PropostaService() 
        self.versao_local = "0.2"  # versão
        self.init_ui()
        self.load_saved_credentials()
        self.verificar_versao_sistema()

    def verificar_versao_sistema(self):
        """Verifica se a versão local é compatível com a do Firebase"""
        try:
            print("🔍 Verificando versão do sistema...")
            versao_firebase = self.proposta_service.obter_versao_sistema()
            
            if versao_firebase:
                print(f"📊 Versão Local: {self.versao_local} | Versão Firebase: {versao_firebase}")
                
                if versao_firebase != self.versao_local:
                    self.mostrar_erro_versao(versao_firebase)
                    return False
                else:
                    print("✅ Versão compatível!")
                    return True
            else:
                print("⚠️  Não foi possível verificar a versão do Firebase")
                return True  # Permite login mesmo sem conseguir verificar
                
        except Exception as e:
            print(f"❌ Erro ao verificar versão: {e}")
            return True  # Permite login em caso de erro        

    def mostrar_erro_versao(self, versao_firebase):
        """Mostra mensagem de erro de versão e bloqueia o login"""
        mensagem = f"""
        ⚠️ **ATUALIZAÇÃO NECESSÁRIA**

        A versão do sistema local (v{self.versao_local}) não é compatível 
        com a versão do servidor (v{versao_firebase}).

        **Por favor, entre em contato com a equipe de desenvolvimento 
        para obter a versão mais recente do sistema.**
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Versão Incompatível")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(mensagem)
        
        # Tentar carregar o ícone
        try:
            msg_box.setWindowIcon(QIcon(resource_path('assets/logo.png')))
        except:
            pass
            
        # Botão personalizado
        btn_ok = msg_box.addButton("Fechar Sistema", QMessageBox.AcceptRole)
        msg_box.exec_()
        
        # Fechar o sistema
        sys.exit(1)        
    
    def init_ui(self):
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
        
        # Layout para senha com botão de mostrar/ocultar
        password_layout = QHBoxLayout()
        password_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("inputField")
        
        # Botão para mostrar/ocultar senha
        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setObjectName("togglePasswordButton")
        self.toggle_password_button.setFixedSize(30, 30)
        self.toggle_password_button.setCursor(Qt.PointingHandCursor)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        
        # Definir ícone inicial (olho fechado)
        self.update_toggle_password_icon()
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)
        
        # Checkbox para lembrar credenciais
        self.remember_me_checkbox = QCheckBox("Lembrar usuário e senha")
        self.remember_me_checkbox.setObjectName("rememberCheckbox")
        
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
        form_layout.addLayout(password_layout)
        form_layout.addWidget(self.remember_me_checkbox)
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
        self.resize(400, 600)  # Aumentei um pouco a altura para acomodar os novos elementos
        self.center_window()

    def toggle_password_visibility(self):
        """Alterna entre mostrar e ocultar a senha"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
        
        self.update_toggle_password_icon()

    def update_toggle_password_icon(self):
        """Atualiza o ícone do botão de mostrar/ocultar senha"""
        if self.password_input.echoMode() == QLineEdit.Password:
            # Ícone de olho (senha oculta)
            try:
                icon_path = resource_path('assets/eye_closed.png')
                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    pixmap = pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.toggle_password_button.setIcon(QIcon(pixmap))
                else:
                    self.toggle_password_button.setText("👁")
            except:
                self.toggle_password_button.setText("👁")
        else:
            # Ícone de olho riscado (senha visível)
            try:
                icon_path = resource_path('assets/eye_open.png')
                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    pixmap = pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.toggle_password_button.setIcon(QIcon(pixmap))
                else:
                    self.toggle_password_button.setText("👁‍🗨")
            except:
                self.toggle_password_button.setText("👁‍🗨")

    def load_saved_credentials(self):
        """Carrega usuário e senha salvos se 'Lembrar' estiver ativo"""
        remember_me = self.settings.value("remember_me", False, type=bool)
        
        if remember_me:
            # ⭐ CARREGA USUÁRIO E SENHA
            username = self.settings.value("username", "")
            password = self.settings.value("password", "")  # ⭐ CARREGA SENHA
            
            self.username_input.setText(username)
            self.password_input.setText(password)
            self.remember_me_checkbox.setChecked(True)
        else:
            # ⭐ DESMARCADO: LIMPA TUDO
            self.username_input.clear()
            self.password_input.clear()
            self.remember_me_checkbox.setChecked(False)
        
        # Mantém o foco no campo apropriado
        if self.username_input.text():
            self.password_input.setFocus()
        else:
            self.username_input.setFocus()

    def save_credentials(self):
        """Salva ou remove as credenciais baseado no checkbox"""
        if self.remember_me_checkbox.isChecked():
            # ⭐ SALVA USUÁRIO E SENHA se estiver marcado
            self.settings.setValue("remember_me", True)
            self.settings.setValue("username", self.username_input.text())
            self.settings.setValue("password", self.password_input.text())  # ⭐ SALVA SENHA
        else:
            # ⭐ DESMARCADO: REMOVE TUDO
            self.settings.setValue("remember_me", False)
            self.settings.remove("username")
            self.settings.remove("password")
        
        # Force salvar imediatamente
        self.settings.sync()

    def attempt_login(self):
        # ⭐⭐ VERIFICAR VERSÃO ANTES DO LOGIN
        if not self.verificar_versao_sistema():
            return
            
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # ⭐⭐ CORREÇÃO: Validação mais robusta
        if not username:
            self.show_error("Por favor, informe o usuário")
            self.username_input.setFocus()
            return
            
        if not password:
            self.show_error("Por favor, informe a senha")
            self.password_input.setFocus()
            return
        
        if len(username) < 3:
            self.show_error("Usuário deve ter pelo menos 3 caracteres")
            self.username_input.setFocus()
            return
        
        # Salva as credenciais antes de tentar o login
        self.save_credentials()
        
        self.set_loading(True)
        self.login_attempt.emit(username, password)

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
        
        versao = QLabel(f"Versão {self.versao_local}")  # ⭐⭐ USAR VARIÁVEL DA VERSÃO
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
    
    def set_loading(self, loading):
        self.login_button.setEnabled(not loading)
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