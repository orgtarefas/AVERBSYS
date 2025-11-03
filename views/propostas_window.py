from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QTabWidget, QProgressBar, QComboBox, QCheckBox,
                             QGroupBox, QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from services.proposta_service import PropostaService
from utils.styles import get_propostas_styles
from utils.tarefas_fixas import get_tarefas_por_tipo
from datetime import datetime

class PropostasWindow(QWidget):
    logout_request = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.proposta_service = PropostaService()
        self.data_criacao = None
        self.tarefas_concluidas = {}
        self.tipo_proposta_atual = None
        self.numero_inputs = {}  # Para armazenar os inputs de cada aba
        self.checkboxes_dict = {}  # Para armazenar checkboxes de cada aba
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sistema de Propostas - AVERBSYS")
        self.setStyleSheet(get_propostas_styles())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = self.criar_header()
        
        # Tabs principais
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.aba_mudou)
        
        # Criar as 3 abas específicas
        self.tab_saque_facil = self.criar_aba_proposta("Saque Fácil")
        self.tab_refin = self.criar_aba_proposta("Refin") 
        self.tab_saque_direcionado = self.criar_aba_proposta("Saque Direcionado")
        
        # Tab de Histórico
        self.tab_historico = self.criar_aba_historico()
        
        # Adicionar tabs
        self.tabs.addTab(self.tab_saque_facil, "Saque Fácil")
        self.tabs.addTab(self.tab_refin, "Refin")
        self.tabs.addTab(self.tab_saque_direcionado, "Saque Direcionado")
        self.tabs.addTab(self.tab_historico, "Histórico")
        
        # Conectar sinais
        self.proposta_service.proposta_criada.connect(self.on_proposta_criada)
        
        layout.addWidget(header)
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
        self.resize(1200, 800)
        
        # Carregar dados iniciais
        self.carregar_historico()
    
    def criar_header(self):
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout()
        
        welcome_label = QLabel(f"Analista: {self.user_data['nome_completo']} - {self.user_data['perfil']}")
        welcome_label.setObjectName("welcomeLabel")
        
        self.logout_button = QPushButton("Sair")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.clicked.connect(self.logout_request.emit)
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_button)
        header.setLayout(header_layout)
        return header
    
    def criar_aba_proposta(self, tipo_proposta):
        aba = QWidget()
        layout = QVBoxLayout()
        
        # Área de entrada da proposta
        input_frame = self.criar_area_input(tipo_proposta)
        
        # Área de tarefas
        tarefas_frame = self.criar_area_tarefas(tipo_proposta)
        
        # Área de ações
        acoes_frame = self.criar_area_acoes(tipo_proposta)
        
        layout.addWidget(input_frame)
        layout.addWidget(tarefas_frame)
        layout.addWidget(acoes_frame)
        layout.addStretch()
        
        aba.setLayout(layout)
        return aba
    
    def criar_area_input(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        
        title = QLabel(f"{tipo_proposta} - Nova Proposta")
        title.setObjectName("titleLabel")
        
        # Layout horizontal para número e botão limpar
        input_layout = QHBoxLayout()
        
        numero_input = QLineEdit()
        numero_input.setPlaceholderText("Digite o número da proposta (9 dígitos)")
        numero_input.setObjectName("inputField")
        numero_input.setMaxLength(9)
        numero_input.textChanged.connect(lambda text: self.validar_numero_proposta(text, tipo_proposta))
        
        # Armazenar referência do input
        self.numero_inputs[tipo_proposta] = numero_input
        
        limpar_button = QPushButton("Limpar")
        limpar_button.setObjectName("secondaryButton")
        limpar_button.clicked.connect(lambda: self.limpar_proposta(tipo_proposta))
        
        input_layout.addWidget(QLabel("Nº Proposta:"))
        input_layout.addWidget(numero_input)
        input_layout.addWidget(limpar_button)
        
        # Info data/hora criação
        data_info_label = QLabel("Data/Hora Criação: --/--/-- --:--:--")
        data_info_label.setObjectName("infoLabel")
        
        # Armazenar referência do label
        self.data_info_labels = getattr(self, 'data_info_labels', {})
        self.data_info_labels[tipo_proposta] = data_info_label
        
        layout.addWidget(title)
        layout.addLayout(input_layout)
        layout.addWidget(data_info_label)
        
        frame.setLayout(layout)
        return frame
    
    def criar_area_tarefas(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        
        title = QLabel("Tarefas da Proposta - Marque as concluídas (✓)")
        title.setObjectName("subtitleLabel")
        
        # Scroll area para tarefas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(300)
        
        tarefas_widget = QWidget()
        tarefas_layout = QGridLayout()
        
        # Carregar tarefas específicas do tipo
        tarefas = get_tarefas_por_tipo(tipo_proposta)
        checkboxes = {}
        
        row, col = 0, 0
        for key, descricao in tarefas.items():
            checkbox = QCheckBox(descricao)
            checkbox.setObjectName("checkbox")
            checkbox.setEnabled(False)  # Inicialmente desabilitado
            checkbox.stateChanged.connect(lambda state, k=key, tp=tipo_proposta: self.atualizar_tarefa(k, state, tp))
            checkboxes[key] = checkbox
            
            tarefas_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 1:  # 2 colunas
                col = 0
                row += 1
        
        # Armazenar checkboxes desta aba
        self.checkboxes_dict[tipo_proposta] = checkboxes
        
        tarefas_widget.setLayout(tarefas_layout)
        scroll.setWidget(tarefas_widget)
        
        layout.addWidget(title)
        layout.addWidget(scroll)
        
        frame.setLayout(layout)
        return frame
    
    def criar_area_acoes(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QHBoxLayout()
        
        aprovar_button = QPushButton("✅ Aprovar Proposta")
        aprovar_button.setObjectName("successButton")
        aprovar_button.clicked.connect(lambda: self.finalizar_proposta(tipo_proposta, "Aprovada"))
        aprovar_button.setEnabled(False)
        
        recusar_button = QPushButton("❌ Recusar Proposta")  
        recusar_button.setObjectName("dangerButton")
        recusar_button.clicked.connect(lambda: self.finalizar_proposta(tipo_proposta, "Recusada"))
        recusar_button.setEnabled(False)
        
        # Armazenar referências dos botões
        self.aprovar_buttons = getattr(self, 'aprovar_buttons', {})
        self.recusar_buttons = getattr(self, 'recusar_buttons', {})
        self.aprovar_buttons[tipo_proposta] = aprovar_button
        self.recusar_buttons[tipo_proposta] = recusar_button
        
        layout.addWidget(aprovar_button)
        layout.addWidget(recusar_button)
        
        frame.setLayout(layout)
        return frame
    
    def criar_aba_historico(self):
        aba = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Histórico de Propostas")
        title.setObjectName("titleLabel")
        
        self.historico_table = QTableWidget()
        self.historico_table.setColumnCount(7)
        self.historico_table.setHorizontalHeaderLabels([
            "Tipo", "Número", "Analista", "Status", "Data Criação", "Data Conclusão", "Duração"
        ])
        self.historico_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(title)
        layout.addWidget(self.historico_table)
        
        aba.setLayout(layout)
        return aba
    
    def aba_mudou(self, index):
        """Quando muda de aba, reseta o estado"""
        self.tipo_proposta_atual = None
        self.data_criacao = None
        self.tarefas_concluidas = {}
    
    def validar_numero_proposta(self, texto, tipo_proposta):
        # Validar se é número e tem 9 dígitos
        if texto.isdigit() and len(texto) == 9:
            # TRAVAR o campo de entrada
            self.numero_inputs[tipo_proposta].setEnabled(False)
            
            # Registrar data/hora de criação
            if not self.data_criacao:
                self.data_criacao = datetime.now()
                self.tipo_proposta_atual = tipo_proposta
                self.data_info_labels[tipo_proposta].setText(
                    f"Data/Hora Criação: {self.data_criacao.strftime('%d/%m/%Y %H:%M:%S')}"
                )
            
            # HABILITAR os checkboxes
            for checkbox in self.checkboxes_dict[tipo_proposta].values():
                checkbox.setEnabled(True)
            
            # HABILITAR botões Aprovar/Recusar
            self.aprovar_buttons[tipo_proposta].setEnabled(True)
            self.recusar_buttons[tipo_proposta].setEnabled(True)
            
        else:
            # Manter tudo desabilitado se não for válido
            self.numero_inputs[tipo_proposta].setEnabled(True)
            for checkbox in self.checkboxes_dict[tipo_proposta].values():
                checkbox.setEnabled(False)
            self.aprovar_buttons[tipo_proposta].setEnabled(False)
            self.recusar_buttons[tipo_proposta].setEnabled(False)
    
    def atualizar_tarefa(self, tarefa_key, estado, tipo_proposta):
        self.tarefas_concluidas[tarefa_key] = (estado == Qt.Checked)
    
    def limpar_proposta(self, tipo_proposta):
        # Reabilitar campo de número
        self.numero_inputs[tipo_proposta].setEnabled(True)
        self.numero_inputs[tipo_proposta].clear()
        
        # Resetar data
        self.data_criacao = None
        self.data_info_labels[tipo_proposta].setText("Data/Hora Criação: --/--/-- --:--:--")
        self.tarefas_concluidas = {}
        
        # Desabilitar checkboxes
        for checkbox in self.checkboxes_dict[tipo_proposta].values():
            checkbox.setEnabled(False)
            checkbox.setChecked(False)
        
        # Desabilitar botões
        self.aprovar_buttons[tipo_proposta].setEnabled(False)
        self.recusar_buttons[tipo_proposta].setEnabled(False)
        
        QMessageBox.information(self, "Limpeza", "Proposta limpa com sucesso!")
    
    def finalizar_proposta(self, tipo_proposta, status):
        numero = self.numero_inputs[tipo_proposta].text().strip()
        
        if not numero or len(numero) != 9:
            QMessageBox.warning(self, "Erro", "Número da proposta inválido!")
            return
        
        # Verificar se pelo menos uma tarefa foi concluída
        tarefas_concluidas = any(self.tarefas_concluidas.values())
        if not tarefas_concluidas:
            QMessageBox.warning(self, "Atenção", "Marque pelo menos uma tarefa como concluída!")
            return
        
        # Criar e finalizar proposta
        self.proposta_service.criar_e_finalizar_proposta(
            numero, 
            self.user_data['login'], 
            tipo_proposta,
            self.tarefas_concluidas,
            status
        )
    
    def on_proposta_criada(self, success, message):
        if success:
            QMessageBox.information(self, "Sucesso", message)
            
            # Limpar formulário da aba atual
            if self.tipo_proposta_atual:
                self.limpar_proposta(self.tipo_proposta_atual)
            
            # Atualizar histórico
            self.carregar_historico()
        else:
            QMessageBox.warning(self, "Erro", message)
    
    def carregar_historico(self):
        propostas = self.proposta_service.listar_todas_propostas()
        self.preencher_tabela_historico(propostas)
    
    def preencher_tabela_historico(self, propostas):
        self.historico_table.setRowCount(len(propostas))
        
        for row, proposta in enumerate(propostas):
            self.historico_table.setItem(row, 0, QTableWidgetItem(proposta['tipo_proposta']))
            self.historico_table.setItem(row, 1, QTableWidgetItem(str(proposta['numero_proposta'])))
            self.historico_table.setItem(row, 2, QTableWidgetItem(proposta['analista']))
            
            status_item = QTableWidgetItem(proposta['status'])
            if proposta['status'] == 'Aprovada':
                status_item.setBackground(Qt.green)
            elif proposta['status'] == 'Recusada':
                status_item.setBackground(Qt.red)
            elif proposta['status'] == 'Pendente':
                status_item.setBackground(Qt.yellow)
            
            self.historico_table.setItem(row, 3, status_item)
            
            # Formatar datas
            data_criacao = proposta['data_criacao']
            if hasattr(data_criacao, 'strftime'):
                self.historico_table.setItem(row, 4, QTableWidgetItem(data_criacao.strftime("%d/%m/%Y %H:%M:%S")))
            else:
                self.historico_table.setItem(row, 4, QTableWidgetItem(str(data_criacao)))
            
            data_conclusao = proposta.get('data_conclusao')
            if data_conclusao and hasattr(data_conclusao, 'strftime'):
                self.historico_table.setItem(row, 5, QTableWidgetItem(data_conclusao.strftime("%d/%m/%Y %H:%M:%S")))
            else:
                self.historico_table.setItem(row, 5, QTableWidgetItem(" - "))
            
            self.historico_table.setItem(row, 6, QTableWidgetItem(proposta.get('duracao_total', ' - ')))