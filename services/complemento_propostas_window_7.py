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

class PropostasWindowPart7:
    """Parte 7 - Métodos de manipulação de filtros (região, convênio, produto)"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
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

        if tipo_proposta in ["Refin", "Solicitação Interna"] and hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
            dados['valor_troco'] = self.troco_inputs[tipo_proposta].text()
            dados['moeda_troco'] = "R$"
        
        return dados