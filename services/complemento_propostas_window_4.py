from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFrame, QCheckBox,
                             QGridLayout, QScrollArea)
import os
import sys

# ⭐⭐ ADICIONAR IMPORT DA FUNÇÃO get_tarefas_por_tipo
from utils.tarefas_fixas import get_tarefas_por_tipo

class PropostasWindowPart4:
    """Parte 4 - Criação de áreas de tarefas e ações"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def criar_area_tarefas(self, tipo_proposta):
        frame = QFrame()
        frame.setObjectName("formFrame")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll.setMinimumHeight(80)  
        scroll.setMaximumHeight(150) 
        
        tarefas_widget = QWidget()
        tarefas_layout = QGridLayout()
        
        # Carregar tarefas específicas do tipo - ⭐⭐ AGORA FUNCIONA
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
        layout.setContentsMargins(8, 4, 8, 4)  
        layout.setSpacing(6)  
        
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
        """Evento chamado quando a janela é redimensionada - CORRIGIDO"""
        # ⭐⭐ REMOVER A CHAMADA SUPER() PROBLEMÁTICA
        # Não chamamos super().resizeEvent(event) aqui porque esta classe
        # não herda diretamente de QWidget
        
        if hasattr(self, 'tabs') and self.tabs.currentWidget():
            current_tab_name = self.tabs.tabText(self.tabs.currentIndex())
            if current_tab_name in ["Saque Fácil", "Refin", "Saque Direcionado"]:
                self.ajustar_altura_tarefas(current_tab_name)

    def ajustar_altura_tarefas(self, tipo_proposta):
        """Ajusta a altura da área de tarefas baseado no tamanho da janela"""
        tab_widget = self.tabs.currentWidget()
        for i in range(tab_widget.layout().count()):
            widget = tab_widget.layout().itemAt(i).widget()
            if isinstance(widget, QFrame) and hasattr(widget, 'layout'):
                for j in range(widget.layout().count()):
                    sub_widget = widget.layout().itemAt(j).widget()
                    if isinstance(sub_widget, QScrollArea):
                        altura = int(self.height() * 0.25)
                        altura = max(100, min(altura, 300))  # Mín: 100, Máx: 300
                        sub_widget.setFixedHeight(altura)
                        break