from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QTabWidget, QProgressBar, QComboBox, QCheckBox,
                             QGroupBox, QGridLayout, QScrollArea, QDateEdit,
                             QFormLayout, QFileDialog, QDialog, QListWidget,
                             QListWidgetItem, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QIntValidator, QPixmap, QIcon
import os
from datetime import datetime, timedelta
from services.proposta_service import PropostaService
from services.user_service import UserService
from utils.styles import get_propostas_styles
from utils.tarefas_fixas import get_tarefas_por_tipo
from utils.motivos_recusa import get_motivos_recusa, get_motivo_por_id
import pandas as pd
import requests
from io import StringIO
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils.dataframe import dataframe_to_rows
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    print("Aviso: openpyxl não instalado. Instale com: pip install openpyxl")
import sys
import os    

class MotivoRecusaDialog(QDialog):
    motivo_selecionado = pyqtSignal(str, str)  # id, descricao
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Motivo da Recusa")
        self.setModal(True)
        self.resize(400, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Selecione o motivo da recusa:")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Lista de motivos
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 1px solid #1976d2;
                border-radius: 3px;
            }
        """)
        
        # Adicionar motivos à lista usando a função do arquivo utils
        motivos = get_motivos_recusa()
        for motivo_id, descricao in motivos:
            item = QListWidgetItem(f"{motivo_id} - {descricao}")
            item.setData(Qt.UserRole, (motivo_id, descricao))
            self.list_widget.addItem(item)
        
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def on_item_double_clicked(self, item):
        """Quando o usuário clica duas vezes em um item"""
        self.on_accept()
    
    def on_accept(self):
        """Quando o usuário clica em OK"""
        current_item = self.list_widget.currentItem()
        if current_item:
            motivo_id, descricao = current_item.data(Qt.UserRole)
            self.motivo_selecionado.emit(motivo_id, descricao)
            self.accept()
        else:
            QMessageBox.warning(self, "Atenção", "Por favor, selecione um motivo da recusa.")

class GoogleSheetsService:
    def __init__(self):
        self.dados = []
        self.carregar_dados_reais()
    
    def carregar_dados_reais(self):
        """Carrega dados reais da planilha Google Sheets pública"""
        try:
            # URL pública da planilha (formato correto para CSV)
            sheet_id = "1p0hnhlLH_xGKLNZzGkpC52V2o9mkCBYSTHIcxVix_GQ"
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            print("Tentando carregar dados da planilha...")
            
            # Fazer requisição para obter o CSV
            response = requests.get(url)
            response.raise_for_status()
            
            # Ler o CSV
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            print(f"Colunas encontradas: {df.columns.tolist()}")
            print(f"Total de linhas: {len(df)}")
            
            # Processar os dados - assumindo que as colunas são:
            # Coluna C = Convênio (índice 2), Coluna F = Produto (índice 5), 
            # Coluna G = Região (índice 6), Coluna H = Status (índice 7)
            dados_processados = []
            
            for index, row in df.iterrows():
                # Verificar se temos dados nas colunas necessárias
                if (len(row) > 7 and 
                    pd.notna(row.iloc[6]) and  # Região (G)
                    pd.notna(row.iloc[2]) and  # Convênio (C) 
                    pd.notna(row.iloc[5])):    # Produto (F)
                    
                    regiao = str(row.iloc[6]).strip()
                    convenio = str(row.iloc[2]).strip()
                    produto = str(row.iloc[5]).strip()
                    status = str(row.iloc[7]).strip() if len(row) > 7 and pd.notna(row.iloc[7]) else "N/A"
                    
                    dados_processados.append({
                        'Região': regiao,
                        'Convênio': convenio,
                        'Produto': produto,
                        'Status': status
                    })
            
            self.dados = dados_processados
            print(f"Dados reais carregados com sucesso: {len(self.dados)} registros")
            
            # Mostrar alguns registros para debug
         #   if self.dados:
         #       print("Primeiros 3 registros:")
         #       for i, item in enumerate(self.dados[:3]):
         #           print(f"  {i+1}: Região={item['Região']}, Convênio={item['Convênio']}, Produto={item['Produto']}, Status={item['Status']}")
         #   else:
         #       print("Nenhum dado válido encontrado na planilha")
         #       QMessageBox.warning(None, "Aviso", 
         #                         "Nenhum dado válido encontrado na planilha. Verifique a estrutura das colunas.")
                
        except Exception as e:
            print(f"Erro ao carregar dados reais: {e}")
            QMessageBox.warning(None, "Erro", 
                              f"Não foi possível carregar os dados da planilha: {str(e)}")
            self.dados = []
    
    def get_regioes(self):
        """Retorna lista única de regiões"""
        regioes = set()
        for row in self.dados:
            if row.get('Região') and row['Região'] != 'N/A':
                regioes.add(row['Região'])
        return sorted(list(regioes))
    
    def get_convenios_por_regiao(self, regiao):
        """Retorna convênios filtrados por região"""
        convenios = set()
        for row in self.dados:
            if (row.get('Região') == regiao and 
                row.get('Convênio') and row['Convênio'] != 'N/A'):
                convenios.add(row['Convênio'])
        return sorted(list(convenios))
    
    def get_produtos_por_convenio(self, convenio):
        """Retorna produtos filtrados por convênio"""
        produtos = set()
        for row in self.dados:
            if (row.get('Convênio') == convenio and 
                row.get('Produto') and row['Produto'] != 'N/A'):
                produtos.add(row['Produto'])
        return sorted(list(produtos))
    
    def get_status_por_produto(self, produto):
        """Retorna status para um produto específico"""
        for row in self.dados:
            if row.get('Produto') == produto:
                status = row.get('Status', 'Status não encontrado')
                return status if status != 'N/A' else 'Status não informado'
        return "Produto não encontrado"


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PropostasWindow(QWidget):
    logout_request = pyqtSignal()
    abrir_manutencao_usuarios = pyqtSignal()
    abrir_cadastro_usuario = pyqtSignal() 
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.proposta_service = PropostaService()
        self.user_service = UserService()
        self.google_sheets_service = GoogleSheetsService()
        
        self.data_criacao = None
        self.data_conclusao = None
        self.tarefas_concluidas = {}
        self.tipo_proposta_atual = None
        self.numero_inputs = {}
        self.checkboxes_dict = {}
        self.proposta_em_andamento = False
        
        # VARIÁVEIS PARA REANÁLISE
        self.eh_reanalise = False
        self.proposta_original = None
        
        # Dicionários para armazenar os comboboxes dos filtros
        self.regiao_combos = {}
        self.convenio_combos = {}
        self.produto_combos = {}
        self.status_labels = {}
        
        self.timer_duracao = QTimer()
        self.timer_duracao.timeout.connect(self.atualizar_duracao_display)
        self.init_ui()
    



    def init_ui(self):
        # DEFINIR ÍCONE DA JANELA
        try:
            self.setWindowIcon(QIcon('assets/logo.png'))
        except:
            print("Logo não encontrada. Verifique o caminho: assets/logo.png")




        self.setWindowTitle("AVERBSYS")
        self.setStyleSheet(get_propostas_styles())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # LINHA 1: AVERBSYS + User info + Botões
        header_layout = QHBoxLayout()
        
        
        # User info + Botões (LADO DIREITO)
        user_controls_layout = QHBoxLayout()
        user_controls_layout.setSpacing(5)
        
        # Informações do usuário
        user_info_label = QLabel(f"{self.user_data['nome_completo']} - {self.user_data['perfil']}")
        user_info_label.setObjectName("userInfoLabel")
        user_info_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                padding: 5px 10px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        
        # Botão Cadastrar Usuário (apenas para Dev)
        self.cadastrar_button = QPushButton("Cadastrar")
        self.cadastrar_button.setObjectName("primaryButton")
        self.cadastrar_button.clicked.connect(self.cadastrar_usuario)
        self.cadastrar_button.setFixedWidth(120)
        
        # Botão Manutenção de Usuários (apenas para Gerente e Dev)
        self.manutencao_button = QPushButton("Manutenção")
        self.manutencao_button.setObjectName("primaryButton")
        self.manutencao_button.clicked.connect(self.abrir_manutencao_usuarios.emit)
        self.manutencao_button.setFixedWidth(120)
        
        # Botão Sair
        self.logout_button = QPushButton("Sair")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.clicked.connect(self.logout_request.emit)
        self.logout_button.setFixedWidth(80)
        
        # Configurar visibilidade dos botões baseado no perfil
        self.configurar_botoes_por_perfil()
        
        # Adicionar controles ao layout
        user_controls_layout.addWidget(user_info_label)
        user_controls_layout.addWidget(self.cadastrar_button)
        user_controls_layout.addWidget(self.manutencao_button)
        user_controls_layout.addWidget(self.logout_button)
        
        # Adicionar ao header
        header_layout.addStretch()
        header_layout.addLayout(user_controls_layout)
        
        # LINHA 2: Tabs principais
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
        
        # Adicionar ao layout principal
        layout.addLayout(header_layout)
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
       # self.resize(900, 400)
   
        # TAMANHO RESPONSIVO baseado na tela
        self.ajustar_tamanho_responsivo()
        
        # Centralizar na tela
        self.center_window()    
        
        # Carregar dados iniciais
        self.carregar_historico()
        self.carregar_filtros_iniciais()


    def center_window(self):
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def ajustar_tamanho_responsivo(self):
        """Ajusta o tamanho da janela baseado no tamanho da tela"""
        screen = self.screen().availableGeometry()
        
        # Usar porcentagem da tela (80% da largura, 70% da altura)
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.7)
        
        # Limites mínimos e máximos
        width = max(900, min(width, 1400))   # Mín: 900, Máx: 1400
        height = max(500, min(height, 800))  # Mín: 500, Máx: 800
        
        self.resize(width, height)        

    
    def carregar_filtros_iniciais(self):
        """Carrega os dados reais nos filtros de todas as abas"""
        try:
            regioes = self.google_sheets_service.get_regioes()
            
            if not regioes:
                QMessageBox.warning(self, "Aviso", 
                                  "Nenhuma região encontrada na planilha. "
                                  "Verifique se a planilha possui dados nas colunas G (Região), C (Convênio) e F (Produto).")
                return
            
            for tipo_proposta in ['Saque Fácil', 'Refin', 'Saque Direcionado']:
                if tipo_proposta in self.regiao_combos:
                    self.regiao_combos[tipo_proposta].clear()
                    self.regiao_combos[tipo_proposta].addItem("Selecione uma região", "")
                    for regiao in regioes:
                        self.regiao_combos[tipo_proposta].addItem(regiao, regiao)
                    
                    # Garantir que convênio e produto também tenham "Selecione"
                    self.convenio_combos[tipo_proposta].clear()
                    self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
                    self.convenio_combos[tipo_proposta].setEnabled(False)
                    
                    self.produto_combos[tipo_proposta].clear()
                    self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
                    self.produto_combos[tipo_proposta].setEnabled(False)
            
            print(f"Filtros carregados com {len(regioes)} regiões")
            
        except Exception as e:
            print(f"Erro ao carregar filtros: {e}")
            QMessageBox.warning(self, "Erro", 
                              f"Erro ao carregar dados da planilha: {str(e)}")
    

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
            pixmap = QPixmap(resource_path('assets/logo.png'))
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_nome_layout.addWidget(logo_label)
            logo_nome_layout.addSpacing(8)
        except Exception as e:
            print(f"Logo não encontrada: {e}")
        
        # Nome do sistema + versão
        nome_versao_layout = QVBoxLayout()
        nome_versao_layout.setSpacing(0)
        
        #nome_label = QLabel("AVERBSYS")
        #nome_label.setObjectName("sistemaNome")
        
        #versao_label = QLabel("v0.1")
        #versao_label.setObjectName("sistemaVersao")
        
        #nome_versao_layout.addWidget(nome_label)
        #nome_versao_layout.addWidget(versao_label)
        
        #logo_nome_layout.addLayout(nome_versao_layout)
        logo_nome_layout.addStretch()
        
        # Welcome label no centro
        welcome_label = QLabel(f"Analista: {self.user_data['nome_completo']} - {self.user_data['perfil']}")
        welcome_label.setObjectName("welcomeLabel")
        
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
        self.logout_button.clicked.connect(self.logout_request.emit)
        
        # Configurar visibilidade dos botões baseado no perfil
        self.configurar_botoes_por_perfil()
        
        # Adicionar botões ao layout
        botoes_layout.addWidget(self.cadastrar_button)
        botoes_layout.addWidget(self.manutencao_button)
        botoes_layout.addWidget(self.logout_button)
        
        # Adicionar tudo ao top_layout
        top_layout.addLayout(logo_nome_layout)
        top_layout.addStretch()
        top_layout.addWidget(welcome_label)
        top_layout.addStretch()
        top_layout.addLayout(botoes_layout)
        
        # LINHA INFERIOR: Apenas as abas (sem botões)
        # As abas serão adicionadas no layout principal depois
        
        # Adicionar top_layout ao header
        header_layout.addLayout(top_layout)
        header.setLayout(header_layout)
        return header

    
    def configurar_botoes_por_perfil(self):
        """Configura a visibilidade dos botões baseado no perfil do usuário"""
        perfil = self.user_data['perfil']
        
        # Cadastrar Usuário: apenas Dev
        self.cadastrar_button.setVisible(perfil == 'Dev')
        
        # Manutenção de Usuários: Dev, Gerente e Supervisor
        self.manutencao_button.setVisible(perfil in ['Dev', 'Gerente', 'Supervisor'])
    

    def cadastrar_usuario(self):
        """Abre a tela de cadastro de usuário"""
        self.abrir_cadastro_usuario.emit()
    
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
        numero_input.setValidator(QIntValidator(0, 999999999))
        numero_input.textChanged.connect(lambda text: self.validar_numero_proposta(text, tipo_proposta))
        
        self.numero_inputs[tipo_proposta] = numero_input
        
        limpar_button = QPushButton("Limpar")
        limpar_button.setObjectName("secondaryButton")
        limpar_button.clicked.connect(lambda: self.limpar_proposta(tipo_proposta))
        
        input_layout.addWidget(QLabel("Nº Proposta:"))
        input_layout.addWidget(numero_input)
        input_layout.addWidget(limpar_button)
        
        # FILTROS DO GOOGLE SHEETS
        filtros_layout = QGridLayout()
        filtros_layout.setHorizontalSpacing(15)
        filtros_layout.setVerticalSpacing(10)
        
        # Filtro Região
        filtros_layout.addWidget(QLabel("Região:"), 0, 0)
        regiao_combo = QComboBox()
        regiao_combo.setObjectName("comboField")
        regiao_combo.currentIndexChanged.connect(
            lambda: self.on_regiao_selecionada(tipo_proposta)
        )
        self.regiao_combos[tipo_proposta] = regiao_combo
        filtros_layout.addWidget(regiao_combo, 0, 1)
        
        # Filtro Convênio
        filtros_layout.addWidget(QLabel("Convênio:"), 1, 0)
        convenio_combo = QComboBox()
        convenio_combo.setObjectName("comboField")
        convenio_combo.setEnabled(False)
        convenio_combo.currentIndexChanged.connect(
            lambda: self.on_convenio_selecionado(tipo_proposta)
        )
        self.convenio_combos[tipo_proposta] = convenio_combo
        filtros_layout.addWidget(convenio_combo, 1, 1)
        
        # Filtro Produto
        filtros_layout.addWidget(QLabel("Produto:"), 2, 0)
        produto_combo = QComboBox()
        produto_combo.setObjectName("comboField")
        produto_combo.setEnabled(False)
        produto_combo.currentIndexChanged.connect(
            lambda: self.on_produto_selecionado(tipo_proposta)
        )
        self.produto_combos[tipo_proposta] = produto_combo
        filtros_layout.addWidget(produto_combo, 2, 1)
        
        # Status
        filtros_layout.addWidget(QLabel("Status:"), 3, 0)
        status_label = QLabel("Não selecionado")
        status_label.setObjectName("infoLabel")
        status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        self.status_labels[tipo_proposta] = status_label
        filtros_layout.addWidget(status_label, 3, 1)
        
        # Info data/hora criação
        data_info_label = QLabel("Data/Hora Criação: --/--/-- --:--:--")
        data_info_label.setObjectName("infoLabel")
        
        self.data_info_labels = getattr(self, 'data_info_labels', {})
        self.data_info_labels[tipo_proposta] = data_info_label
        
        layout.addWidget(title)
        layout.addLayout(input_layout)
        layout.addLayout(filtros_layout)
       # layout.addWidget(data_info_label)
        
        frame.setLayout(layout)
        return frame
    
    def on_regiao_selecionada(self, tipo_proposta):
        """Quando uma região é selecionada, carrega os convênios correspondentes"""
        regiao_combo = self.regiao_combos[tipo_proposta]
        convenio_combo = self.convenio_combos[tipo_proposta]
        produto_combo = self.produto_combos[tipo_proposta]
        status_label = self.status_labels[tipo_proposta]
        
        # Limpar dependências
        convenio_combo.clear()
        convenio_combo.addItem("Selecione um convênio", "")
        produto_combo.clear()
        produto_combo.addItem("Selecione um produto", "")
        status_label.setText("Não selecionado")
        status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        regiao_selecionada = regiao_combo.currentData()
        
        if regiao_selecionada:  # Se não for o item "Selecione"
            convenios = self.google_sheets_service.get_convenios_por_regiao(regiao_selecionada)
            
            for convenio in convenios:
                convenio_combo.addItem(convenio, convenio)
            
            convenio_combo.setEnabled(True)
            produto_combo.setEnabled(False)
        else:
            # Se selecionou "Selecione uma região", desabilitar os outros
            convenio_combo.setEnabled(False)
            produto_combo.setEnabled(False)
        
        # Validar estado dos botões após mudança
        self.validar_botoes_apos_mudanca_filtro(tipo_proposta)

    def on_convenio_selecionado(self, tipo_proposta):
        """Quando um convênio é selecionado, carrega os produtos correspondentes"""
        convenio_combo = self.convenio_combos[tipo_proposta]
        produto_combo = self.produto_combos[tipo_proposta]
        status_label = self.status_labels[tipo_proposta]
        
        # Limpar dependências
        produto_combo.clear()
        produto_combo.addItem("Selecione um produto", "")
        status_label.setText("Não selecionado")
        status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        convenio_selecionado = convenio_combo.currentData()
        
        if convenio_selecionado:  # Se não for o item "Selecione"
            produtos = self.google_sheets_service.get_produtos_por_convenio(convenio_selecionado)
            
            for produto in produtos:
                produto_combo.addItem(produto, produto)
            
            produto_combo.setEnabled(True)
        else:
            produto_combo.setEnabled(False)
        
        # Validar estado dos botões após mudança
        self.validar_botoes_apos_mudanca_filtro(tipo_proposta)

    def on_produto_selecionado(self, tipo_proposta):
        """Quando um produto é selecionado, mostra o status correspondente"""
        produto_combo = self.produto_combos[tipo_proposta]
        status_label = self.status_labels[tipo_proposta]
        
        produto_selecionado = produto_combo.currentData()
        
        if produto_selecionado:
            status = self.google_sheets_service.get_status_por_produto(produto_selecionado)
            
            # Aplicar estilo baseado no status
            if status and any(ativo in status.lower() for ativo in ['ativo', 'disponível', 'liberado']):
                status_label.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 3px;")
            elif status and any(inativo in status.lower() for inativo in ['inativo', 'indisponível', 'bloqueado']):
                status_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 3px;")
            else:
                status_label.setStyleSheet("color: #6c757d; font-weight: bold; padding: 5px; background-color: #e2e3e5; border: 1px solid #d6d8db; border-radius: 3px;")
            
            status_label.setText(status)
        else:
            status_label.setText("Não selecionado")
            status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        # Validar estado dos botões após mudança
        self.validar_botoes_apos_mudanca_filtro(tipo_proposta)

    def validar_botoes_apos_mudanca_filtro(self, tipo_proposta):
        """Valida o estado dos botões após mudança nos filtros"""
        if self.proposta_em_andamento and tipo_proposta == self.tipo_proposta_atual:
            todas_concluidas = self.verificar_todas_tarefas_concluidas(tipo_proposta)
            filtros_preenchidos = self.verificar_filtros_preenchidos(tipo_proposta)
            
            # Atualizar estado dos botões
            self.aprovar_buttons[tipo_proposta].setEnabled(todas_concluidas and filtros_preenchidos)
            self.recusar_buttons[tipo_proposta].setEnabled(filtros_preenchidos)
    
    def get_dados_filtro_atual(self, tipo_proposta):
        """Retorna os dados atualmente selecionados nos filtros"""
        return {
            'regiao': self.regiao_combos[tipo_proposta].currentData(),
            'convenio': self.convenio_combos[tipo_proposta].currentData(),
            'produto': self.produto_combos[tipo_proposta].currentData(),
            'status': self.status_labels[tipo_proposta].text()
        }

    def limpar_proposta(self, tipo_proposta):
        """Limpa completamente todos os campos para uma nova proposta"""
        # Parar timer de duração
        self.timer_duracao.stop()
        
        # 1. Limpar campo principal
        self.numero_inputs[tipo_proposta].setEnabled(True)
        self.numero_inputs[tipo_proposta].clear()
        
        # 2. Resetar filtros para estado INICIAL COM "SELECIONE"
        self.regiao_combos[tipo_proposta].setCurrentIndex(0)
        
        self.convenio_combos[tipo_proposta].clear()
        self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
        self.convenio_combos[tipo_proposta].setEnabled(False)
        
        self.produto_combos[tipo_proposta].clear()
        self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
        self.produto_combos[tipo_proposta].setEnabled(False)
        
        self.status_labels[tipo_proposta].setText("Não selecionado")
        self.status_labels[tipo_proposta].setStyleSheet("font-weight: bold; padding: 5px;")
        
        # 3. Resetar dados internos
        self.data_criacao = None
        self.data_conclusao = None
        self.proposta_em_andamento = False
        self.tarefas_concluidas = {}
        self.eh_reanalise = False
        self.proposta_original = None
        
        # 4. Atualizar interface
        self.data_info_labels[tipo_proposta].setText("Data/Hora Criação: --/--/-- --:--:--")
        
        # Checkboxes - desmarcar e desabilitar
        for checkbox in self.checkboxes_dict[tipo_proposta].values():
            checkbox.setEnabled(False)
            checkbox.setChecked(False)
        
        # Botões - desabilitar
        self.aprovar_buttons[tipo_proposta].setEnabled(False)
        self.recusar_buttons[tipo_proposta].setEnabled(False)
        
        # 5. Destravar abas
        self.destravar_todas_abas()
        
        print("✅ Proposta completamente limpa - pronta para nova análise")

    
    def criar_area_tarefas(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        title = QLabel("Tarefas da Proposta - Marque as concluídas (✓)")
        title.setObjectName("subtitleLabel")
        title.setStyleSheet("font-size: 12px;")
        
        info_label = QLabel("⚠️ Todas as tarefas devem ser marcadas")
        info_label.setObjectName("warningLabel")
        info_label.setStyleSheet("color: #ff9800; font-size: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # ALTURA RESPONSIVA baseada no tamanho da janela
        scroll.setMinimumHeight(100)
        scroll.setMaximumHeight(200)
        
        tarefas_widget = QWidget()
        tarefas_layout = QGridLayout()
        
        # Carregar tarefas específicas do tipo
        tarefas = get_tarefas_por_tipo(tipo_proposta)
        checkboxes = {}
        
        row, col = 0, 0
        for key, descricao in tarefas.items():
            checkbox = QCheckBox(descricao)
            checkbox.setObjectName("checkbox")
            checkbox.setEnabled(False)
            checkbox.stateChanged.connect(lambda state, k=key, tp=tipo_proposta: self.atualizar_tarefa(k, state, tp))
            checkboxes[key] = checkbox
            
            tarefas_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        self.checkboxes_dict[tipo_proposta] = checkboxes
        
        tarefas_widget.setLayout(tarefas_layout)
        scroll.setWidget(tarefas_widget)
        
        layout.addWidget(title)
        layout.addWidget(info_label)
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
        recusar_button.clicked.connect(lambda: self.recusar_proposta(tipo_proposta))
        recusar_button.setEnabled(False)
        
        self.aprovar_buttons = getattr(self, 'aprovar_buttons', {})
        self.recusar_buttons = getattr(self, 'recusar_buttons', {})
        self.aprovar_buttons[tipo_proposta] = aprovar_button
        self.recusar_buttons[tipo_proposta] = recusar_button
        
        layout.addWidget(aprovar_button)
        layout.addWidget(recusar_button)
        
        frame.setLayout(layout)
        return frame

    def resizeEvent(self, event):
        """Evento chamado quando a janela é redimensionada"""
        super().resizeEvent(event)
        
        # Ajustar elementos quando a janela mudar de tamanho
        if hasattr(self, 'tabs') and self.tabs.currentWidget():
            # Ajustar altura da área de tarefas baseado no novo tamanho
            current_tab_name = self.tabs.tabText(self.tabs.currentIndex())
            if current_tab_name in ["Saque Fácil", "Refin", "Saque Direcionado"]:
                self.ajustar_altura_tarefas(current_tab_name)

    def ajustar_altura_tarefas(self, tipo_proposta):
        """Ajusta a altura da área de tarefas baseado no tamanho da janela"""
        # Encontra o scroll area de tarefas
        tab_widget = self.tabs.currentWidget()
        for i in range(tab_widget.layout().count()):
            widget = tab_widget.layout().itemAt(i).widget()
            if isinstance(widget, QFrame) and hasattr(widget, 'layout'):
                for j in range(widget.layout().count()):
                    sub_widget = widget.layout().itemAt(j).widget()
                    if isinstance(sub_widget, QScrollArea):
                        # Define altura como 25% da altura da janela, com limites
                        altura = int(self.height() * 0.25)
                        altura = max(100, min(altura, 300))  # Mín: 100, Máx: 300
                        sub_widget.setFixedHeight(altura)
                        break
    
    def criar_aba_historico(self):
        aba = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)
        
        title = QLabel("Histórico de Propostas")
        title.setObjectName("titleLabel")
        
        # Frame de filtros
        filtros_frame = self.criar_filtros_historico()
        
        # TABELA com tamanho responsivo
        self.historico_table = QTableWidget()
        self.historico_table.setColumnCount(12)
        self.historico_table.setHorizontalHeaderLabels([
            "Tipo", "Número", "Analista", "Status", "Data Criação", "Data Conclusão", "Duração",
            "Região", "Convênio", "Produto", "Status Produto", "Motivo de Recusa"
        ])
        
        # Header responsivo
        header = self.historico_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # Permite ajuste
        header.setStretchLastSection(True)  # Estica a última seção
        self.historico_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 🔒 IMPEDIR EDIÇÃO DOS DADOS NA TABELA
        self.historico_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.historico_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.historico_table.setFocusPolicy(Qt.NoFocus)
        
        layout.addWidget(title)
        layout.addWidget(filtros_frame)
        layout.addWidget(self.historico_table)
        
        aba.setLayout(layout)
        return aba
    
    def criar_filtros_historico(self):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QHBoxLayout()
        
        # Período - Data Início
        periodo_layout = QHBoxLayout()
        periodo_layout.addWidget(QLabel("Período:"))
        
        self.data_inicio = QDateEdit()
        self.data_inicio.setDate(QDate.currentDate().addDays(-30))  # Últimos 30 dias
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setObjectName("dateField")
        
        self.data_fim = QDateEdit()
        self.data_fim.setDate(QDate.currentDate())
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setObjectName("dateField")
        
        periodo_layout.addWidget(QLabel("De:"))
        periodo_layout.addWidget(self.data_inicio)
        periodo_layout.addWidget(QLabel("Até:"))
        periodo_layout.addWidget(self.data_fim)
        
        # Filtro por Analista
        analista_layout = QHBoxLayout()
        analista_layout.addWidget(QLabel("Analista:"))
        
        self.combo_analista = QComboBox()
        self.combo_analista.setObjectName("comboField")
        
        # Se for analista, mostra apenas o próprio login
        if self.user_data['perfil'] == 'Analista':
            self.combo_analista.addItem(self.user_data['login'])
            self.combo_analista.setEnabled(False)  # Não permite alterar
        else:
            # Para outros perfis, carrega todos os analistas
            self.combo_analista.addItem("Todos", "todos")
            self.carregar_analistas()
        
        analista_layout.addWidget(self.combo_analista)
        
        # Botões
        botoes_layout = QHBoxLayout()
        
        filtrar_button = QPushButton("🔍 Filtrar")
        filtrar_button.setObjectName("primaryButton")
        filtrar_button.clicked.connect(self.aplicar_filtros)
        
        self.exportar_button = QPushButton("📊 Exportar")
        self.exportar_button.setObjectName("successButton")
        self.exportar_button.clicked.connect(self.exportar_para_xlsx)
        
        # Só mostra botão exportar se não for Analista
        if self.user_data['perfil'] == 'Analista':
            self.exportar_button.setVisible(False)
        
        botoes_layout.addWidget(filtrar_button)
        botoes_layout.addWidget(self.exportar_button)
        
        # Adicionar todos os layouts ao layout principal
        layout.addLayout(periodo_layout)
        layout.addSpacing(20)
        layout.addLayout(analista_layout)
        layout.addSpacing(20)
        layout.addLayout(botoes_layout)
        
        frame.setLayout(layout)
        return frame
    
    def carregar_analistas(self):
        """Carrega a lista de analistas disponíveis (apenas para perfis não Analista)"""
        try:
            # Buscar todos os analistas únicos do banco de dados
            propostas = self.proposta_service.listar_todas_propostas()
            analistas = set()
            
            for proposta in propostas:
                if 'analista' in proposta:
                    analistas.add(proposta['analista'])
            
            # Ordenar e adicionar ao combobox
            analistas_ordenados = sorted(list(analistas))
            for analista in analistas_ordenados:
                self.combo_analista.addItem(analista, analista)
                
        except Exception as e:
            print(f"Erro ao carregar analistas: {e}")


    def aplicar_filtros(self):
        """Aplica os filtros selecionados na tabela de histórico"""
        try:
            # Obter datas do período - já são objetos QDate
            data_inicio_qdate = self.data_inicio.date()
            data_fim_qdate = self.data_fim.date()
            
            # Converter QDate para Python date
            data_inicio = data_inicio_qdate.toPyDate()
            data_fim = data_fim_qdate.toPyDate()
            
            # Obter analista selecionado
            analista_selecionado = None
            if self.user_data['perfil'] == 'Analista':
                analista_selecionado = self.user_data['login']
            else:
                analista_data = self.combo_analista.currentData()
                if analista_data != "todos":
                    analista_selecionado = analista_data
            
            # Buscar propostas com filtros usando o método mais simples
            propostas = self.proposta_service.listar_propostas_simples_filtro(
                data_inicio=data_inicio,
                data_fim=data_fim,
                analista=analista_selecionado
            )
            
            self.preencher_tabela_historico(propostas)
            
            # Mostrar quantidades de resultados
            QMessageBox.information(self, "Filtro Aplicado", f"Encontradas {len(propostas)} propostas no período selecionado.")
            
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao aplicar filtros: {str(e)}")

    def exportar_para_xlsx(self):
        """Exporta os dados da tabela para XLSX"""
        try:
            if self.historico_table.rowCount() == 0:
                QMessageBox.warning(self, "Aviso", "Não há dados para exportar!")
                return
            
            # Solicitar local para salvar o arquivo
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Salvar Arquivo Excel", 
                f"propostas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", 
                "Excel Files (*.xlsx)"
            )
            
            if not file_path:
                return
            
            # Importar pandas para criar o Excel
            import pandas as pd
            
            # Preparar dados para exportação
            headers = []
            for col in range(self.historico_table.columnCount()):
                headers.append(self.historico_table.horizontalHeaderItem(col).text())
            
            data = []
            for row in range(self.historico_table.rowCount()):
                row_data = []
                for col in range(self.historico_table.columnCount()):
                    item = self.historico_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            # Criar DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # Salvar como Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Propostas', index=False)
                
                # Ajustar largura das colunas automaticamente
                worksheet = writer.sheets['Propostas']
                for idx, col in enumerate(df.columns):
                    max_length = max(df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
            
            QMessageBox.information(self, "Sucesso", f"Dados exportados com sucesso!\n{file_path}")
            
        except ImportError:
            QMessageBox.warning(self, "Erro", 
                            "Biblioteca pandas ou openpyxl não encontrada. "
                            "Instale com: pip install pandas openpyxl")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao exportar XLSX: {str(e)}")




    def aba_mudou(self, index):
        """Quando muda de aba, reseta o estado"""
        # Só permite mudar de aba se não houver proposta em andamento
        if self.proposta_em_andamento:
            # Volta para a aba anterior
            current_index = self.tabs.currentIndex()
            if current_index != index:
                self.tabs.setCurrentIndex(current_index)
                QMessageBox.warning(self, "Atenção", "Finalize a proposta atual antes de mudar de aba!")
        else:
            self.tipo_proposta_atual = None
            self.data_criacao = None
            self.tarefas_concluidas = {}
    
    def validar_numero_proposta(self, texto, tipo_proposta):
        if texto.isdigit() and len(texto) == 9:
            # Verificar se a proposta já existe
            proposta_existente = self.proposta_service.verificar_proposta_existente(texto)
            
            if proposta_existente:
                # Formatar datas para exibição
                data_criacao = proposta_existente.get('data_criacao')
                data_conclusao = proposta_existente.get('data_conclusao')
                
                if hasattr(data_criacao, 'strftime'):
                    data_criacao_str = data_criacao.strftime('%d/%m/%Y %H:%M:%S')
                else:
                    data_criacao_str = str(data_criacao)
                    
                if data_conclusao and hasattr(data_conclusao, 'strftime'):
                    data_conclusao_str = data_conclusao.strftime('%d/%m/%Y %H:%M:%S')
                else:
                    data_conclusao_str = " - "
                
                # Montar informações detalhadas da proposta anterior
                info_anterior = f"""
    <b>Proposta {texto} já analisada anteriormente.</b>

    <b>Informações da análise anterior:</b>
    • Tipo: {proposta_existente.get('tipo_proposta', 'N/A')}
    • Analista: {proposta_existente.get('analista', 'N/A')}
    • Status: <b>{proposta_existente.get('status', 'N/A')}</b>
    • Data de Criação: {data_criacao_str}
    • Data de Conclusão: {data_conclusao_str}
    • Duração: {proposta_existente.get('duracao_total', ' - ')}

    <b>Deseja fazer reanálise desta proposta?</b>
                """
                
                # Criar message box personalizada
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Proposta Existente")
                msg_box.setTextFormat(Qt.RichText)
                msg_box.setText(info_anterior)
                msg_box.setIcon(QMessageBox.Question)
                
                # Botões personalizados
                btn_reanalise = msg_box.addButton("Sim, Fazer Reanálise", QMessageBox.YesRole)
                btn_nova = msg_box.addButton("Não, Digitar Outra", QMessageBox.NoRole)
                btn_cancelar = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
                
                msg_box.setDefaultButton(btn_reanalise)
                
                # Executar e verificar resposta
                resposta = msg_box.exec_()
                
                if msg_box.clickedButton() == btn_reanalise:
                    # Usuário quer reanálise
                    self.eh_reanalise = True
                    self.proposta_original = proposta_existente
                    self.configurar_proposta_em_andamento(tipo_proposta)
                    QMessageBox.information(self, "Reanálise", "Modo de reanálise ativado. A proposta será salva com ' - Reanalise' no tipo.")
                    
                elif msg_box.clickedButton() == btn_nova:
                    # Usuário quer digitar outra proposta, limpar campo
                    self.numero_inputs[tipo_proposta].clear()
                    self.eh_reanalise = False
                    self.proposta_original = None
                    return
                else:
                    # Cancelar, limpar campo e sair
                    self.numero_inputs[tipo_proposta].clear()
                    self.eh_reanalise = False
                    self.proposta_original = None
                    return
            else:
                # Proposta nova
                self.eh_reanalise = False
                self.proposta_original = None
                self.configurar_proposta_em_andamento(tipo_proposta)
                
        else:
            # Manter tudo desabilitado se não for válido
            self.numero_inputs[tipo_proposta].setEnabled(True)
            for checkbox in self.checkboxes_dict[tipo_proposta].values():
                checkbox.setEnabled(False)
            self.aprovar_buttons[tipo_proposta].setEnabled(False)
            self.recusar_buttons[tipo_proposta].setEnabled(False)

    def configurar_proposta_em_andamento(self, tipo_proposta):
        """Configura o estado quando uma proposta está em andamento"""
        # TRAVAR o campo de entrada
        self.numero_inputs[tipo_proposta].setEnabled(False)
        
        # HABILITAR os filtros
        self.regiao_combos[tipo_proposta].setEnabled(True)
        
        # Registrar data/hora de criação
        if not self.data_criacao:
            self.data_criacao = datetime.now()
            self.tipo_proposta_atual = tipo_proposta
            self.proposta_em_andamento = True
            
            # Iniciar timer para atualizar duração
            self.timer_duracao.start(1000)
            
            self.data_info_labels[tipo_proposta].setText(
                f"Data/Hora Criação: {self.data_criacao.strftime('%d/%m/%Y %H:%M:%S')}"
            )
        
        # HABILITAR os checkboxes
        for checkbox in self.checkboxes_dict[tipo_proposta].values():
            checkbox.setEnabled(True)
        
        # VALIDAR ESTADO INICIAL DOS BOTÕES (provavelmente desabilitados)
        self.validar_botoes_apos_mudanca_filtro(tipo_proposta)
        
        # Se for reanálise, atualizar o título para indicar
        if self.eh_reanalise:
            titulo_original = f"{tipo_proposta} - Nova Proposta"
            # Encontrar e atualizar o título na aba atual
            for i in range(self.tabs.currentWidget().layout().count()):
                widget = self.tabs.currentWidget().layout().itemAt(i).widget()
                if isinstance(widget, QFrame) and hasattr(widget, 'layout'):
                    for j in range(widget.layout().count()):
                        sub_widget = widget.layout().itemAt(j).widget()
                        if isinstance(sub_widget, QLabel) and sub_widget.text() == titulo_original:
                            sub_widget.setText(f"{tipo_proposta} - Reanálise")
                            sub_widget.setStyleSheet("color: #ff9800; font-weight: bold;")
        
        # Travando as outras abas
        self.travar_outras_abas(tipo_proposta)

    def verificar_filtros_preenchidos(self, tipo_proposta):
        """Verifica se todos os filtros obrigatórios estão preenchidos"""
        dados_filtro = self.get_dados_filtro_atual(tipo_proposta)
        
        # Verificar se todos os campos obrigatórios estão preenchidos
        regiao_preenchida = bool(dados_filtro['regiao'])
        convenio_preenchido = bool(dados_filtro['convenio'])
        produto_preenchido = bool(dados_filtro['produto'])
        
        todos_preenchidos = regiao_preenchida and convenio_preenchido and produto_preenchido
        
        if not todos_preenchidos:
            print("❌ Filtros obrigatórios não preenchidos:")
            print(f"   - Região: {'✅' if regiao_preenchida else '❌'} {dados_filtro['regiao'] or 'Não selecionada'}")
            print(f"   - Convênio: {'✅' if convenio_preenchido else '❌'} {dados_filtro['convenio'] or 'Não selecionado'}")
            print(f"   - Produto: {'✅' if produto_preenchido else '❌'} {dados_filtro['produto'] or 'Não selecionado'}")
        
        return todos_preenchidos   
    
    def atualizar_tarefa(self, tarefa_key, estado, tipo_proposta):
        self.tarefas_concluidas[tarefa_key] = (estado == Qt.Checked)
        
        # Verificar se TODOS os checkboxes estão marcados E filtros preenchidos
        if self.proposta_em_andamento and tipo_proposta == self.tipo_proposta_atual:
            todas_concluidas = self.verificar_todas_tarefas_concluidas(tipo_proposta)
            filtros_preenchidos = self.verificar_filtros_preenchidos(tipo_proposta)
            
            # Habilita aprovar apenas se TUDO estiver preenchido
            self.aprovar_buttons[tipo_proposta].setEnabled(todas_concluidas and filtros_preenchidos)
            
            # Habilita recusar apenas se os filtros estiverem preenchidos
            self.recusar_buttons[tipo_proposta].setEnabled(filtros_preenchidos)
            
            # Debug
            if todas_concluidas and not filtros_preenchidos:
                print("⚠️  Tarefas concluídas, mas filtros não preenchidos - Aprovar desabilitado")
            elif filtros_preenchidos and not todas_concluidas:
                print("⚠️  Filtros preenchidos, mas tarefas não concluídas - Aprovar desabilitado")
            elif todas_concluidas and filtros_preenchidos:
                print("✅ Tarefas concluídas e filtros preenchidos - Aprovar habilitado")
    
    def verificar_todas_tarefas_concluidas(self, tipo_proposta):
        """Verifica se todas as tarefas da aba foram concluídas"""
        checkboxes = self.checkboxes_dict.get(tipo_proposta, {})
        return all(checkbox.isChecked() for checkbox in checkboxes.values())
    
    #def atualizar_duracao_display(self):
    #    """Atualiza o display da duração em tempo real"""
    #    if self.proposta_em_andamento and self.data_criacao and self.tipo_proposta_atual:
    #        duracao = datetime.now() - self.data_criacao
    #        horas = duracao.seconds // 3600
    #        minutos = (duracao.seconds % 3600) // 60
    #        segundos = duracao.seconds % 60        
    #        duracao_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    #        self.duracao_labels[self.tipo_proposta_atual].setText(f"Duração: {duracao_str}")

    def atualizar_duracao_display(self):
        """Atualiza o display da duração em tempo real - MANTIDO MAS VAZIO PARA OCULTAR NA INTERFACE"""
        # Este método é mantido para evitar erros, mas não faz nada
        # A duração continua sendo calculada e salva no banco, apenas não é exibida
        pass
    
    def calcular_duracao_total(self):
        """Calcula a duração total quando a proposta é finalizada"""
        if self.data_criacao and self.data_conclusao:
            duracao = self.data_conclusao - self.data_criacao
            horas = duracao.seconds // 3600
            minutos = (duracao.seconds % 3600) // 60
            segundos = duracao.seconds % 60
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        return "00:00:00"
    

    def limpar_proposta(self, tipo_proposta):
        """Limpa completamente todos os campos para uma nova proposta"""
        # Parar timer de duração
        self.timer_duracao.stop()
        
        # 1. Limpar campo principal
        self.numero_inputs[tipo_proposta].setEnabled(True)
        self.numero_inputs[tipo_proposta].clear()
        
        # 2. Resetar filtros para estado INICIAL COM "SELECIONE"
        # Região - voltar para "Selecione uma região" (índice 0)
        self.regiao_combos[tipo_proposta].setCurrentIndex(0)
        
        # Convênio - limpar, adicionar "Selecione" e desabilitar
        self.convenio_combos[tipo_proposta].clear()
        self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
        self.convenio_combos[tipo_proposta].setEnabled(False)
        
        # Produto - limpar, adicionar "Selecione" e desabilitar
        self.produto_combos[tipo_proposta].clear()
        self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
        self.produto_combos[tipo_proposta].setEnabled(False)
        
        # Status - resetar para "Não selecionado"
        self.status_labels[tipo_proposta].setText("Não selecionado")
        self.status_labels[tipo_proposta].setStyleSheet("font-weight: bold; padding: 5px;")
        
        # 3. Resetar dados internos
        self.data_criacao = None
        self.data_conclusao = None
        self.proposta_em_andamento = False
        self.tarefas_concluidas = {}
        self.eh_reanalise = False
        self.proposta_original = None
        
        # 4. Atualizar interface
        self.data_info_labels[tipo_proposta].setText("Data/Hora Criação: --/--/-- --:--:--")
        
        # Checkboxes - desmarcar e desabilitar
        for checkbox in self.checkboxes_dict[tipo_proposta].values():
            checkbox.setEnabled(False)
            checkbox.setChecked(False)
        
        # Botões - desabilitar
        self.aprovar_buttons[tipo_proposta].setEnabled(False)
        self.recusar_buttons[tipo_proposta].setEnabled(False)
        
        # 5. Destravar abas
        self.destravar_todas_abas()
        
        print("✅ Proposta completamente limpa - pronta para nova análise")
        print(f"   - Região: {self.regiao_combos[tipo_proposta].currentText()}")
        print(f"   - Convênio: {self.convenio_combos[tipo_proposta].currentText()}")
        print(f"   - Produto: {self.produto_combos[tipo_proposta].currentText()}")
        print(f"   - Status: {self.status_labels[tipo_proposta].text()}")


    def recusar_proposta(self, tipo_proposta):
        """Abre popup para selecionar motivo da recusa"""
        dialog = MotivoRecusaDialog(self)
        dialog.motivo_selecionado.connect(lambda motivo_id, descricao: self.on_motivo_recusa_selecionado(tipo_proposta, motivo_id, descricao))
        dialog.exec_()

    def on_motivo_recusa_selecionado(self, tipo_proposta, motivo_id, descricao):
        """Callback quando um motivo de recusa é selecionado"""
        print(f"Motivo selecionado: {motivo_id} - {descricao}")
        
        # Confirmar recusa com o motivo
        resposta = QMessageBox.question(
            self, 
            "Confirmar Recusa",
            f"Tem certeza que deseja recusar a proposta?\n\n"
            f"Motivo: {motivo_id} - {descricao}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            # Finalizar proposta com status "Recusada" e motivo
            self.finalizar_proposta_com_motivo(tipo_proposta, "Recusada", motivo_id, descricao)


    def finalizar_proposta_com_motivo(self, tipo_proposta, status, motivo_id, motivo_descricao):
        """Finaliza a proposta com motivo específico"""
        # VALIDAÇÃO OBRIGATÓRIA DOS FILTROS
        if not self.verificar_filtros_preenchidos(tipo_proposta):
            QMessageBox.warning(self, "Campos Obrigatórios", 
                            "Preencha todos os filtros obrigatórios:\n"
                            "• Região\n• Convênio\n• Produto\n\n"
                            "Antes de finalizar a proposta.")
            return
        
        numero = self.numero_inputs[tipo_proposta].text().strip()
        
        if not numero or len(numero) != 9:
            QMessageBox.warning(self, "Erro", "Número da proposta inválido!")
            return
        
        # Registrar data de conclusão
        self.data_conclusao = datetime.now()
        
        # Parar timer de duração
        self.timer_duracao.stop()
        
        # Calcular duração total
        duracao_total = self.calcular_duracao_total()
        
        # Se for reanálise, adicionar " - Reanalise" ao tipo
        tipo_final = tipo_proposta
        if self.eh_reanalise:
            tipo_final = f"{tipo_proposta} - Reanalise"
        
        # Obter dados dos filtros
        dados_filtro = self.get_dados_filtro_atual(tipo_proposta)
        
        # Adicionar motivo da recusa aos dados
        dados_filtro['motivo_recusa_id'] = motivo_id
        dados_filtro['motivo_recusa_descricao'] = motivo_descricao
        
        # Criar e finalizar proposta incluindo dados dos filtros e motivo
        self.proposta_service.criar_e_finalizar_proposta(
            numero, 
            self.user_data['login'], 
            tipo_final,
            self.tarefas_concluidas,
            status,
            self.data_criacao,
            self.data_conclusao,
            duracao_total,
            dados_filtro
        )        
        
    def finalizar_proposta(self, tipo_proposta, status):
        """Finaliza proposta (para aprovação)"""
        if status == "Recusada":
            # Para recusa, usar o método com popup de motivos
            self.recusar_proposta(tipo_proposta)
        else:
            # Para aprovação, usar o fluxo normal
            self.finalizar_proposta_sem_motivo(tipo_proposta, status)

    def finalizar_proposta_sem_motivo(self, tipo_proposta, status):
        """Finaliza proposta sem motivo (para aprovação)"""
        # VALIDAÇÃO OBRIGATÓRIA DOS FILTROS
        if not self.verificar_filtros_preenchidos(tipo_proposta):
            QMessageBox.warning(self, "Campos Obrigatórios", 
                            "Preencha todos os filtros obrigatórios:\n"
                            "• Região\n• Convênio\n• Produto\n\n"
                            "Antes de finalizar a proposta.")
            return
        
        numero = self.numero_inputs[tipo_proposta].text().strip()
        
        if not numero or len(numero) != 9:
            QMessageBox.warning(self, "Erro", "Número da proposta inválido!")
            return
        
        # Para aprovação, verificar se TODAS as tarefas foram concluídas
        if status == "Aprovada" and not self.verificar_todas_tarefas_concluidas(tipo_proposta):
            QMessageBox.warning(self, "Atenção", "Todas as tarefas devem ser concluídas para aprovar a proposta!")
            return
        
        # Registrar data de conclusão
        self.data_conclusao = datetime.now()
        
        # Parar timer de duração
        self.timer_duracao.stop()
        
        # Calcular duração total
        duracao_total = self.calcular_duracao_total()
        
        # Se for reanálise, adicionar " - Reanalise" ao tipo
        tipo_final = tipo_proposta
        if self.eh_reanalise:
            tipo_final = f"{tipo_proposta} - Reanalise"
        
        # Obter dados dos filtros
        dados_filtro = self.get_dados_filtro_atual(tipo_proposta)
        
        # Criar e finalizar proposta
        self.proposta_service.criar_e_finalizar_proposta(
            numero, 
            self.user_data['login'], 
            tipo_final,
            self.tarefas_concluidas,
            status,
            self.data_criacao,
            self.data_conclusao,
            duracao_total,
            dados_filtro
        )


    
    def travar_outras_abas(self, aba_atual):
        """Trava todas as abas exceto a atual quando uma proposta está em andamento"""
        for i in range(self.tabs.count()):
            if i != self.tabs.indexOf(self.tabs.currentWidget()):
                self.tabs.setTabEnabled(i, False)
    
    def destravar_todas_abas(self):
        """Destrava todas as abas quando não há proposta em andamento"""
        for i in range(self.tabs.count()):
            self.tabs.setTabEnabled(i, True)
    
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
        """Carrega o histórico inicial baseado no perfil do usuário"""
        try:
            if self.user_data['perfil'] == 'Analista':
                # Para analistas, carrega apenas suas próprias propostas
                propostas = self.proposta_service.listar_propostas_por_analista(self.user_data['login'])
            else:
                # Para outros perfis, carrega todas as propostas dos últimos 30 dias
                data_inicio = datetime.now() - timedelta(days=30)
                propostas = self.proposta_service.listar_propostas_com_filtros(
                    data_inicio=data_inicio,
                    data_fim=datetime.now()
                )
            
            self.preencher_tabela_historico(propostas)
            
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    def preencher_tabela_historico(self, propostas):
        """Preenche a tabela de histórico com as propostas incluindo tipo de recusa"""
        self.historico_table.setRowCount(len(propostas))
        
        for row, proposta in enumerate(propostas):
            # CAMPOS ORIGINAIS
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
            
            # Exibir duração
            duracao = proposta.get('duracao_total', ' - ')
            self.historico_table.setItem(row, 6, QTableWidgetItem(duracao))
            
            # CAMPOS DOS FILTROS
            dados_filtro = proposta.get('dados_filtro', {})
            
            regiao = dados_filtro.get('regiao', 'N/A')
            convenio = dados_filtro.get('convenio', 'N/A')
            produto = dados_filtro.get('produto', 'N/A')
            status_produto = dados_filtro.get('status', 'N/A')
            
            self.historico_table.setItem(row, 7, QTableWidgetItem(regiao))
            self.historico_table.setItem(row, 8, QTableWidgetItem(convenio))
            self.historico_table.setItem(row, 9, QTableWidgetItem(produto))
            
            # Status do produto com formatação
            status_produto_item = QTableWidgetItem(status_produto)
            if 'ativo' in status_produto.lower():
                status_produto_item.setBackground(Qt.green)
            elif 'inativo' in status_produto.lower():
                status_produto_item.setBackground(Qt.red)
            self.historico_table.setItem(row, 10, status_produto_item)
            
            # TIPO DE RECUSA (nova coluna)
            tipo_recusa = dados_filtro.get('tipo_recusa', '')
            tipo_recusa_item = QTableWidgetItem(tipo_recusa)
            if proposta['status'] == 'Recusada' and tipo_recusa:
                tipo_recusa_item.setBackground(Qt.red)
            self.historico_table.setItem(row, 11, tipo_recusa_item)