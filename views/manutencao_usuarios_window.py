from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from services.user_service import UserService  # CORREÇÃO AQUI
from utils.styles import get_propostas_styles

class ManutencaoUsuariosWindow(QWidget):
    fechar_request = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.user_service = UserService()  # CORREÇÃO AQUI
        self.usuario_selecionado = None
        self.init_ui()
        self.carregar_usuarios()
    
    def init_ui(self):
        self.setWindowTitle("Manutenção de Usuários - AVERBSYS")
        self.setStyleSheet(get_propostas_styles())
        self.resize(1000, 700)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = self.criar_header()
        
        # Área principal
        main_layout = QHBoxLayout()
        
        # Lista de usuários
        lista_frame = self.criar_lista_usuarios()
        
        # Formulário de edição
        form_frame = self.criar_formulario_edicao()
        
        main_layout.addWidget(lista_frame, 1)
        main_layout.addWidget(form_frame, 1)
        
        layout.addWidget(header)
        layout.addLayout(main_layout)
        
        self.setLayout(layout)
    
    def criar_header(self):
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout()
        
        title = QLabel("Manutenção de Usuários")
        title.setObjectName("titleLabel")
        
        fechar_button = QPushButton("Voltar")
        fechar_button.setObjectName("backButton")  
        fechar_button.clicked.connect(self.fechar_request.emit)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(fechar_button)
        
        header.setLayout(header_layout)
        return header
    
    def criar_lista_usuarios(self):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        
        title = QLabel("Lista de Usuários")
        title.setObjectName("subtitleLabel")
        
        self.tabela_usuarios = QTableWidget()
        self.tabela_usuarios.setColumnCount(4)
        self.tabela_usuarios.setHorizontalHeaderLabels([
            "Login", "Nome Completo", "Perfil", "Status"
        ])
        self.tabela_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_usuarios.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_usuarios.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_usuarios.itemSelectionChanged.connect(self.usuario_selecionado_changed)
        
        # ESTILO PARA GARANTIR TEXTO PRETO SEMPRE
        self.tabela_usuarios.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item {
                color: black;
                background-color: white;
                padding: 5px;
            }
            QTableWidget::item:selected {
                color: black;
                background-color: #e0e0e0;
            }
            QTableWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(self.tabela_usuarios)
        
        frame.setLayout(layout)
        return frame
    
    def criar_formulario_edicao(self):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        
        title = QLabel("Editar Usuário")
        title.setObjectName("subtitleLabel")
        
        # Formulário
        form_group = QGroupBox("Dados do Usuário")
        form_layout = QFormLayout()
        
        self.login_label = QLabel("--")
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome completo")
        
        self.perfil_combo = QComboBox()
        self.perfil_combo.addItems(["Analista", "Supervisor", "Gerente", "Dev"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Ativo", "Bloqueado"])
        
        # NOVO: Campo para senha
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Deixe em branco para manter a senha atual")
        self.senha_input.setEchoMode(QLineEdit.Password)
        
        self.senha_button = QPushButton("🔑 Resetar Senha")
        self.senha_button.setObjectName("primaryButton")
        self.senha_button.clicked.connect(self.resetar_senha)
        
        self.salvar_button = QPushButton("💾 Salvar Alterações")
        self.salvar_button.setObjectName("successButton")
        self.salvar_button.clicked.connect(self.salvar_alteracoes)
        
        form_layout.addRow("Login:", self.login_label)
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Perfil:", self.perfil_combo)
        form_layout.addRow("Status:", self.status_combo)
       # form_layout.addRow("Nova Senha:", self.senha_input)  # NOVO CAMPO
        form_layout.addRow(self.senha_button)
        form_layout.addRow(self.salvar_button)
        
        form_group.setLayout(form_layout)
        
        layout.addWidget(title)
        layout.addWidget(form_group)
        
        # Inicialmente desabilitar o formulário
        self.habilitar_formulario(False)
        
        frame.setLayout(layout)
        return frame
    
    def carregar_usuarios(self):
        try:
            usuarios = self.user_service.listar_todos_usuarios()
            
            # FILTRAR USUÁRIOS CONFORME O PERFIL DO USUÁRIO LOGADO
            usuarios_filtrados = self.filtrar_usuarios_por_permissao(usuarios)
            
            self.preencher_tabela_usuarios(usuarios_filtrados)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar usuários: {str(e)}")

    def filtrar_usuarios_por_permissao(self, usuarios):
        """Filtra os usuários que podem ser visualizados conforme o perfil"""
        perfil_usuario_logado = self.user_data['perfil']
        
        if perfil_usuario_logado == 'Dev':
            # Dev vê todos os usuários
            return usuarios
        elif perfil_usuario_logado == 'Gerente':
            # Gerente não vê usuários Dev
            return [usuario for usuario in usuarios if usuario['perfil'] != 'Dev']
        elif perfil_usuario_logado == 'Supervisor':
            # Supervisor só vê Supervisor e Analista
            return [usuario for usuario in usuarios if usuario['perfil'] in ['Supervisor', 'Analista']]
        else:
            # Outros perfis não deveriam acessar, mas por segurança retorna vazio
            return []            
    
    def preencher_tabela_usuarios(self, usuarios):
        self.tabela_usuarios.setRowCount(len(usuarios))
        
        for row, usuario in enumerate(usuarios):
            # Criar itens normalmente
            item_login = QTableWidgetItem(usuario['login'])
            item_nome = QTableWidgetItem(usuario['nome_completo'])
            item_perfil = QTableWidgetItem(usuario['perfil'])
            item_status = QTableWidgetItem(usuario['status'])
            
            # Apenas configurar o fundo para status, o estilo CSS cuida da cor do texto
            if usuario['status'] == 'Ativo':
                item_status.setBackground(Qt.green)
            else:
                item_status.setBackground(Qt.red)
                        
            self.tabela_usuarios.setItem(row, 0, item_login)
            self.tabela_usuarios.setItem(row, 1, item_nome)
            self.tabela_usuarios.setItem(row, 2, item_perfil)
            self.tabela_usuarios.setItem(row, 3, item_status)
    
    def usuario_selecionado_changed(self):
        selected_items = self.tabela_usuarios.selectedItems()
        if not selected_items:
            self.habilitar_formulario(False)
            return
        
        # Obter dados do usuário selecionado
        row = selected_items[0].row()
        login = self.tabela_usuarios.item(row, 0).text()
        nome = self.tabela_usuarios.item(row, 1).text()
        perfil = self.tabela_usuarios.item(row, 2).text()
        status = self.tabela_usuarios.item(row, 3).text()
        
        self.usuario_selecionado = {
            'login': login,
            'nome_completo': nome,
            'perfil': perfil,
            'status': status
        }
        
        # Preencher formulário
        self.login_label.setText(login)
        self.nome_input.setText(nome)
        self.perfil_combo.setCurrentText(perfil)
        self.status_combo.setCurrentText(status)
        self.senha_input.clear()  # LIMPAR campo de senha quando selecionar novo usuário
        
        # Habilitar formulário
        self.habilitar_formulario(True)
        
        # Habilitar/desabilitar controles baseado no perfil do usuário logado
        self.habilitar_controles_por_perfil()
    
    def habilitar_controles_por_perfil(self):
        """Habilita/desabilita controles baseado no perfil do usuário logado"""
        perfil_usuario_logado = self.user_data['perfil']
        
        # Resetar senha: permitido para Supervisor, Gerente e Dev
        self.senha_button.setEnabled(perfil_usuario_logado in ['Supervisor', 'Gerente', 'Dev'])
        
        # Alterar perfil: permitido apenas para Dev
        self.perfil_combo.setEnabled(perfil_usuario_logado == 'Dev')
        
        # Alterar status: permitido apenas para Dev
        self.status_combo.setEnabled(perfil_usuario_logado == 'Dev')
        
        # Alterar nome: permitido apenas para Dev e Gerente
        self.nome_input.setEnabled(perfil_usuario_logado in ['Dev', 'Gerente'])
        
        # Para Gerente: pode resetar senha e alterar nome, mas não alterar perfil ou status
        if perfil_usuario_logado == 'Gerente':
            self.perfil_combo.setEnabled(False)
            self.status_combo.setEnabled(False)
        
        # Para Supervisor: pode apenas resetar senha
        if perfil_usuario_logado == 'Supervisor':
            self.perfil_combo.setEnabled(False)
            self.status_combo.setEnabled(False)
            self.nome_input.setEnabled(False)
    
    def habilitar_formulario(self, habilitar):
        self.nome_input.setEnabled(habilitar and self.user_data['perfil'] in ['Dev', 'Gerente'])
        self.perfil_combo.setEnabled(habilitar and self.user_data['perfil'] == 'Dev')
        self.status_combo.setEnabled(habilitar and self.user_data['perfil'] == 'Dev')
        self.senha_input.setEnabled(habilitar and self.user_data['perfil'] in ['Dev', 'Gerente'])
        self.senha_button.setEnabled(habilitar and self.user_data['perfil'] in ['Supervisor', 'Gerente', 'Dev'])
        self.salvar_button.setEnabled(habilitar)
    
    def resetar_senha(self):
        if not self.usuario_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário primeiro!")
            return
        
        # Diálogo para escolher a nova senha
        from PyQt5.QtWidgets import QInputDialog
        
        nova_senha, ok = QInputDialog.getText(
            self, 
            "Resetar Senha", 
            f"Digite a nova senha para {self.usuario_selecionado['login']}:",
            QLineEdit.Password
        )
        
        if ok and nova_senha:
            try:
                success = self.user_service.resetar_senha(
                    self.usuario_selecionado['login'], 
                    nova_senha
                )
                if success:
                    QMessageBox.information(self, "Sucesso", "Senha resetada com sucesso!")
                else:
                    QMessageBox.warning(self, "Erro", "Erro ao resetar senha!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao resetar senha: {str(e)}")
        elif ok and not nova_senha:
            QMessageBox.warning(self, "Aviso", "A senha não pode estar vazia!")
    
    def salvar_alteracoes(self):
        if not self.usuario_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário primeiro!")
            return
        
        try:
            dados_atualizados = {
                'nome_completo': self.nome_input.text().strip(),
                'perfil': self.perfil_combo.currentText(),
                'status': self.status_combo.currentText()
            }
            
            # Validar dados
            if not dados_atualizados['nome_completo']:
                QMessageBox.warning(self, "Aviso", "O nome completo é obrigatório!")
                return
            
            # Se foi preenchida uma nova senha, adicionar aos dados atualizados
            nova_senha = self.senha_input.text().strip()
            if nova_senha:
                dados_atualizados['senha'] = nova_senha
                # Limpar o campo de senha após usar
                self.senha_input.clear()
            
            success = self.user_service.atualizar_usuario(
                self.usuario_selecionado['login'],
                dados_atualizados
            )
            
            if success:
                QMessageBox.information(self, "Sucesso", "Usuário atualizado com sucesso!")
                self.carregar_usuarios()  # Recarregar lista
            else:
                QMessageBox.warning(self, "Erro", "Erro ao atualizar usuário!")
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar usuário: {str(e)}")