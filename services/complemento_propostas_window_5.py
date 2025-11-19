# services/complemento_propostas_window_5.py (CORRIGIDO)
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QTableWidget, QHeaderView, QComboBox, QDateEdit,
                             QTableWidgetItem)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import os
import sys


class PropostasWindowPart5:
    """Parte 5 - Criação da aba de histórico e filtros COM BOTÃO TMA"""
    
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
        
        # Frame de filtros (AGORA COM BOTÃO TMA)
        filtros_frame = self.criar_filtros_historico()
        
        # ⭐⭐ TABELA COM TODOS OS NOVOS CAMPOS
        self.historico_table = QTableWidget()
        self.historico_table.setColumnCount(17)
        self.historico_table.setHorizontalHeaderLabels([
            "Tipo", "Número", "Analista", "Status", "Data Criação", "Data Conclusão", "Duração",
            "Região", "Convênio", "Produto", "Status Convênio", 
            "CPF", "Valor Liberado", "Prazo", "Observações", "Valor de Troco", "Motivo de Recusa"
        ])
        
        # ⭐⭐ CONFIGURAÇÃO PARA REDIMENSIONAR COLUNAS
        header = self.historico_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Definir tamanhos iniciais para as colunas
        larguras_colunas = {
            0: 120, 1: 120, 2: 120, 3: 100, 4: 140, 5: 140, 6: 80,
            7: 100, 8: 120, 9: 120, 10: 120, 11: 120, 12: 100,
            13: 80, 14: 200, 15: 100, 16: 150
        }
        
        for col, largura in larguras_colunas.items():
            self.historico_table.setColumnWidth(col, largura)
        
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
        
        # ⭐⭐ RODAPÉ COM TOTAL DE PROPOSTAS
        footer_layout = QHBoxLayout()
        self.label_total_historico = QLabel("Total: 0 propostas")
        self.label_total_historico.setFont(QFont("Arial", 10, QFont.Bold))
        footer_layout.addWidget(self.label_total_historico)
        footer_layout.addStretch()
        layout.addLayout(footer_layout)
        
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
        self.data_inicio.setDate(QDate.currentDate().addDays(-30))
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setObjectName("dateField")
        self.data_inicio.setFixedWidth(100)
        
        self.data_fim = QDateEdit()
        self.data_fim.setDate(QDate.currentDate())
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setObjectName("dateField")
        self.data_fim.setFixedWidth(100)
        
        periodo_layout.addWidget(QLabel("De:"))
        periodo_layout.addWidget(self.data_inicio)
        periodo_layout.addWidget(QLabel("Até:"))
        periodo_layout.addWidget(self.data_fim)
        
        # Filtro por Analista
        analista_layout = QHBoxLayout()
        analista_layout.addWidget(QLabel("Analista:"))
        
        self.combo_analista = QComboBox()
        self.combo_analista.setObjectName("comboField")
        self.combo_analista.setFixedWidth(150)
        
        # Se for analista, mostra apenas o próprio login
        if self.user_data['perfil'] == 'Analista':
            self.combo_analista.addItem(self.user_data['login'])
            self.combo_analista.setEnabled(False)
        else:
            # Para outros perfis, carrega todos os analistas
            self.combo_analista.addItem("Todos", "todos")
            self.carregar_analistas()
        
        analista_layout.addWidget(self.combo_analista)
        
        # Botões
        botoes_layout = QHBoxLayout()
        
        self.btn_filtrar_historico = QPushButton("🔍 Filtrar")
        self.btn_filtrar_historico.setObjectName("primaryButton")
        self.btn_filtrar_historico.setFixedWidth(100)
        self.btn_filtrar_historico.clicked.connect(self.aplicar_filtros)
        
        self.exportar_button = QPushButton("📊 Exportar")
        self.exportar_button.setObjectName("successButton")
        self.exportar_button.setFixedWidth(100)
        self.exportar_button.clicked.connect(self.exportar_para_xlsx)
        
        # ⭐⭐ BOTÃO TMA ADICIONADO AQUI
        if self.user_data['perfil'] != 'Analista':
            self.btn_tma_historico = QPushButton("📈 TMA")
            self.btn_tma_historico.setObjectName("infoButton")
            self.btn_tma_historico.setFixedWidth(80)
            # A conexão do click será feita na Part11
        
        botoes_layout.addWidget(self.btn_filtrar_historico)
        botoes_layout.addWidget(self.exportar_button)
        # ⭐⭐ ADICIONA BOTÃO TMA AO LAYOUT (se não for Analista)
        if self.user_data['perfil'] != 'Analista':
            botoes_layout.addWidget(self.btn_tma_historico)

        
        # Só mostra botão exportar se não for Analista
        if self.user_data['perfil'] == 'Analista':
            self.exportar_button.setVisible(False)
        
        # Adicionar todos os layouts ao layout principal
        layout.addLayout(periodo_layout)
        layout.addSpacing(8)
        layout.addLayout(analista_layout)
        layout.addSpacing(8)
        layout.addLayout(botoes_layout)
        layout.addStretch()
        
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
            data_inicio = self.data_inicio.date().toPyDate()
            data_fim = self.data_fim.date().toPyDate()
            analista = self.combo_analista.currentData()
            
            print(f"🔍 Aplicando filtros - Data: {data_inicio} a {data_fim}, Analista: {analista}")
            
            # ⭐⭐ CORREÇÃO: Usar o método correto que existe no PropostaService
            propostas = self.proposta_service.listar_propostas_simples_filtro(
                data_inicio, data_fim, analista
            )
            
            # Limpar tabela
            self.historico_table.setRowCount(0)
            
            # Preencher tabela
            for row, proposta in enumerate(propostas):
                self.historico_table.insertRow(row)
                
                # Obter dados dos filtros
                dados_filtro = proposta.get('dados_filtro', {})
                
                # Preencher cada coluna
                colunas = [
                    proposta.get('tipo_proposta', ''),
                    proposta.get('numero_proposta', ''),
                    proposta.get('analista', ''),
                    proposta.get('status', ''),
                    self.formatar_data(proposta.get('data_criacao')),
                    self.formatar_data(proposta.get('data_conclusao')),
                    proposta.get('duracao_total', ''),
                    dados_filtro.get('regiao', ''),
                    dados_filtro.get('convenio', ''),
                    dados_filtro.get('produto', ''),
                    dados_filtro.get('status', ''),
                    dados_filtro.get('cpf', ''),
                    dados_filtro.get('valor_liberado', ''),
                    dados_filtro.get('prazo', ''),
                    dados_filtro.get('observacoes', ''),
                    dados_filtro.get('valor_troco', ''),
                    dados_filtro.get('motivo_recusa_descricao', '')
                ]
                
                for col, valor in enumerate(colunas):
                    item = QTableWidgetItem(str(valor) if valor is not None else '')
                    self.historico_table.setItem(row, col, item)
            
            # Atualizar total
            total = len(propostas)
            if hasattr(self, 'label_total_historico'):
                self.label_total_historico.setText(f"Total: {total} propostas")
            
            print(f"✅ Filtros aplicados: {total} propostas encontradas")
            
        except Exception as e:
            print(f"❌ Erro ao aplicar filtros: {e}")
            import traceback
            traceback.print_exc()

    def formatar_data(self, data):
        """Formata data para exibição"""
        if not data:
            return ''
        
        if isinstance(data, str):
            return data
        
        try:
            if hasattr(data, 'strftime'):
                return data.strftime('%d/%m/%Y %H:%M:%S')
            else:
                return str(data)
        except:
            return str(data)

    def carregar_historico(self):
        """Carrega o histórico inicial"""
        self.aplicar_filtros()

    def exportar_para_xlsx(self):
        """Exporta os dados do histórico para Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Coletar dados da tabela
            dados = []
            colunas = [
                "Tipo", "Número", "Analista", "Status", "Data Criação", "Data Conclusão", "Duração",
                "Região", "Convênio", "Produto", "Status Convênio", 
                "CPF", "Valor Liberado", "Prazo", "Observações", "Valor de Troco", "Motivo de Recusa"
            ]
            
            for row in range(self.historico_table.rowCount()):
                linha = {}
                for col in range(self.historico_table.columnCount()):
                    item = self.historico_table.item(row, col)
                    linha[colunas[col]] = item.text() if item else ''
                dados.append(linha)
            
            if not dados:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Aviso", "Nenhum dado para exportar.")
                return
            
            # Criar DataFrame e exportar
            df = pd.DataFrame(dados)
            data_hoje = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"historico_propostas_{data_hoje}.xlsx"
            
            df.to_excel(filename, index=False, engine='openpyxl')
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Sucesso", f"Dados exportados para: {filename}")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Erro", f"Erro ao exportar dados: {str(e)}")