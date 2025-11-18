from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QComboBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
import os
import sys

class PropostasWindowPart3:
    """Parte 3 - Criação de abas e áreas de input"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
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
            placeholder = "cinco padrões distintos vide manual"
            max_length = 15
            texto_inicial = ""
            label_text = "Nº Contrato:"
        else:
            placeholder = "ex: 50-12345678900"
            max_length = 14
            texto_inicial = ""
            label_text = "Nº Contrato:"

        numero_input = QLineEdit()
        numero_input.setPlaceholderText(placeholder)
        numero_input.setObjectName("inputField")
        numero_input.setMaxLength(max_length)
        numero_input.setText(texto_inicial)
        numero_input.setFixedWidth(200)  # ⭐⭐ AUMENTADO PARA 200
        numero_input.setStyleSheet("""
            QLineEdit {
                font-size: 10px;  /* ⭐⭐ FONTE MENOR PARA PLACEHOLDER */
            }
        """)
        
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
        
        # ⭐⭐ BOTÕES DO SISTEMA (Cadastrar, Manutenção, Sair) - EM TODAS AS ABAS EXCETO HISTÓRICO
        if tipo_proposta != "Histórico":  # ⭐⭐ AGORA EM TODAS AS ABAS EXCETO HISTÓRICO
            # Botão Cadastrar Usuário (apenas para Dev)
            cadastrar_button = QPushButton("Cadastrar")
            cadastrar_button.setObjectName("primaryButton")
            cadastrar_button.clicked.connect(self.cadastrar_usuario)
            cadastrar_button.setFixedWidth(120)
            cadastrar_button.setFixedHeight(28)
            
            # Botão Manutenção de Usuários (apenas para Gerente e Dev)
            manutencao_button = QPushButton("Manutenção")
            manutencao_button.setObjectName("primaryButton")
            manutencao_button.clicked.connect(self.abrir_manutencao_usuarios.emit)
            manutencao_button.setFixedWidth(120)
            manutencao_button.setFixedHeight(28)
            
            # Botão Sair
            logout_button = QPushButton("Sair")
            logout_button.setObjectName("logoutButton")
            logout_button.clicked.connect(self.logout_request.emit)
            logout_button.setFixedWidth(70)
            logout_button.setFixedHeight(28)
            
            # Configurar visibilidade dos botões baseado no perfil
            if self.user_data['perfil'] == 'Analista':
                cadastrar_button.setVisible(False)
                manutencao_button.setVisible(False)
            # Opção 1 (mais clara):
            if self.user_data['perfil'] in ['Supervisor', 'Gerente']:
                cadastrar_button.setVisible(False)
            
            # Adicionar botões ao layout
            input_layout.addWidget(cadastrar_button)
            input_layout.addWidget(manutencao_button)
            input_layout.addWidget(logout_button)
        
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
        if tipo_proposta in ["Refin", "Saque Direcionado", "Solicitação Interna"]:
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