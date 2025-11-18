from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget)
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QIcon
import os
import sys
from services.proposta_service import PropostaService
from services.user_service import UserService
from services.google_sheets_service import GoogleSheetsService
from services.complemento_propostas_window_1 import PropostasWindowPart1
from services.complemento_propostas_window_2 import PropostasWindowPart2
from services.complemento_propostas_window_3 import PropostasWindowPart3
from services.complemento_propostas_window_4 import PropostasWindowPart4
from services.complemento_propostas_window_5 import PropostasWindowPart5
from services.complemento_propostas_window_6 import PropostasWindowPart6
from services.complemento_propostas_window_7 import PropostasWindowPart7
from services.complemento_propostas_window_8 import PropostasWindowPart8
from services.complemento_propostas_window_9 import PropostasWindowPart9
from services.complemento_propostas_window_10 import PropostasWindowPart10
from utils.styles import get_propostas_styles

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PropostasWindow(QWidget, 
                     PropostasWindowPart1,
                     PropostasWindowPart2,
                     PropostasWindowPart3,
                     PropostasWindowPart4,
                     PropostasWindowPart5,
                     PropostasWindowPart6,
                     PropostasWindowPart7,
                     PropostasWindowPart8,
                     PropostasWindowPart9,
                     PropostasWindowPart10):
    
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
            icon_path = 'assets/logo.png'
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                print(f"✅ Ícone carregado: {icon_path}")
            else:
                print(f"❌ Logo não encontrada. Verifique o caminho: {icon_path}")
        except Exception as e:
            print(f"❌ Erro ao carregar ícone: {e}")

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