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

# ⭐⭐ ADICIONAR IMPORTS NECESSÁRIOS
from utils.motivos_recusa import get_motivos_recusa

class PropostasWindowPart9:
    """Parte 9 - Métodos de finalização de propostas (aprovação, recusa) e MotivoRecusaDialog"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
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
    
    def atualizar_duracao_display(self):
        """Atualiza o display da duração em tempo real - MANTIDO MAS VAZIO PARA OCULTAR NA INTERFACE"""
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
        msg_box = QMessageBox()
        msg_box.setWindowTitle(" ")
        
        # ⭐⭐ ADICIONAR ÍCONE NA MESSAGE BOX
        try:
            msg_box.setWindowIcon(QIcon(self.resource_path('assets/logo.png')))
        except:
            print("Logo não encontrada para message box")
        
        msg_box.setText(f"Tem certeza que deseja recusar a proposta?\n\n"
                        f"Motivo: {motivo_id} - {descricao}")
        msg_box.setIcon(QMessageBox.Question)

        # ⭐⭐ BOTÕES EM PORTUGUÊS
        btn_sim = msg_box.addButton("Sim", QMessageBox.YesRole)
        btn_nao = msg_box.addButton("Não", QMessageBox.NoRole)

        msg_box.setDefaultButton(btn_nao)

        # Mostrar e verificar resposta
        msg_box.exec_()

        if msg_box.clickedButton() == btn_sim:
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

# ⭐⭐ CLASSE MotivoRecusaDialog DENTRO DO MESMO ARQUIVO
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