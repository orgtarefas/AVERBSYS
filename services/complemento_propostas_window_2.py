from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
import sys

class PropostasWindowPart2:
    """Parte 2 - Criação do header e configuração de botões por perfil"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def criar_header(self):
        header = QFrame()
        header.setObjectName("header")
        header_layout = QVBoxLayout()  # MUDADO para VBoxLayout
        
        # LINHA SUPERIOR: Logo + Nome + Welcome + Botões
        top_layout = QHBoxLayout()
        
        # LOGO + NOME (LADO ESQUERDO)
        logo_nome_layout = QHBoxLayout()
        try:
            logo_label = QLabel()
            pixmap = QPixmap(self.resource_path('assets/logo.png'))
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_nome_layout.addWidget(logo_label)
            logo_nome_layout.addSpacing(8)
        except Exception as e:
            print(f"Logo não encontrada: {e}")
        
        # Nome do sistema + versão
        nome_versao_layout = QVBoxLayout()
        nome_versao_layout.setSpacing(0)
        
        logo_nome_layout.addStretch()
        
        # Botões no lado direito
        botoes_layout = QHBoxLayout()
        
        # Botão Cadastrar Usuário (apenas para Dev)
        self.cadastrar_button = QPushButton("➕ Cadastrar Usuário")
        self.cadastrar_button.setObjectName("primaryButton")
        self.cadastrar_button.clicked.connect(self.cadastrar_usuario)
        
        # Botão Manutenção de Usuários (apenas para Gerente e Dev)
        self.manutencao_button = QPushButton("👥 Manutenção de Usuários")
        self.manutencao_button.setObjectName("primaryButton")
        self.manutencao_button.clicked.connect(self.abrir_manutencao_usuarios.emit)
        
        # Botão Sair
        self.logout_button = QPushButton("Sair")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.clicked.connect(self.on_sair_clicked)
        
        # Configurar visibilidade dos botões baseado no perfil
        self.configurar_botoes_por_perfil()
        
        # Adicionar botões ao layout
        botoes_layout.addWidget(self.cadastrar_button)
        botoes_layout.addWidget(self.manutencao_button)
        botoes_layout.addWidget(self.logout_button)
        
        # Adicionar tudo ao top_layout
        top_layout.addLayout(logo_nome_layout)
        top_layout.addStretch()
        top_layout.addLayout(botoes_layout)
        
        # LINHA INFERIOR: Apenas as abas (sem botões)
        # As abas serão adicionadas no layout principal depois
        
        # Adicionar top_layout ao header
        header_layout.addLayout(top_layout)
        header.setLayout(header_layout)
        return header
    
    def on_sair_clicked(self):
        """Executado quando clica no botão Sair"""
        # Salva as credenciais antes de sair (se necessário)
        self.salvar_credenciais_antes_de_sair()
        
        # Emite o sinal para voltar ao login
        self.logout_request.emit()
        
        # Fecha esta janela
        self.close()
    
    def salvar_credenciais_antes_de_sair(self):
        """Garante que as credenciais estão salvas antes de sair"""
        # Se você tem acesso às credenciais atuais, salve-as
        # Ou apenas force o QSettings a sincronizar
        from PyQt5.QtCore import QSettings
        settings = QSettings("AVERBSYS", "LoginApp")
        settings.sync()  # Force salvar no disco
    
    def configurar_botoes_por_perfil(self):
        """Configura a visibilidade dos botões baseado no perfil do usuário"""
        perfil = self.user_data['perfil']
        
        # Cadastrar Usuário: apenas Dev
        self.cadastrar_button.setVisible(perfil == 'Dev')
        
        # Manutenção de Usuários: Dev, Gerente e Supervisor (mas com permissões diferentes)
        self.manutencao_button.setVisible(perfil in ['Dev', 'Gerente', 'Supervisor'])
    
    def cadastrar_usuario(self):
        """Abre a tela de cadastro de usuário"""
        self.abrir_cadastro_usuario.emit()