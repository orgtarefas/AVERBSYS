from PyQt5.QtWidgets import (QMessageBox, QApplication)
from PyQt5.QtCore import Qt
import os
import sys
from datetime import datetime

class PropostasWindowPart8:
    """Parte 8 - Métodos de gerenciamento de propostas (criação, limpeza, reanálise)"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    

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
        self.status_labels[tipo_proposta].setStyleSheet("color: #6c757d; font-weight: bold; padding: 5px; background-color: #e2e3e5; border: 1px solid #d6d8db; border-radius: 3px;")
        
        # 3. ⭐⭐ DESABILITAR E LIMPAR NOVOS CAMPOS (incluindo troco)
        if hasattr(self, 'cpf_inputs') and tipo_proposta in self.cpf_inputs:
            self.cpf_inputs[tipo_proposta].clear()
            self.cpf_inputs[tipo_proposta].setEnabled(False)
            self.cpf_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'valor_inputs') and tipo_proposta in self.valor_inputs:
            self.valor_inputs[tipo_proposta].clear()
            self.valor_inputs[tipo_proposta].setEnabled(False)
            self.valor_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'prazo_inputs') and tipo_proposta in self.prazo_inputs:
            self.prazo_inputs[tipo_proposta].clear()
            self.prazo_inputs[tipo_proposta].setEnabled(False)
            self.prazo_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'observacoes_inputs') and tipo_proposta in self.observacoes_inputs:
            self.observacoes_inputs[tipo_proposta].clear()
            self.observacoes_inputs[tipo_proposta].setEnabled(False)
            self.observacoes_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        # ⭐⭐ DESABILITAR E LIMPAR CAMPO DE TROCO (se existir)
        if hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
            self.troco_inputs[tipo_proposta].clear()
            self.troco_inputs[tipo_proposta].setEnabled(False)
            self.troco_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        # 4. Resetar dados internos
        self.data_criacao = None
        self.data_conclusao = None
        self.proposta_em_andamento = False
        self.tarefas_concluidas = {}
        self.eh_reanalise = False
        self.proposta_original = None
        
        # 5. Atualizar interface
        self.data_info_labels[tipo_proposta].setText("Data/Hora Criação: --/--/-- --:--:--")
        
        # ⭐⭐ DESABILITAR FLAGS E BOTÕES que estão no complemento_propostas_window_7.py quando convênio não for Liberado
        self.desabilitar_flags_e_botoes(tipo_proposta)
        
        # 6. Destravar abas
        self.destravar_todas_abas()
            
        print("✅ Contrato completamente limpo - pronto para nova análise")

    def mostrar_popup_reanalise(self, numero_contrato, contrato_existente, tipo_contrato):
        """Mostra popup para reanálise quando contrato já existe"""
        try:
            print(f"🔄 Contrato {numero_contrato} já existe - preparando popup de reanálise")
            
            # ⭐⭐ SALVAR DADOS DO CONTRATO ORIGINAL
            self.contrato_original = contrato_existente
            self.eh_reanalise = True
            
            # ⭐⭐ CALCULAR NÚMERO DA PRÓXIMA REANÁLISE (CORRIGIDO)
            numero_reanalise = self._calcular_proxima_reanalise(numero_contrato, tipo_contrato)
            print(f"🔢 Número calculado para reanálise: {numero_reanalise}")
            
            # Criar popup de confirmação
            from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox
            from PyQt5.QtCore import Qt
            
            class ReanaliseDialog(QDialog):
                def __init__(self, parent=None, numero_contrato="", tipo_contrato="", contrato_existente=None, numero_reanalise=""):
                    super().__init__(parent)
                    self.setWindowTitle("Contrato Já Existente - Reanálise")
                    self.setModal(True)
                    self.resize(500, 350)
                    
                    layout = QVBoxLayout()
                    
                    # Mensagem principal
                    mensagem = QLabel(
                        f"<b>Contrato {numero_contrato} já existe no sistema!</b><br><br>"
                        f"<b>Tipo:</b> {tipo_contrato}<br>"
                        f"<b>Analista Original:</b> {contrato_existente.get('analista', 'N/A')}<br>"
                        f"<b>Status:</b> {contrato_existente.get('status', 'N/A')}<br>"
                        f"<b>Data Criação:</b> {contrato_existente.get('data_criacao', 'N/A')}<br><br>"
                        f"<b>Nova numeração para reanálise:</b><br>"
                        f"<b style='color: #d35400; font-size: 14px;'>{numero_reanalise}</b><br><br>"
                        "Deseja realizar uma <b>REANÁLISE</b> deste contrato?"
                    )
                    mensagem.setWordWrap(True)
                    mensagem.setAlignment(Qt.AlignLeft)
                    layout.addWidget(mensagem)
                    
                    # Checkbox para confirmar reanálise
                    self.checkbox_confirmar = QCheckBox("Confirmar reanálise do contrato existente")
                    self.checkbox_confirmar.setChecked(False)
                    layout.addWidget(self.checkbox_confirmar)
                    
                    # Botões
                    btn_layout = QVBoxLayout()
                    
                    self.btn_reanalise = QPushButton(f"✅ Iniciar Reanálise ({numero_reanalise})")
                    self.btn_reanalise.setEnabled(False)
                    self.btn_reanalise.clicked.connect(self.accept_reanalise)
                    self.btn_reanalise.setFixedHeight(35)
                    
                    self.btn_cancelar = QPushButton("❌ Cancelar")
                    self.btn_cancelar.clicked.connect(self.reject)
                    self.btn_cancelar.setFixedHeight(35)
                    
                    btn_layout.addWidget(self.btn_reanalise)
                    btn_layout.addWidget(self.btn_cancelar)
                    
                    layout.addLayout(btn_layout)
                    self.setLayout(layout)
                    
                    # Conectar checkbox
                    self.checkbox_confirmar.stateChanged.connect(self.on_checkbox_changed)
                    
                    self.resultado = "cancelar"
                    self.numero_reanalise = numero_reanalise
                
                def on_checkbox_changed(self, state):
                    """Habilita botão de reanálise quando checkbox está marcado"""
                    self.btn_reanalise.setEnabled(state == Qt.Checked)
                
                def accept_reanalise(self):
                    """Confirma reanálise"""
                    self.resultado = "reanalise"
                    self.accept()
            
            # Mostrar dialog
            dialog = ReanaliseDialog(
                self, 
                numero_contrato, 
                tipo_contrato, 
                contrato_existente,
                numero_reanalise
            )
            
            resultado = dialog.exec_()
            
            if resultado == QDialog.Accepted:
                if dialog.resultado == "reanalise":
                    print(f"✅ Usuário escolheu REANÁLISE do contrato {numero_contrato} -> {numero_reanalise}")
                    # ⭐⭐ CONFIGURAR COM O NOVO NÚMERO DA REANÁLISE
                    self._configurar_reanalise_contrato(numero_reanalise, contrato_existente, tipo_contrato)
                    return True
                    
            else:
                print(f"❌ Usuário cancelou - contrato {numero_contrato}")
                # Limpar campo de número do contrato
                if tipo_contrato in self.numero_inputs:
                    self.numero_inputs[tipo_contrato].clear()
                    self.numero_inputs[tipo_contrato].setEnabled(True)
                
                self.eh_reanalise = False
                self.contrato_original = None
                return False
                
        except Exception as e:
            print(f"❌ Erro ao mostrar popup de reanálise: {e}")
            import traceback
            traceback.print_exc()
            return False


    def _calcular_proxima_reanalise(self, numero_contrato_original, tipo_contrato):
        """Calcula o próximo número de reanálise usando APENAS 1 LEITURA"""
        try:
            print(f"🔍 Calculando próxima reanálise para: {numero_contrato_original}")
            print(f"🎯 Fazendo APENAS 1 LEITURA no banco...")
            
            # ⭐⭐ APENAS 1 LEITURA - Buscar todos os contratos com o prefixo
            contratos_existentes = self.proposta_service.buscar_contratos_por_prefixo(numero_contrato_original, tipo_contrato)
            
            print(f"📊 Processando {len(contratos_existentes)} contratos localmente...")
            
            # Encontrar o maior número de reanálise LOCALMENTE
            maior_reanalise = 0
            
            for contrato in contratos_existentes:
                numero_completo = contrato.get('numero', '')
                
                # Verificar se é uma reanálise (contém -R seguido de números)
                if '-R' in numero_completo:
                    try:
                        # Extrair o número após -R
                        partes = numero_completo.split('-R')
                        if len(partes) == 2:
                            # Pegar apenas os dígitos após -R
                            numero_str = partes[1]
                            # Remover qualquer caractere não numérico
                            numero_str = ''.join(filter(str.isdigit, numero_str))
                            
                            if numero_str:
                                numero_reanalise = int(numero_str)
                                print(f"   📊 Reanálise encontrada: R{numero_reanalise} - {numero_completo}")
                                
                                if numero_reanalise > maior_reanalise:
                                    maior_reanalise = numero_reanalise
                    except (ValueError, IndexError) as e:
                        print(f"   ⚠️ Erro ao processar {numero_completo}: {e}")
                        continue
            
            # Calcular próximo número
            proximo_numero = maior_reanalise + 1
            novo_numero = f"{numero_contrato_original}-R{proximo_numero}"
            
            print(f"✅ Próxima reanálise: {novo_numero}")
            print(f"🎯 Maior reanálise encontrada: R{maior_reanalise}")
            
            return novo_numero
            
        except Exception as e:
            print(f"❌ Erro ao calcular próxima reanálise: {e}")
            import traceback
            traceback.print_exc()
            # Em caso de erro, retorna a primeira reanálise
            return f"{numero_contrato_original}-R1"


    def _configurar_reanalise_contrato(self, numero_reanalise, contrato_existente, tipo_contrato):
        """Configura o estado para reanálise de contrato existente COM NOVO NÚMERO"""
        try:
            # ⭐⭐ CORREÇÃO: Obter número do contrato original corretamente
            numero_original = contrato_existente.get('numero', '')
            if not numero_original:
                numero_original = contrato_existente.get('id', 'N/A')
            
            print(f"🔄 Configurando REANÁLISE: {numero_original} -> {numero_reanalise}")
            
            # ⭐⭐ VERIFICAR SE O CAMPO ESTÁ SENDO ATUALIZADO CORRETAMENTE
            print(f"🔍 ANTES de atualizar - Número no campo: '{self.numero_inputs[tipo_contrato].text()}'")
            
            # ⭐⭐ CORREÇÃO CRÍTICA: BLOQUEAR SINAIS E FORÇAR ATUALIZAÇÃO
            self.numero_inputs[tipo_contrato].blockSignals(True)  # Bloquear sinais temporariamente
            self.numero_inputs[tipo_contrato].setText(numero_reanalise)
            self.numero_inputs[tipo_contrato].blockSignals(False)  # Liberar sinais
            
            # ⭐⭐ FORÇAR ATUALIZAÇÃO VISUAL
            self.numero_inputs[tipo_contrato].repaint()
            QApplication.processEvents()  # Forçar processamento de eventos Qt
            
            # ⭐⭐ VERIFICAR IMEDIATAMENTE SE ATUALIZOU
            numero_verificado = self.numero_inputs[tipo_contrato].text().strip()
            print(f"🔍 DEPOIS de atualizar - Número no campo: '{numero_verificado}'")
            print(f"🔍 Número esperado: '{numero_reanalise}'")
            
            if numero_verificado != numero_reanalise:
                print(f"❌❌❌ ERRO CRÍTICO: Campo não foi atualizado!")
                print(f"   Esperado: {numero_reanalise}")
                print(f"   Obtido: {numero_verificado}")
                # ⭐⭐ TENTAR FORÇAR NOVAMENTE
                self.numero_inputs[tipo_contrato].setText(numero_reanalise)
                QApplication.processEvents()
                
                # Verificar novamente
                numero_verificado = self.numero_inputs[tipo_contrato].text().strip()
                print(f"🔍 SEGUNDA VERIFICAÇÃO: '{numero_verificado}'")
            
            self.numero_inputs[tipo_contrato].setEnabled(False)
            print(f"✅ Campo de número atualizado para: {numero_reanalise}")
            
            # HABILITAR filtros
            self.regiao_combos[tipo_contrato].setEnabled(True)
            
            # Preencher dados existentes nos filtros (se disponíveis)
            self._preencher_filtros_existentes(contrato_existente, tipo_contrato)
            
            # Preencher checkboxes concluídos anteriormente
            self._preencher_checkboxes_existentes(contrato_existente, tipo_contrato)
            
            # Registrar dados internos
            self.data_criacao = datetime.now()
            self.tipo_contrato_atual = tipo_contrato
            self.contrato_em_andamento = True
            self.eh_reanalise = True
            self.contrato_original = contrato_existente
            
            # Iniciar timer para duração
            self.timer_duracao.start(1000)
            
            # Atualizar display de data
            self.data_info_labels[tipo_contrato].setText(
                f"🔄 REANÁLISE - Data/Hora Início: {self.data_criacao.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
            # HABILITAR checkboxes
            for checkbox in self.checkboxes_dict[tipo_contrato].values():
                checkbox.setEnabled(True)
            
            # Validar estado inicial dos botões
            self.validar_botoes_apos_mudanca_filtro(tipo_contrato)
            
            # Travar outras abas
            self.travar_outras_abas(tipo_contrato)
            
            # ⭐⭐ VERIFICAÇÃO FINAL
            numero_final = self.numero_inputs[tipo_contrato].text().strip()
            print(f"🔍 VERIFICAÇÃO FINAL - Número no campo: '{numero_final}'")
            
            print(f"✅ Reanálise configurada: {tipo_contrato} - Novo número: {numero_reanalise}")
            
        except Exception as e:
            print(f"❌ Erro ao configurar reanálise: {e}")
            import traceback
            traceback.print_exc()



    def _preencher_filtros_existentes(self, contrato_existente, tipo_contrato):
        """Preenche os filtros com dados do contrato existente"""
        try:
            dados_filtro = contrato_existente.get('dados_filtro', {})
            
            print(f"📋 Preenchendo filtros com dados existentes: {dados_filtro}")
            
            # Preencher região
            if 'regiao' in dados_filtro and dados_filtro['regiao']:
                regiao = dados_filtro['regiao']
                regiao_combo = self.regiao_combos.get(tipo_contrato)
                if regiao_combo:
                    index = regiao_combo.findText(regiao)
                    if index >= 0:
                        regiao_combo.setCurrentIndex(index)
                        print(f"   ✅ Região preenchida: {regiao}")
            
            # Preencher convênio
            if 'convenio' in dados_filtro and dados_filtro['convenio']:
                convenio = dados_filtro['convenio']
                convenio_combo = self.convenio_combos.get(tipo_contrato)
                if convenio_combo:
                    # Aguardar um pouco para o combobox de região processar
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(100, lambda: self._preencher_convenio_delay(convenio, tipo_contrato))
            
            # Preencher produto
            if 'produto' in dados_filtro and dados_filtro['produto']:
                produto = dados_filtro['produto']
                produto_combo = self.produto_combos.get(tipo_contrato)
                if produto_combo:
                    index = produto_combo.findText(produto)
                    if index >= 0:
                        produto_combo.setCurrentIndex(index)
                        print(f"   ✅ Produto preenchido: {produto}")
                        
        except Exception as e:
            print(f"❌ Erro ao preencher filtros existentes: {e}")

    def _preencher_convenio_delay(self, convenio, tipo_contrato):
        """Preenche o convênio com delay para garantir que os dados estão carregados"""
        try:
            convenio_combo = self.convenio_combos.get(tipo_contrato)
            if convenio_combo:
                index = convenio_combo.findText(convenio)
                if index >= 0:
                    convenio_combo.setCurrentIndex(index)
                    print(f"   ✅ Convênio preenchido: {convenio}")
        except Exception as e:
            print(f"❌ Erro ao preencher convênio com delay: {e}")

    def _preencher_checkboxes_existentes(self, contrato_existente, tipo_contrato):
        """Preenche os checkboxes com o estado anterior do contrato"""
        try:
            tarefas_concluidas = contrato_existente.get('tarefas_concluidas', {})
            print(f"📋 Preenchendo checkboxes com estado anterior: {tarefas_concluidas}")
            
            if tipo_contrato in self.checkboxes_dict:
                for tarefa_nome, checkbox in self.checkboxes_dict[tipo_contrato].items():
                    if tarefa_nome in tarefas_concluidas:
                        checkbox.setChecked(bool(tarefas_concluidas[tarefa_nome]))
                        print(f"   ✅ Checkbox {tarefa_nome}: {tarefas_concluidas[tarefa_nome]}")
                        
        except Exception as e:
            print(f"❌ Erro ao preencher checkboxes existentes: {e}")

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


    def configurar_contrato_em_andamento(self, numero_contrato, tipo_contrato):
        """Configura o estado quando um contrato está em andamento"""
        print(f"🔍 Verificando contrato: {numero_contrato} na aba: {tipo_contrato}")
        
        if tipo_contrato != "Solicitação Interna":
            try:
                # ⭐⭐ VERIFICAR APENAS NA COLEÇÃO ESPECÍFICA DA ABA ATUAL
                contrato_existente = self.proposta_service.verificar_contrato_existente(numero_contrato, tipo_contrato)
                
                if contrato_existente:
                    print("⚠️ Contrato já existe - mostrando popup reanálise")
                    # Contrato já existe - mostrar popup de reanálise
                    self.mostrar_popup_reanalise(numero_contrato, contrato_existente, tipo_contrato)
                    return False
                else:
                    print("✅ Contrato novo - prosseguindo normalmente")
                    # ⭐⭐ CONFIGURAR CONTRATO NOVO
                    self._configurar_contrato_novo(numero_contrato, tipo_contrato)
                    return True
                    
            except Exception as e:
                print(f"❌ Erro ao verificar contrato existente: {e}")
                # Em caso de erro, configurar como novo contrato
                self._configurar_contrato_novo(numero_contrato, tipo_contrato)
                return True
        else:
            print("✅ Solicitação Interna - não verifica existência")
            # ⭐⭐ SOLICITAÇÃO INTERNA SEMPRE CONFIGURA COMO NOVO
            self._configurar_contrato_novo(numero_contrato, tipo_contrato)
            return True

    def _configurar_contrato_novo(self, numero_contrato, tipo_contrato):
        """Configura o estado para um contrato novo"""
        print("✅ Configurando contrato em andamento")
        
        # TRAVAR o campo de entrada
        self.numero_inputs[tipo_contrato].setEnabled(False)
        
        # HABILITAR os filtros (já que é um contrato válido)
        self.regiao_combos[tipo_contrato].setEnabled(True)
        print("✅ Filtro de região habilitado")
        
        # Registrar dados internos
        self.data_criacao = datetime.now()
        self.tipo_contrato_atual = tipo_contrato
        self.contrato_em_andamento = True
        
        # Iniciar timer para atualizar duração
        self.timer_duracao.start(1000)
        
        self.data_info_labels[tipo_contrato].setText(
            f"Data/Hora Criação: {self.data_criacao.strftime('%d/%m/%Y %H:%M:%S')}"
        )
        
        # HABILITAR os checkboxes
        for checkbox in self.checkboxes_dict[tipo_contrato].values():
            checkbox.setEnabled(True)
        
        # VALIDAR ESTADO INICIAL DOS BOTÕES
        self.validar_botoes_apos_mudanca_filtro(tipo_contrato)
        
        # TRAVANDO as outras abas
        self.travar_outras_abas(tipo_contrato)
        
        print(f"✅ Contrato em andamento: {tipo_contrato}")