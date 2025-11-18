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

class PropostasWindowPart5:
    """Parte 5 - Criação da aba de histórico e filtros"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
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