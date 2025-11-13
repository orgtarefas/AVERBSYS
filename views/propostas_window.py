from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QTabWidget, QProgressBar, QComboBox, QCheckBox,
                             QGroupBox, QGridLayout, QScrollArea, QDateEdit,
                             QFormLayout, QFileDialog, QDialog, QListWidget,
                             QListWidgetItem, QDialogButtonBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QIntValidator, QPixmap, QIcon
import os
import sys
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



class MotivoRecusaDialog(QDialog):
    motivo_selecionado = pyqtSignal(str, str)  # id, descricao
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Motivo da Recusa")
        self.setModal(True)
        self.resize(400, 500)
        self.init_ui()
        
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
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        
        # LINHA 2: Tabs principais
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.aba_mudou)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #C2C7CB;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E1E1E1;
                border: 1px solid #C4C4C3;
                padding: 6px 12px;
                margin-right: 2px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-bottom-color: #FFFFFF;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # Criar as abas específicas
        self.tab_saque_facil = self.criar_aba_proposta("Saque Fácil")
        self.tab_refin = self.criar_aba_proposta("Refin") 
        self.tab_saque_direcionado = self.criar_aba_proposta("Saque Direcionado")
        self.tab_solicitacao_interna = self.criar_aba_proposta("Solicitação Interna")
        
        # Tab de Histórico
        self.tab_historico = self.criar_aba_historico()
        
        # Adicionar tabs
        self.tabs.addTab(self.tab_saque_facil, "Saque Fácil")
        self.tabs.addTab(self.tab_refin, "Refin")
        self.tabs.addTab(self.tab_saque_direcionado, "Saque Direcionado")
        self.tabs.addTab(self.tab_solicitacao_interna, "Solicitação Interna")
        self.tabs.addTab(self.tab_historico, "Histórico")
        
        # Conectar sinais
        self.proposta_service.proposta_criada.connect(self.on_proposta_criada)
        
        # Adicionar ao layout principal
        layout.addWidget(self.tabs)  # ⭐⭐ AGORA SÓ AS TABS
        
        self.setLayout(layout)

        # ⭐⭐ TAMANHO RESPONSIVO OTIMIZADO PARA 1366x768
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
        """Ajusta o tamanho da janela baseado no tamanho da tela - OTIMIZADO PARA 1366x768"""
        screen = self.screen().availableGeometry()
        
        # ⭐⭐ OTIMIZADO PARA 1366x768 - ALTURA REDUZIDA
        if screen.width() <= 1366:
            # Modo compacto para telas pequenas
            width = int(screen.width() * 0.95)  # 95% da largura
            height = int(screen.height() * 0.85)  # ⭐⭐ REDUZIDO de 0.9 para 0.85
            
            # Limites específicos para 1366x768
            width = min(width, 1300)
            height = min(height, 650)  # ⭐⭐ REDUZIDO de 700 para 650
            
            # Mínimos para usabilidade
            width = max(width, 1000)
            height = max(height, 550)  # ⭐⭐ REDUZIDO de 600 para 550
        else:
            # Modo normal para telas maiores
            width = int(screen.width() * 0.85)
            height = int(screen.height() * 0.75)  # ⭐⭐ REDUZIDO de 0.8 para 0.75
            
            width = max(1000, min(width, 1400))
            height = max(550, min(height, 700))  # ⭐⭐ REDUZIDO de 600/800 para 550/700
        
        print(f"🖥️  Tela: {screen.width()}x{screen.height()}")
        print(f"📐 Ajustando janela para: {width}x{height}")
        
        self.resize(width, height)

    
    def carregar_filtros_iniciais(self):
        """Carrega os dados reais nos filtros de todas as abas"""
        try:
            if self.google_sheets_service is None:
                print("⚠️ Google Sheets Service não disponível - usando dados mock")
                regioes = ["Região 1", "Região 2", "Região 3"]  # Dados mock
            else:
                regioes = self.google_sheets_service.get_regioes()
            
            print(f"📍 Regiões carregadas: {regioes}")
            
            if not regioes:
                QMessageBox.warning(self, "Aviso", 
                                "Nenhuma região encontrada na planilha. "
                                "Verifique se a planilha possui dados nas colunas G (Região), C (Convênio) e F (Produto).")
                return
            
            for tipo_proposta in ['Saque Fácil', 'Refin', 'Saque Direcionado', 'Solicitação Interna']:
                print(f"🔄 Carregando filtros para: {tipo_proposta}")
                
                if tipo_proposta in self.regiao_combos:
                    self.regiao_combos[tipo_proposta].clear()
                    self.regiao_combos[tipo_proposta].addItem("Selecione uma região", "")
                    for regiao in regioes:
                        self.regiao_combos[tipo_proposta].addItem(regiao, regiao)
                    
                    # ⭐⭐ INICIAR COM REGIÃO DESABILITADA ⭐⭐
                    self.regiao_combos[tipo_proposta].setEnabled(False)
                    print(f"   ✅ Regiões carregadas: {self.regiao_combos[tipo_proposta].count()} itens (Desabilitada)")
                    
                    # Garantir que convênio e produto também tenham "Selecione" e desabilitados
                    self.convenio_combos[tipo_proposta].clear()
                    self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
                    self.convenio_combos[tipo_proposta].setEnabled(False)
                    
                    self.produto_combos[tipo_proposta].clear()
                    self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
                    self.produto_combos[tipo_proposta].setEnabled(False)
            
            print(f"✅ Filtros carregados com {len(regioes)} regiões (todos desabilitados inicialmente)")
            
        except Exception as e:
            print(f"❌ Erro ao carregar filtros: {e}")
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
       # self.logout_button.clicked.connect(self.logout_request.emit)
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
        
        # Manutenção de Usuários: Dev, Gerente e Supervisor
        self.manutencao_button.setVisible(perfil in ['Dev', 'Gerente', 'Supervisor'])
    

    def cadastrar_usuario(self):
        """Abre a tela de cadastro de usuário"""
        self.abrir_cadastro_usuario.emit()
    

    def criar_aba_proposta(self, tipo_proposta):
        aba = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  
        layout.setSpacing(3)  # ⭐⭐ REDUZIDO ESPAÇAMENTO GERAL (5 -> 3)
        
        # Área de entrada da proposta
        input_frame = self.criar_area_input(tipo_proposta)
        
        # Área de tarefas
        tarefas_frame = self.criar_area_tarefas(tipo_proposta)
        
        # Área de ações
        acoes_frame = self.criar_area_acoes(tipo_proposta)
        
        layout.addWidget(input_frame)
        layout.addWidget(tarefas_frame)
        layout.addWidget(acoes_frame)
        layout.addStretch(1)
        
        aba.setLayout(layout)
        return aba
        

    def criar_area_input(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)  # ⭐⭐ REDUZIDO verticalmente (8,8,8,8 -> 8,6,8,6)
        layout.setSpacing(4)  # ⭐⭐ REDUZIDO (5 -> 4)
        
        # Layout horizontal para número, botão limpar, analista E botões do sistema
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)
        
        # CONFIGURAÇÃO POR TIPO DE PROPOSTA
        if tipo_proposta == "Solicitação Interna":
            placeholder = "Digite o contrato (00-1234567890 ou A00-1234567890)"
            max_length = 14
            texto_inicial = ""
            label_text = "Nº Contrato:"
        else:
            placeholder = "Digite o número do contrato (ex: 50-1234567890)"
            max_length = 13
            texto_inicial = ""
            label_text = "Nº Contrato:"
        
        numero_input = QLineEdit()
        numero_input.setPlaceholderText(placeholder)
        numero_input.setObjectName("inputField")
        numero_input.setMaxLength(max_length)
        numero_input.setText(texto_inicial)
        
        numero_input.textChanged.connect(lambda text: self.validar_formato_contrato(text, tipo_proposta))
        
        self.numero_inputs[tipo_proposta] = numero_input
        
        limpar_button = QPushButton("Limpar")
        limpar_button.setObjectName("secondaryButton")
        limpar_button.clicked.connect(lambda: self.limpar_proposta(tipo_proposta))
        
        # ⭐⭐ ADICIONAR NOME DO ANALISTA
        input_layout.addWidget(QLabel(label_text))
        input_layout.addWidget(numero_input)
        input_layout.addWidget(limpar_button)
        input_layout.addStretch()  # ⭐⭐ PRIMEIRO STRETCH - empurra o analista para a direita
        
        analista_label = QLabel(f"{self.user_data['nome_completo']} - {self.user_data['perfil']}")
        analista_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 11px;
                padding: 4px 12px;
                background-color: #ecf0f1;
                border-radius: 3px;
                margin-left: 20px;
            }
        """)
        analista_label.setFixedHeight(28)
        analista_label.setAlignment(Qt.AlignCenter)
        
        input_layout.addWidget(analista_label)
        
        # ⭐⭐ BOTÕES DO SISTEMA (Cadastrar, Manutenção, Sair) - APENAS NA PRIMEIRA ABA
        if tipo_proposta == "Saque Fácil":  # Apenas na primeira aba para evitar duplicação
            # Botão Cadastrar Usuário (apenas para Dev)
            self.cadastrar_button = QPushButton("Cadastrar")
            self.cadastrar_button.setObjectName("primaryButton")
            self.cadastrar_button.clicked.connect(self.cadastrar_usuario)
            self.cadastrar_button.setFixedWidth(120)
            self.cadastrar_button.setFixedHeight(28)
            
            # Botão Manutenção de Usuários (apenas para Gerente e Dev)
            self.manutencao_button = QPushButton("Manutenção")
            self.manutencao_button.setObjectName("primaryButton")
            self.manutencao_button.clicked.connect(self.abrir_manutencao_usuarios.emit)
            self.manutencao_button.setFixedWidth(120)
            self.manutencao_button.setFixedHeight(28)
            
            # Botão Sair
            self.logout_button = QPushButton("Sair")
            self.logout_button.setObjectName("logoutButton")
            self.logout_button.clicked.connect(self.logout_request.emit)
            self.logout_button.setFixedWidth(70)
            self.logout_button.setFixedHeight(28)
            
            # Configurar visibilidade dos botões baseado no perfil
            self.configurar_botoes_por_perfil()
            
            # Adicionar botões ao layout
            input_layout.addWidget(self.cadastrar_button)
            input_layout.addWidget(self.manutencao_button)
            input_layout.addWidget(self.logout_button)
        
        # LINHA 1: Filtros Google Sheets (Região, Convênio, Produto, Status)
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(8)
        
        # Região
        regiao_layout = QVBoxLayout()
        regiao_layout.setSpacing(2)
        regiao_layout.addWidget(QLabel("Região:"))
        regiao_combo = QComboBox()
        regiao_combo.setObjectName("comboField")
        regiao_combo.currentIndexChanged.connect(
            lambda: self.on_regiao_selecionada(tipo_proposta)
        )
        self.regiao_combos[tipo_proposta] = regiao_combo
        regiao_layout.addWidget(regiao_combo)
        linha1_layout.addLayout(regiao_layout)
        
        # Convênio
        convenio_layout = QVBoxLayout()
        convenio_layout.setSpacing(2)
        convenio_layout.addWidget(QLabel("Convênio:"))
        convenio_combo = QComboBox()
        convenio_combo.setObjectName("comboField")
        convenio_combo.setEnabled(False)
        convenio_combo.currentIndexChanged.connect(
            lambda: self.on_convenio_selecionado(tipo_proposta)
        )
        self.convenio_combos[tipo_proposta] = convenio_combo
        convenio_layout.addWidget(convenio_combo)
        linha1_layout.addLayout(convenio_layout)
        
        # Produto
        produto_layout = QVBoxLayout()
        produto_layout.setSpacing(2)
        produto_layout.addWidget(QLabel("Produto:"))
        produto_combo = QComboBox()
        produto_combo.setObjectName("comboField")
        produto_combo.setEnabled(False)
        produto_combo.currentIndexChanged.connect(
            lambda: self.on_produto_selecionado(tipo_proposta)
        )
        self.produto_combos[tipo_proposta] = produto_combo
        produto_layout.addWidget(produto_combo)
        linha1_layout.addLayout(produto_layout)
        
        # Status
        status_layout = QVBoxLayout()
        status_layout.setSpacing(2)
        status_layout.addWidget(QLabel("Status:"))
        status_label = QLabel("Não selecionado")
        status_label.setObjectName("infoLabel")
        status_label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 3px;")
        status_label.setMinimumHeight(30)
        status_label.setAlignment(Qt.AlignCenter)
        self.status_labels[tipo_proposta] = status_label
        status_layout.addWidget(status_label)
        linha1_layout.addLayout(status_layout)
        
        # LINHA 2: Novos campos com LARGURAS FIXAS
        linha2_layout = QHBoxLayout()
        linha2_layout.setSpacing(10)
        
        # CPF - LARGURA FIXA
        cpf_layout = QVBoxLayout()
        cpf_layout.setSpacing(2)
        cpf_layout.addWidget(QLabel("CPF:"))
        cpf_input = QLineEdit()
        cpf_input.setPlaceholderText("000.000.000-00")
        cpf_input.setObjectName("inputField")
        cpf_input.setMaxLength(14)
        cpf_input.setFixedWidth(150)  # ⭐⭐ LARGURA FIXA
        cpf_input.textChanged.connect(self.formatar_cpf)
        self.cpf_inputs = getattr(self, 'cpf_inputs', {})
        self.cpf_inputs[tipo_proposta] = cpf_input
        cpf_layout.addWidget(cpf_input)
        linha2_layout.addLayout(cpf_layout)
        
        # Valor Liberado - LARGURA FIXA
        valor_layout = QVBoxLayout()
        valor_layout.setSpacing(2)
        valor_layout.addWidget(QLabel("Valor liberado:"))
        valor_input = QLineEdit()
        valor_input.setPlaceholderText("0,00")
        valor_input.setObjectName("inputField")
        valor_input.setFixedWidth(100)  # ⭐⭐ LARGURA FIXA
        valor_input.textChanged.connect(self.formatar_valor)
        self.valor_inputs = getattr(self, 'valor_inputs', {})
        self.valor_inputs[tipo_proposta] = valor_input
        valor_layout.addWidget(valor_input)
        linha2_layout.addLayout(valor_layout)

        # ⭐⭐ VALOR DE TROCO (apenas para Refin e Solicitação Interna) - LARGURA FIXA
        if tipo_proposta in ["Refin", "Solicitação Interna"]:
            troco_layout = QVBoxLayout()
            troco_layout.setSpacing(2)
            troco_layout.addWidget(QLabel("Valor de Troco:"))
            troco_input = QLineEdit()
            troco_input.setPlaceholderText("0,00")
            troco_input.setObjectName("inputField")
            troco_input.setFixedWidth(100)  # ⭐⭐ LARGURA FIXA
            troco_input.textChanged.connect(self.formatar_valor)
            self.troco_inputs = getattr(self, 'troco_inputs', {})
            self.troco_inputs[tipo_proposta] = troco_input
            troco_layout.addWidget(troco_input)
            linha2_layout.addLayout(troco_layout)
        
        # Prazo - LARGURA FIXA
        prazo_layout = QVBoxLayout()
        prazo_layout.setSpacing(2)
        prazo_layout.addWidget(QLabel("Prazo (meses):"))
        prazo_input = QLineEdit()
        prazo_input.setPlaceholderText("0")
        prazo_input.setObjectName("inputField")
        prazo_input.setFixedWidth(80)  # ⭐⭐ LARGURA FIXA
        prazo_input.setValidator(QIntValidator(0, 999, self))
        self.prazo_inputs = getattr(self, 'prazo_inputs', {})
        self.prazo_inputs[tipo_proposta] = prazo_input
        prazo_layout.addWidget(prazo_input)
        linha2_layout.addLayout(prazo_layout)
        
        # Observações - LARGURA EXPANSÍVEL que preenche o espaço disponível
        observacoes_layout = QVBoxLayout()
        observacoes_layout.setSpacing(2)
        observacoes_layout.addWidget(QLabel("Observações:"))
        observacoes_input = QLineEdit()
        observacoes_input.setPlaceholderText("Digite observações adicionais...")
        observacoes_input.setObjectName("inputField")

        # ⭐⭐ OBSERVAÇÕES EXPANSÍVEL - preenche o espaço restante
        observacoes_input.setMinimumWidth(250)
        observacoes_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.observacoes_inputs = getattr(self, 'observacoes_inputs', {})
        self.observacoes_inputs[tipo_proposta] = observacoes_input
        observacoes_layout.addWidget(observacoes_input)
        linha2_layout.addLayout(observacoes_layout)
        
        # Info data/hora criação
        data_info_label = QLabel("Data/Hora Criação: --/--/-- --:--:--")
        data_info_label.setObjectName("infoLabel")
        
        self.data_info_labels = getattr(self, 'data_info_labels', {})
        self.data_info_labels[tipo_proposta] = data_info_label
        
        layout.addLayout(input_layout)
        layout.addLayout(linha1_layout)
        layout.addLayout(linha2_layout)
        
        frame.setLayout(layout)
        return frame
        
    def formatar_cpf(self, text):
        """Formata o CPF enquanto o usuário digita"""
        sender = self.sender()
        if not sender:
            return
            
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, text))
        
        # Aplica a formatação
        if len(cpf) <= 3:
            formatted_cpf = cpf
        elif len(cpf) <= 6:
            formatted_cpf = f"{cpf[:3]}.{cpf[3:]}"
        elif len(cpf) <= 9:
            formatted_cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
        else:
            formatted_cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
        
        # Atualiza o texto sem disparar o sinal novamente
        sender.blockSignals(True)
        sender.setText(formatted_cpf)
        sender.setCursorPosition(len(formatted_cpf))
        sender.blockSignals(False)

    def formatar_valor(self, text):
        """Formata o valor monetário enquanto o usuário digita"""
        sender = self.sender()
        if not sender:
            return
            
        # Remove caracteres não numéricos, exceto vírgula
        valor = ''.join(filter(lambda x: x.isdigit() or x == ',', text))
        
        # Se houver mais de uma vírgula, mantém apenas a primeira
        if valor.count(',') > 1:
            partes = valor.split(',')
            valor = partes[0] + ',' + ''.join(partes[1:])
        
        # Move o cursor para o final
        sender.blockSignals(True)
        sender.setText(valor)
        sender.setCursorPosition(len(valor))
        sender.blockSignals(False)


    def validar_formato_contrato(self, texto, tipo_proposta):
        """Valida o formato baseado no tipo de proposta"""
        input_field = self.numero_inputs[tipo_proposta]
        
        # Limpar estilo anterior
        input_field.setStyleSheet("")
        
        print(f"🔍 Validando formato: '{texto}' | Tipo: {tipo_proposta}")
        
        # Verificar se o formato está completo
        formato_completo = self.verificar_formato_completo(texto, tipo_proposta)
        print(f"📋 Formato completo: {formato_completo}")
        
        if formato_completo:
            # Formato válido - estilo verde
            input_field.setStyleSheet("border: 2px solid #28a745;")
            print(f"✅ Formato válido: {texto}")
            
            # Configurar proposta em andamento
            self.configurar_proposta_em_andamento(texto, tipo_proposta)
                
        else:
            # Formato incompleto ou inválido
            if texto:  # Só mostra vermelho se já digitou algo
                input_field.setStyleSheet("border: 2px solid #dc3545;")
                print(f"❌ Formato inválido: {texto}")
            
            # Desabilitar tudo se formato não estiver completo
            self.regiao_combos[tipo_proposta].setEnabled(False)
            self.convenio_combos[tipo_proposta].setEnabled(False)
            self.produto_combos[tipo_proposta].setEnabled(False)
            
            # Resetar filtros dependentes
            self.convenio_combos[tipo_proposta].clear()
            self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
            
            self.produto_combos[tipo_proposta].clear()
            self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
            
            self.status_labels[tipo_proposta].setText("Não selecionado")
            self.status_labels[tipo_proposta].setStyleSheet("font-weight: bold; padding: 5px;")
            
            # ⭐⭐ CORREÇÃO: Desabilitar ambos os botões quando formato não está completo
            self.aprovar_buttons[tipo_proposta].setEnabled(False)
            self.recusar_buttons[tipo_proposta].setEnabled(False)
            
            # Se tinha proposta em andamento, limpar completamente
            if self.proposta_em_andamento and self.tipo_proposta_atual == tipo_proposta:
                print("🔄 Limpando proposta em andamento...")
                self.limpar_proposta(tipo_proposta)


    def limpar_proposta(self, tipo_proposta):
        """Limpa completamente todos os campos para uma nova proposta"""
        # Parar timer de duração
        self.timer_duracao.stop()
        
        # 1. Limpar campo principal
        self.numero_inputs[tipo_proposta].setEnabled(True)
        self.numero_inputs[tipo_proposta].clear()
        
        # 2. Resetar filtros para estado INICIAL COM "SELECIONE" E DESABILITADOS
        self.regiao_combos[tipo_proposta].setCurrentIndex(0)
        self.regiao_combos[tipo_proposta].setEnabled(False)
            
        self.convenio_combos[tipo_proposta].clear()
        self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
        self.convenio_combos[tipo_proposta].setEnabled(False)
        
        self.produto_combos[tipo_proposta].clear()
        self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
        self.produto_combos[tipo_proposta].setEnabled(False)
        
        self.status_labels[tipo_proposta].setText("Não selecionado")
        self.status_labels[tipo_proposta].setStyleSheet("font-weight: bold; padding: 5px;")
        
        # 3. ⭐⭐ LIMPAR NOVOS CAMPOS (incluindo troco)
        if hasattr(self, 'cpf_inputs') and tipo_proposta in self.cpf_inputs:
            self.cpf_inputs[tipo_proposta].clear()
        
        if hasattr(self, 'valor_inputs') and tipo_proposta in self.valor_inputs:
            self.valor_inputs[tipo_proposta].clear()
        
        if hasattr(self, 'prazo_inputs') and tipo_proposta in self.prazo_inputs:
            self.prazo_inputs[tipo_proposta].clear()
        
        if hasattr(self, 'observacoes_inputs') and tipo_proposta in self.observacoes_inputs:
            self.observacoes_inputs[tipo_proposta].clear()
        
        # ⭐⭐ LIMPAR CAMPO DE TROCO (se existir)
        if hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
            self.troco_inputs[tipo_proposta].clear()
        
        # 4. Resetar dados internos
        self.data_criacao = None
        self.data_conclusao = None
        self.proposta_em_andamento = False
        self.tarefas_concluidas = {}
        self.eh_reanalise = False
        self.proposta_original = None
        
        # 5. Atualizar interface
        self.data_info_labels[tipo_proposta].setText("Data/Hora Criação: --/--/-- --:--:--")
        
        # Checkboxes - desmarcar e desabilitar
        for checkbox in self.checkboxes_dict[tipo_proposta].values():
            checkbox.setEnabled(False)
            checkbox.setChecked(False)
        
        # Botões - desabilitar
        self.aprovar_buttons[tipo_proposta].setEnabled(False)
        self.recusar_buttons[tipo_proposta].setEnabled(False)
        
        # 6. Destravar abas
        self.destravar_todas_abas()
        
        print("✅ Contrato completamente limpo - pronto para nova análise")


    def mostrar_popup_reanalise(self, texto, proposta_existente, tipo_proposta):
        """Mostra popup quando o contrato já existe"""
        # EXCEÇÃO: Nunca deve chegar aqui para Solicitação Interna
        if tipo_proposta == "Solicitação Interna":
            print("❌ ERRO: Popup de reanálise não deveria ser chamado para Solicitação Interna")
            return
        
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
    <b>Contrato {texto} já analisado anteriormente.</b>

    <b>Informações da análise anterior:</b>
    • Tipo: {proposta_existente.get('tipo_proposta', 'N/A')}
    • Analista: {proposta_existente.get('analista', 'N/A')}
    • Status: <b>{proposta_existente.get('status', 'N/A')}</b>
    • Data de Criação: {data_criacao_str}
    • Data de Conclusão: {data_conclusao_str}
    • Duração: {proposta_existente.get('duracao_total', ' - ')}

    <b>Deseja fazer reanálise deste contrato?</b>
        """
        
        # Criar message box personalizada
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Contrato Existente")
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
            # Continuar com a configuração da proposta em andamento
            self.continuar_configuracao_reanalise(texto, tipo_proposta)
            
        elif msg_box.clickedButton() == btn_nova:
            # Usuário quer digitar outra proposta, limpar campo
            self.numero_inputs[tipo_proposta].clear()
            self.eh_reanalise = False
            self.proposta_original = None
        else:
            # Cancelar, limpar campo e sair
            self.numero_inputs[tipo_proposta].clear()
            self.eh_reanalise = False
            self.proposta_original = None


    def continuar_configuracao_reanalise(self, numero_contrato, tipo_proposta):
        """Continua a configuração após usuário optar por reanálise"""
        print(f"✅ Configurando REANÁLISE: {tipo_proposta}")
        
        # TRAVAR o campo de entrada
        self.numero_inputs[tipo_proposta].setEnabled(False)
        
        # ⭐⭐ HABILITAR os filtros (já que é uma reanálise com contrato válido)
        self.regiao_combos[tipo_proposta].setEnabled(True)
        print("✅ Filtro de região habilitado para reanálise")
        
        # Registrar dados internos
        self.data_criacao = datetime.now()
        self.tipo_proposta_atual = tipo_proposta
        self.proposta_em_andamento = True
        
        # Já definimos self.eh_reanalise = True e self.proposta_original na função anterior
        
        # Iniciar timer para atualizar duração
        self.timer_duracao.start(1000)
        
        self.data_info_labels[tipo_proposta].setText(
            f"Data/Hora Criação: {self.data_criacao.strftime('%d/%m/%Y %H:%M:%S')} (Reanálise)"
        )
        
        # HABILITAR os checkboxes
        for checkbox in self.checkboxes_dict[tipo_proposta].values():
            checkbox.setEnabled(True)
        
        # VALIDAR ESTADO INICIAL DOS BOTÕES
        self.validar_botoes_apos_mudanca_filtro(tipo_proposta)
        
        # TRAVANDO as outras abas
        self.travar_outras_abas(tipo_proposta)
        
        print(f"✅ REANÁLISE em andamento: {tipo_proposta}")

    def verificar_formato_completo(self, texto, tipo_proposta):
        """Verifica se o formato está completo baseado no tipo"""
        print(f"🔎 Verificando formato completo: '{texto}' | Tipo: {tipo_proposta}")
        
        if tipo_proposta == "Solicitação Interna":
            # ⭐⭐ ACEITA DOIS FORMATOS ⭐⭐
            
            # Formato 1: A00-0000000000 (Letra + 2 dígitos + hífen + 10 dígitos)
            if len(texto) == 14 and '-' in texto:
                partes = texto.split('-')
                print(f"📝 Formato 1 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 3 and 
                    partes[0][0].isalpha() and  # Primeiro caractere é letra
                    partes[0][1:].isdigit() and  # Próximos 2 são dígitos
                    len(partes[1]) == 10 and partes[1].isdigit()):  # 10 dígitos após hífen
                    print("✅ Formato 1 válido: A00-0000000000")
                    return True
            
            # Formato 2: 00-0000000000 (2 dígitos + hífen + 10 dígitos)
            if len(texto) == 13 and '-' in texto:
                partes = texto.split('-')
                print(f"📝 Formato 2 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 2 and partes[0].isdigit() and
                    len(partes[1]) == 10 and partes[1].isdigit()):
                    print("✅ Formato 2 válido: 00-0000000000")
                    return True
            
            print("❌ Nenhum formato válido para Solicitação Interna")
            return False
            
        else:
            # Outras abas: apenas formato XX-XXXXXXXXXX
            if len(texto) == 13 and '-' in texto:
                partes = texto.split('-')
                print(f"📝 Outras abas - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 2 and partes[0].isdigit() and
                    len(partes[1]) == 10 and partes[1].isdigit()):
                    print("✅ Formato válido para outras abas: 00-0000000000")
                    return True
            
            print("❌ Formato inválido para outras abas")
            return False
    
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
        
        # ⭐⭐ VALIDAR BOTÕES APÓS MUDANÇA
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
            
            # ⭐⭐ CORREÇÃO: LÓGICA SEPARADA
            # APROVAR: precisa de tarefas + filtros
            # RECUSAR: precisa APENAS de filtros
            self.aprovar_buttons[tipo_proposta].setEnabled(todas_concluidas and filtros_preenchidos)
            self.recusar_buttons[tipo_proposta].setEnabled(filtros_preenchidos)
            
            print(f"🔍 Validação após filtro - {tipo_proposta}:")
            print(f"   - Recusar habilitado: {filtros_preenchidos} (filtros: {filtros_preenchidos})")
    
    def get_dados_filtro_atual(self, tipo_proposta):
        """Retorna os dados atualmente selecionados nos filtros E novos campos"""
        dados = {
            'regiao': self.regiao_combos[tipo_proposta].currentData(),
            'convenio': self.convenio_combos[tipo_proposta].currentData(),
            'produto': self.produto_combos[tipo_proposta].currentData(),
            'status': self.status_labels[tipo_proposta].text()
        }
        
        # ⭐⭐ ADICIONAR NOVOS CAMPOS
        if hasattr(self, 'cpf_inputs') and tipo_proposta in self.cpf_inputs:
            dados['cpf'] = self.cpf_inputs[tipo_proposta].text()
        
        if hasattr(self, 'valor_inputs') and tipo_proposta in self.valor_inputs:
            dados['valor_liberado'] = self.valor_inputs[tipo_proposta].text()
            dados['moeda'] = "R$"
        
        if hasattr(self, 'prazo_inputs') and tipo_proposta in self.prazo_inputs:
            dados['prazo'] = self.prazo_inputs[tipo_proposta].text()
            dados['unidade_prazo'] = "Meses"
        
        if hasattr(self, 'observacoes_inputs') and tipo_proposta in self.observacoes_inputs:
            dados['observacoes'] = self.observacoes_inputs[tipo_proposta].text()
        
        # ⭐⭐ ADICIONAR VALOR DE TROCO (apenas para Refin e Solicitação Interna)
        if tipo_proposta in ["Refin", "Solicitação Interna"] and hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
            dados['valor_troco'] = self.troco_inputs[tipo_proposta].text()
            dados['moeda_troco'] = "R$"
        
        return dados

    
    def criar_area_tarefas(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # ⭐⭐ ALTURA REDUZIDA - ajustada para telas menores
        scroll.setMinimumHeight(80)  # Reduzido de 100 para 80
        scroll.setMaximumHeight(150)  # Reduzido de 200 para 150
        
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
        
        layout.addWidget(scroll)
        
        frame.setLayout(layout)
        return frame


    def criar_area_acoes(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)  # ⭐⭐ REDUZIDO verticalmente (8,8,8,8 -> 8,4,8,4)
        layout.setSpacing(6)  # ⭐⭐ REDUZIDO ESPAÇAMENTO (8 -> 6)
        
        aprovar_button = QPushButton("✅ Aprovar Contrato")
        aprovar_button.setObjectName("successButton")
        aprovar_button.clicked.connect(lambda: self.finalizar_proposta(tipo_proposta, "Aprovada"))
        aprovar_button.setEnabled(False)
        
        recusar_button = QPushButton("❌ Recusar Contrato")  
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
        
        
        # Frame de filtros
        filtros_frame = self.criar_filtros_historico()
        
        # ⭐⭐ TABELA COM TODOS OS NOVOS CAMPOS
        self.historico_table = QTableWidget()
        self.historico_table.setColumnCount(17)  # ⭐⭐ AUMENTADO para 17 colunas
        self.historico_table.setHorizontalHeaderLabels([
            "Tipo", "Número", "Analista", "Status", "Data Criação", "Data Conclusão", "Duração",
            "Região", "Convênio", "Produto", "Status Convênio", 
            "CPF", "Valor Liberado", "Prazo", "Observações", "Valor de Troco", "Motivo de Recusa"  # ⭐⭐ NOVAS COLUNAS
        ])
        
        # ⭐⭐ CONFIGURAÇÃO PARA REDIMENSIONAR COLUNAS
        header = self.historico_table.horizontalHeader()
        
        # Definir modo de redimensionamento como Interactive para permitir ajuste manual
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Definir tamanhos iniciais para as colunas
        larguras_colunas = {
            0: 120,   # Tipo
            1: 120,   # Número
            2: 120,   # Analista
            3: 100,   # Status
            4: 140,   # Data Criação
            5: 140,   # Data Conclusão
            6: 80,    # Duração
            7: 100,   # Região
            8: 120,   # Convênio
            9: 120,   # Produto
            10: 120,  # Status Convênio
            11: 120,  # CPF
            12: 100,  # Valor Liberado
            13: 80,   # Prazo
            14: 200,  # Observações
            15: 100,  # Valor de Troco
            16: 150   # Motivo de Recusa
        }
        
        for col, largura in larguras_colunas.items():
            self.historico_table.setColumnWidth(col, largura)
        
        # Permitir que o usuário redimensione as colunas
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)
        
        # 🔒 IMPEDIR EDIÇÃO DOS DADOS NA TABELA
        self.historico_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.historico_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.historico_table.setFocusPolicy(Qt.NoFocus)
        
        # ⭐⭐ HABILITAR ORDENAÇÃO POR COLUNAS
        self.historico_table.setSortingEnabled(True)
        
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
        layout.addSpacing(8)
        layout.addLayout(analista_layout)
        layout.addSpacing(8)
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
        """Exporta os dados da tabela para XLSX incluindo todos os novos campos"""
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
                df.to_excel(writer, sheet_name='Contratos', index=False)
                
                # Ajustar largura das colunas automaticamente
                worksheet = writer.sheets['Contratos']
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
        if texto.isdigit() and len(texto) == 13:
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
    <b>Contrato {texto} já analisada anteriormente.</b>

    <b>Informações da análise anterior:</b>
    • Tipo: {proposta_existente.get('tipo_proposta', 'N/A')}
    • Analista: {proposta_existente.get('analista', 'N/A')}
    • Status: <b>{proposta_existente.get('status', 'N/A')}</b>
    • Data de Criação: {data_criacao_str}
    • Data de Conclusão: {data_conclusao_str}
    • Duração: {proposta_existente.get('duracao_total', ' - ')}

    <b>Deseja fazer reanálise desta contrato?</b>
                """
                
                # Criar message box personalizada
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Contrato Existente")
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
                    QMessageBox.information(self, "Reanálise", "Modo de reanálise ativado. O contrato será salva com ' - Reanalise' no tipo.")
                    
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
                # Contrato novo
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


    def configurar_proposta_em_andamento(self, numero_contrato, tipo_proposta):
        """Configura o estado quando uma proposta está em andamento"""
        print(f"🔍 Verificando contrato: {numero_contrato}")
        
        # EXCEÇÃO: Para Solicitação Interna, não verifica se já existe
        if tipo_proposta != "Solicitação Interna":
            try:
                # Verificar se o contrato já existe no sistema (apenas para outras abas)
                proposta_existente = self.proposta_service.verificar_proposta_existente(numero_contrato)
                
                if proposta_existente:
                    print("⚠️ Contrato já existe - mostrando popup reanálise")
                    # Contrato já existe - mostrar popup de reanálise
                    self.mostrar_popup_reanalise(numero_contrato, proposta_existente, tipo_proposta)
                    return  # ⭐⭐ IMPORTANTE: Sai da função aqui se mostrar popup
                else:
                    print("✅ Contrato novo - prosseguindo normalmente")
            except Exception as e:
                print(f"❌ Erro ao verificar contrato existente: {e}")
                # Em caso de erro, prossegue como contrato novo
                QMessageBox.warning(self, "Aviso", "Erro ao verificar contrato existente. Prosseguindo como novo contrato.")
        else:
            print("✅ Solicitação Interna - não verifica existência")
        
        # ⭐⭐ SÓ CHEGA AQUI SE:
        # 1. É Solicitação Interna OU
        # 2. É outra aba mas o contrato é NOVO OU
        # 3. Houve erro na verificação
        
        print("✅ Configurando proposta em andamento")
        
        # TRAVAR o campo de entrada
        self.numero_inputs[tipo_proposta].setEnabled(False)
        
        # ⭐⭐ O FILTRO DE REGIÃO JÁ FOI HABILITADO NA validação_formato_contrato ⭐⭐
        # Apenas verificar se está habilitado
        regiao_habilitada = self.regiao_combos[tipo_proposta].isEnabled()
        print(f"🔍 Estado do filtro região: {'✅ Habilitado' if regiao_habilitada else '❌ Desabilitado'}")
        
        # Se por algum motivo não estiver habilitado, habilitar agora
        if not regiao_habilitada:
            self.regiao_combos[tipo_proposta].setEnabled(True)
            print("✅ Filtro de região habilitado (correção)")
        
        # Registrar dados internos
        self.data_criacao = datetime.now()
        self.tipo_proposta_atual = tipo_proposta
        self.proposta_em_andamento = True
        
        # EXCEÇÃO: Para Solicitação Interna, nunca é reanálise
        if tipo_proposta == "Solicitação Interna":
            self.eh_reanalise = False
            self.proposta_original = None
        else:
            # Para outras abas, também não é reanálise (já verificamos que é novo)
            self.eh_reanalise = False
            self.proposta_original = None
        
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
        
        # TRAVANDO as outras abas
        self.travar_outras_abas(tipo_proposta)
        
        print(f"✅ Proposta em andamento: {tipo_proposta}")

    def verificar_filtros_preenchidos(self, tipo_proposta):
        """Verifica se todos os filtros obrigatórios estão preenchidos, incluindo Valor de Troco quando aplicável"""
        dados_filtro = self.get_dados_filtro_atual(tipo_proposta)
        
        # Verificar se todos os campos obrigatórios estão preenchidos
        regiao_preenchida = bool(dados_filtro.get('regiao', ''))
        convenio_preenchido = bool(dados_filtro.get('convenio', ''))
        produto_preenchido = bool(dados_filtro.get('produto', ''))
        
        # ⭐⭐ VERIFICAR VALOR DE TROCO (obrigatório nas abas Refin e Solicitação Interna)
        troco_preenchido = True  # Por padrão é True (não obrigatório)
        if tipo_proposta in ["Refin", "Solicitação Interna"]:
            troco_valor = dados_filtro.get('valor_troco', '')
            # Verificar se o campo existe e não está vazio
            troco_preenchido = bool(troco_valor and troco_valor.strip() and troco_valor != '0,00')
            print(f"🔍 Validação Valor de Troco: '{troco_valor}' -> Preenchido: {troco_preenchido}")
        
        todos_preenchidos = regiao_preenchida and convenio_preenchido and produto_preenchido and troco_preenchido
        
        if not todos_preenchidos:
            print("❌ Campos obrigatórios não preenchidos:")
            print(f"   - Região: {'✅' if regiao_preenchida else '❌'} {dados_filtro.get('regiao', 'Não selecionada')}")
            print(f"   - Convênio: {'✅' if convenio_preenchido else '❌'} {dados_filtro.get('convenio', 'Não selecionado')}")
            print(f"   - Produto: {'✅' if produto_preenchido else '❌'} {dados_filtro.get('produto', 'Não selecionado')}")
            if tipo_proposta in ["Refin", "Solicitação Interna"]:
                print(f"   - Valor de Troco: {'✅' if troco_preenchido else '❌'} '{dados_filtro.get('valor_troco', 'Não preenchido')}'")
        
        return todos_preenchidos
    
    def atualizar_tarefa(self, tarefa_key, estado, tipo_proposta):
        self.tarefas_concluidas[tarefa_key] = (estado == Qt.Checked)
        
        # Verificar se TODOS os checkboxes estão marcados E filtros preenchidos
        if self.proposta_em_andamento and tipo_proposta == self.tipo_proposta_atual:
            todas_concluidas = self.verificar_todas_tarefas_concluidas(tipo_proposta)
            filtros_preenchidos = self.verificar_filtros_preenchidos(tipo_proposta)
            
            # ⭐⭐ CORREÇÃO: LÓGICA SEPARADA PARA CADA BOTÃO
            # APROVAR: precisa de TODAS as tarefas + filtros preenchidos
            # RECUSAR: precisa APENAS dos filtros preenchidos (NÃO depende de tarefas)
            
            # Botão APROVAR: depende de tarefas + filtros
            self.aprovar_buttons[tipo_proposta].setEnabled(todas_concluidas and filtros_preenchidos)
            
            # Botão RECUSAR: depende APENAS de filtros (NUNCA de tarefas)
            self.recusar_buttons[tipo_proposta].setEnabled(filtros_preenchidos)
            
            # Debug
            print(f"🔍 Estado dos botões - {tipo_proposta}:")
            print(f"   - Tarefas concluídas: {todas_concluidas}")
            print(f"   - Filtros preenchidos: {filtros_preenchidos}")
            print(f"   - Aprovar habilitado: {todas_concluidas and filtros_preenchidos}")
            print(f"   - Recusar habilitado: {filtros_preenchidos} (só depende dos filtros)")
    
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
    




    def recusar_proposta(self, tipo_proposta):
        """Abre popup para selecionar motivo da recusa"""
        # ⭐⭐ NÃO VALIDAR TAREFAS PARA RECUSA
        # Apenas verificar filtros obrigatórios
        if not self.verificar_filtros_preenchidos(tipo_proposta):
            mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
            if tipo_proposta in ["Refin", "Solicitação Interna"]:
                mensagem_erro += "\n• Valor de Troco"
            mensagem_erro += "\n\nAntes de recusar a proposta."
            
            QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
            return
        
        dialog = MotivoRecusaDialog(self)
        dialog.motivo_selecionado.connect(lambda motivo_id, descricao: self.on_motivo_recusa_selecionado(tipo_proposta, motivo_id, descricao))
        dialog.exec_()

    def on_motivo_recusa_selecionado(self, tipo_proposta, motivo_id, descricao):
        """Callback quando um motivo de recusa é selecionado"""
        print(f"Motivo selecionado: {motivo_id} - {descricao}")
        
        # ⭐⭐ NÃO VALIDAR TAREFAS PARA RECUSA - apenas filtros
        if not self.verificar_filtros_preenchidos(tipo_proposta):
            mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
            if tipo_proposta in ["Refin", "Solicitação Interna"]:
                mensagem_erro += "\n• Valor de Troco"
            mensagem_erro += "\n\nAntes de recusar a proposta."
            
            QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
            return
        
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
        # ⭐⭐ VALIDAÇÃO APENAS DOS FILTROS OBRIGATÓRIOS (não valida tarefas para recusa)
        if not self.verificar_filtros_preenchidos(tipo_proposta):
            mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
            if tipo_proposta in ["Refin", "Solicitação Interna"]:
                mensagem_erro += "\n• Valor de Troco"
            mensagem_erro += "\n\nAntes de finalizar a proposta."
            
            QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
            return
        
        numero = self.numero_inputs[tipo_proposta].text().strip()
        
        # VALIDAÇÃO POR TIPO
        if not self.verificar_formato_completo(numero, tipo_proposta):
            if tipo_proposta == "Solicitação Interna":
                QMessageBox.warning(self, "Erro", 
                                "Número do contrato inválido!\n"
                                "Formatos aceitos:\n"
                                "• 00-1234567890 (2 dígitos + 10 dígitos)\n"
                                "• A00-1234567890 (Letra + 2 dígitos + 10 dígitos)")
            else:
                QMessageBox.warning(self, "Erro", 
                                "Número do contrato inválido!\n"
                                "Formato deve ser: 2 dígitos + 10 dígitos\n"
                                "Exemplo: 50-1234567890")
            return
        
        # ⭐⭐ NÃO VALIDAR TAREFAS PARA RECUSA
        
        # Registrar data de conclusão
        self.data_conclusao = datetime.now()
        
        # Parar timer de duração
        self.timer_duracao.stop()
        
        # Calcular duração total
        duracao_total = self.calcular_duracao_total()
        
        # Se for reanálise, adicionar " - Reanalise" ao tipo
        tipo_final = tipo_proposta
        if self.eh_reanalise and tipo_proposta != "Solicitação Interna":
            tipo_final = f"{tipo_proposta} - Reanalise"
        
        # Obter dados dos filtros
        dados_filtro = self.get_dados_filtro_atual(tipo_proposta)
        
        # Adicionar motivo da recusa aos dados
        dados_filtro['motivo_recusa_id'] = motivo_id
        dados_filtro['motivo_recusa_descricao'] = motivo_descricao
        
        # Adicionar novos campos
        dados_filtro['cpf'] = self.cpf_inputs.get(tipo_proposta, "").text() if hasattr(self, 'cpf_inputs') and tipo_proposta in self.cpf_inputs else ""
        dados_filtro['valor_liberado'] = self.valor_inputs.get(tipo_proposta, "").text() if hasattr(self, 'valor_inputs') and tipo_proposta in self.valor_inputs else ""
        dados_filtro['moeda'] = "R$"
        dados_filtro['prazo'] = self.prazo_inputs.get(tipo_proposta, "").text() if hasattr(self, 'prazo_inputs') and tipo_proposta in self.prazo_inputs else ""
        dados_filtro['unidade_prazo'] = "Meses"
        dados_filtro['observacoes'] = self.observacoes_inputs.get(tipo_proposta, "").text() if hasattr(self, 'observacoes_inputs') and tipo_proposta in self.observacoes_inputs else ""
        
        # Adicionar Valor de Troco (apenas para Refin e Solicitação Interna)
        if tipo_proposta in ["Refin", "Solicitação Interna"]:
            dados_filtro['valor_troco'] = self.troco_inputs.get(tipo_proposta, "").text() if hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs else ""
            dados_filtro['moeda_troco'] = "R$"
        
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
        # VALIDAÇÃO OBRIGATÓRIA DOS FILTROS (para APROVAR e RECUSAR)
        if not self.verificar_filtros_preenchidos(tipo_proposta):
            mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
            if tipo_proposta in ["Refin", "Solicitação Interna"]:
                mensagem_erro += "\n• Valor de Troco"
            mensagem_erro += "\n\nAntes de finalizar a proposta."
            
            QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
            return
        
        numero = self.numero_inputs[tipo_proposta].text().strip()
        
        # VALIDAÇÃO POR TIPO
        if not self.verificar_formato_completo(numero, tipo_proposta):
            if tipo_proposta == "Solicitação Interna":
                QMessageBox.warning(self, "Erro", 
                                "Número do contrato inválido!\n"
                                "Formatos aceitos:\n"
                                "• 00-1234567890 (2 dígitos + 10 dígitos)\n"
                                "• A00-1234567890 (Letra + 2 dígitos + 10 dígitos)")
            else:
                QMessageBox.warning(self, "Erro", 
                                "Número do contrato inválido!\n"
                                "Formato deve ser: 2 dígitos + 10 dígitos\n"
                                "Exemplo: 50-1234567890")
            return
        
        # ⭐⭐ CORREÇÃO: Apenas para APROVAÇÃO verificar se TODAS as tarefas foram concluídas
        # Para RECUSA, não precisa verificar tarefas - REMOVIDA A VALIDAÇÃO DE TAREFAS PARA RECUSA
        if status == "Aprovada" and not self.verificar_todas_tarefas_concluidas(tipo_proposta):
            QMessageBox.warning(self, "Atenção", "Todas as tarefas devem ser concluídas para aprovar a proposta!")
            return
        
        # Registrar data de conclusão
        self.data_conclusao = datetime.now()
        
        # Parar timer de duração
        self.timer_duracao.stop()
        
        # Calcular duração total
        duracao_total = self.calcular_duracao_total()
        
        # Se for reanálise, adicionar " - Reanalise" ao tipo (EXCETO para Solicitação Interna)
        tipo_final = tipo_proposta
        if self.eh_reanalise and tipo_proposta != "Solicitação Interna":
            tipo_final = f"{tipo_proposta} - Reanalise"
                
        # Obter dados dos filtros
        dados_filtro = self.get_dados_filtro_atual(tipo_proposta)
        
        # ⭐⭐ ADICIONAR NOVOS CAMPOS AOS DADOS
        dados_filtro['cpf'] = self.cpf_inputs.get(tipo_proposta, "").text() if hasattr(self, 'cpf_inputs') and tipo_proposta in self.cpf_inputs else ""
        dados_filtro['valor_liberado'] = self.valor_inputs.get(tipo_proposta, "").text() if hasattr(self, 'valor_inputs') and tipo_proposta in self.valor_inputs else ""
        dados_filtro['moeda'] = "R$"
        dados_filtro['prazo'] = self.prazo_inputs.get(tipo_proposta, "").text() if hasattr(self, 'prazo_inputs') and tipo_proposta in self.prazo_inputs else ""
        dados_filtro['unidade_prazo'] = "Meses"
        dados_filtro['observacoes'] = self.observacoes_inputs.get(tipo_proposta, "").text() if hasattr(self, 'observacoes_inputs') and tipo_proposta in self.observacoes_inputs else ""
        
        # ⭐⭐ ADICIONAR VALOR DE TROCO (apenas para Refin e Solicitação Interna)
        if tipo_proposta in ["Refin", "Solicitação Interna"]:
            dados_filtro['valor_troco'] = self.troco_inputs.get(tipo_proposta, "").text() if hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs else ""
            dados_filtro['moeda_troco'] = "R$"
        
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
        current_index = self.tabs.indexOf(self.tabs.currentWidget())
        
        for i in range(self.tabs.count()):
            if i != current_index:
                self.tabs.setTabEnabled(i, False)
        
        print("🔒 Abas travadas - proposta em andamento")
    
    def destravar_todas_abas(self):
        """Destrava todas as abas quando não há proposta em andamento"""
        for i in range(self.tabs.count()):
            self.tabs.setTabEnabled(i, True)
        
        print("🔓 Todas as abas destravadas")
    
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
        """Preenche a tabela de histórico com todas as propostas incluindo os novos campos"""
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
            
            # ⭐⭐ NOVOS CAMPOS ADICIONADOS
            cpf = dados_filtro.get('cpf', 'N/A')
            valor_liberado = dados_filtro.get('valor_liberado', 'N/A')
            prazo = dados_filtro.get('prazo', 'N/A')
            observacoes = dados_filtro.get('observacoes', 'N/A')
            valor_troco = dados_filtro.get('valor_troco', 'N/A')
            motivo_recusa = dados_filtro.get('motivo_recusa_descricao', 'N/A')
            
            self.historico_table.setItem(row, 11, QTableWidgetItem(cpf))
            self.historico_table.setItem(row, 12, QTableWidgetItem(valor_liberado))
            self.historico_table.setItem(row, 13, QTableWidgetItem(prazo))
            self.historico_table.setItem(row, 14, QTableWidgetItem(observacoes))
            self.historico_table.setItem(row, 15, QTableWidgetItem(valor_troco))
            self.historico_table.setItem(row, 16, QTableWidgetItem(motivo_recusa))
        
        # ⭐⭐ AJUSTAR AUTOMATICAMENTE AS COLUNAS AO CONTEÚDO (opcional)
            self.historico_table.resizeColumnsToContents()