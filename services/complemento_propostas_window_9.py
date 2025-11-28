from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QMessageBox,
                             QDialog, QListWidget, QListWidgetItem, QDialogButtonBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from datetime import datetime
from utils.motivos_recusa import get_motivos_recusa
import os
import sys

class PropostasWindowPart9:
    """Parte 9 - Métodos de finalização de contratos (aprovação, recusa) e MotivoRecusaDialog"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def verificar_filtros_preenchidos(self, tipo_contrato):
        """Verifica se todos os filtros obrigatórios estão preenchidos, incluindo Valor de Troco quando aplicável"""
        dados_filtro = self.get_dados_filtro_atual(tipo_contrato)
        
        # Verificar se todos os campos obrigatórios estão preenchidos
        regiao_preenchida = bool(dados_filtro.get('regiao', ''))
        convenio_preenchido = bool(dados_filtro.get('convenio', ''))
        produto_preenchido = bool(dados_filtro.get('produto', ''))
        
        # ⭐⭐ VERIFICAR VALOR DE TROCO (obrigatório nas abas Refin e Saque Direcionado)
        troco_preenchido = True  # Por padrão é True (não obrigatório)
        if tipo_contrato in ["Refin", "Saque Direcionado"]:
            troco_valor = dados_filtro.get('valor_troco', '')
            # Verificar se o campo existe, não está vazio e é maior que "0,00"
            troco_preenchido = bool(troco_valor and troco_valor.strip() and troco_valor != "0,00")
            print(f"🔍 Validação Valor de Troco: '{troco_valor}' -> Preenchido: {troco_preenchido}")
        
        todos_preenchidos = regiao_preenchida and convenio_preenchido and produto_preenchido and troco_preenchido
        
        if not todos_preenchidos:
            print("❌ Campos obrigatórios não preenchidos:")
            print(f"   - Região: {'✅' if regiao_preenchida else '❌'} {dados_filtro.get('regiao', 'Não selecionada')}")
            print(f"   - Convênio: {'✅' if convenio_preenchido else '❌'} {dados_filtro.get('convenio', 'Não selecionado')}")
            print(f"   - Produto: {'✅' if produto_preenchido else '❌'} {dados_filtro.get('produto', 'Não selecionado')}")
            if tipo_contrato in ["Refin", "Solicitação Interna"]:
                print(f"   - Valor de Troco: {'✅' if troco_preenchido else '❌'} '{dados_filtro.get('valor_troco', 'Não preenchido')}'")
        
        return todos_preenchidos
    
    def atualizar_tarefa(self, tarefa_key, estado, tipo_contrato):
        self.tarefas_concluidas[tarefa_key] = (estado == Qt.Checked)
        
        # Verificar se TODOS os checkboxes estão marcados E filtros preenchidos
        if self.contrato_em_andamento and tipo_contrato == self.tipo_contrato_atual:
            todas_concluidas = self.verificar_todas_tarefas_concluidas(tipo_contrato)
            filtros_preenchidos = self.verificar_filtros_preenchidos(tipo_contrato)
                       
            # Botão APROVAR: depende de tarefas + filtros
            self.aprovar_buttons[tipo_contrato].setEnabled(todas_concluidas and filtros_preenchidos)
            
            # Botão RECUSAR: depende APENAS de filtros (NUNCA de tarefas)
            self.recusar_buttons[tipo_contrato].setEnabled(filtros_preenchidos)
            
            # Debug
            print(f"🔍 Estado dos botões - {tipo_contrato}:")
            print(f"   - Tarefas concluídas: {todas_concluidas}")
            print(f"   - Filtros preenchidos: {filtros_preenchidos}")
            print(f"   - Aprovar habilitado: {todas_concluidas and filtros_preenchidos}")
            print(f"   - Recusar habilitado: {filtros_preenchidos} (só depende dos filtros)")
    
    def verificar_todas_tarefas_concluidas(self, tipo_contrato):
        """Verifica se todas as tarefas da aba foram concluídas"""
        checkboxes = self.checkboxes_dict.get(tipo_contrato, {})
        return all(checkbox.isChecked() for checkbox in checkboxes.values())
    
    def atualizar_duracao_display(self):
        """Atualiza o display da duração em tempo real - MANTIDO MAS VAZIO PARA OCULTAR NA INTERFACE"""
        pass
    
    def calcular_duracao_total(self):
        """Calcula a duração total quando o contrato é finalizado"""
        if self.data_criacao and self.data_conclusao:
            duracao = self.data_conclusao - self.data_criacao
            horas = duracao.seconds // 3600
            minutos = (duracao.seconds % 3600) // 60
            segundos = duracao.seconds % 60
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        return "00:00:00"
    
    def verificar_estado_reanalise(self, tipo_contrato):
        """Método de debug para verificar o estado da reanálise"""
        print(f"🔍 ESTADO DA REANÁLISE - {tipo_contrato}:")
        print(f"   - Número atual: {self.numero_inputs[tipo_contrato].text()}")
        print(f"   - É reanálise: {self.eh_reanalise}")
        if self.contrato_original:
            print(f"   - Contrato original: {self.contrato_original.get('numero', 'N/A')}")
            print(f"   - ID do original: {self.contrato_original.get('id', 'N/A')}")
        else:
            print(f"   - Contrato original: Nenhum")
        print(f"   - Contrato em andamento: {self.contrato_em_andamento}")    
    

    def finalizar_contrato(self, tipo_contrato, status):
        """Finaliza contrato (para aprovação ou recusa)"""
        try:
            print(f"🎯 INICIANDO FINALIZAÇÃO do contrato - Tipo: {tipo_contrato}, Status: {status}")
            # ⭐⭐ DEBUG: Verificar estado no início
            self.verificar_estado_reanalise(tipo_contrato)
            
            print(f"   🔄 É reanálise: {self.eh_reanalise}")
            
            if self.eh_reanalise and self.contrato_original:
                contrato_original_numero = self.contrato_original.get('numero', '') or self.contrato_original.get('id', '')
                print(f"   📋 Contrato original: {contrato_original_numero}")
            
            if status == "Recusada":
                # Para recusa, usar o método com popup de motivos
                print("🔄 Iniciando processo de RECUSA")
                self.recusar_contrato(tipo_contrato)
            else:
                # Para aprovação, usar o fluxo normal
                print("🔄 Iniciando processo de APROVAÇÃO")
                self.finalizar_contrato_sem_motivo(tipo_contrato, status)
                
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao finalizar contrato: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar contrato: {str(e)}")


    def recusar_contrato(self, tipo_contrato):
        """Abre popup para selecionar motivo da recusa"""
        try:
            print(f"🔍 Validando filtros para RECUSA - {tipo_contrato}")
            
            # Apenas verificar filtros obrigatórios
            if not self.verificar_filtros_preenchidos(tipo_contrato):
                mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
                if tipo_contrato in ["Refin", "Saque Direcionado"]:
                    mensagem_erro += "\n• Valor de Troco"
                mensagem_erro += "\n\nAntes de recusar o contrato."
                
                QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
                return
            
            print("✅ Filtros válidos - abrindo popup de motivos")
            dialog = MotivoRecusaDialog(self)
            dialog.motivo_selecionado.connect(lambda motivo_id, descricao: self.on_motivo_recusa_selecionado(tipo_contrato, motivo_id, descricao))
            dialog.exec_()
            
        except Exception as e:
            print(f"❌ Erro ao recusar contrato: {e}")
            import traceback
            traceback.print_exc()


    def on_motivo_recusa_selecionado(self, tipo_contrato, motivo_id, descricao):
        """Callback quando um motivo de recusa é selecionado"""
        try:
            print(f"🎯 Motivo selecionado: {motivo_id} - {descricao}")
            
            # ⭐⭐ NÃO VALIDAR TAREFAS PARA RECUSA - apenas filtros
            if not self.verificar_filtros_preenchidos(tipo_contrato):
                mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
                if tipo_contrato in ["Refin", "Saque Direcionado"]:
                    mensagem_erro += "\n• Valor de Troco"
                mensagem_erro += "\n\nAntes de recusar o contrato."
                
                QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
                return
            
            # Confirmar recusa com o motivo
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Confirmação de Recusa")
            
            # ⭐⭐ ADICIONAR ÍCONE NA MESSAGE BOX
            try:
                msg_box.setWindowIcon(QIcon(self.resource_path('assets/logo.png')))
            except:
                print("Logo não encontrada para message box")
            
            numero_contrato = self.numero_inputs[tipo_contrato].text().strip()
            msg_box.setText(f"Tem certeza que deseja recusar o contrato {numero_contrato}?\n\n"
                            f"Motivo: {motivo_id} - {descricao}")
            msg_box.setIcon(QMessageBox.Question)

            # ⭐⭐ BOTÕES EM PORTUGUÊS
            btn_sim = msg_box.addButton("Sim", QMessageBox.YesRole)
            btn_nao = msg_box.addButton("Não", QMessageBox.NoRole)

            msg_box.setDefaultButton(btn_nao)

            # Mostrar e verificar resposta
            msg_box.exec_()

            if msg_box.clickedButton() == btn_sim:
                print("✅ Usuário confirmou recusa - finalizando contrato")
                # Finalizar contrato com status "Recusada" e motivo
                self.finalizar_contrato_com_motivo(tipo_contrato, "Recusada", motivo_id, descricao)
            else:
                print("❌ Usuário cancelou recusa")
                
        except Exception as e:
            print(f"❌ Erro ao processar motivo de recusa: {e}")
            import traceback
            traceback.print_exc()


    def finalizar_contrato_com_motivo(self, tipo_contrato, status, motivo_id, motivo_descricao):
        """Finaliza o contrato com motivo específico"""
        try:
            print(f"🎯 FINALIZANDO CONTRATO COM MOTIVO - {tipo_contrato}, Status: {status}")
            
            # ⭐⭐ DEBUG: Verificar estado antes de finalizar
            self.verificar_estado_reanalise(tipo_contrato)
            
            # ⭐⭐ DEBUG EXTRA: Verificar o número ANTES de qualquer processamento
            numero_antes = self.numero_inputs[tipo_contrato].text().strip()
            print(f"🔍 Número ANTES de qualquer processamento: '{numero_antes}'")
            
            # ⭐⭐ VALIDAÇÃO APENAS DOS FILTROS OBRIGATÓRIOS (não valida tarefas para recusa)
            if not self.verificar_filtros_preenchidos(tipo_contrato):
                mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
                if tipo_contrato in ["Refin", "Saque Direcionado"]:
                    mensagem_erro += "\n• Valor de Troco"
                mensagem_erro += "\n\nAntes de finalizar o contrato."
                
                QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
                return
            
            numero = self.numero_inputs[tipo_contrato].text().strip()
            print(f"   📋 Número do contrato: {numero}")
            
            # ⭐⭐ CORREÇÃO: VERIFICAR SE O NÚMERO JÁ TEM O SUFIXO CORRETO
            if self.eh_reanalise and not numero.endswith(('-R1', '-R2', '-R3', '-R4', '-R5')):
                print(f"⚠️  ALERTA: Reanálise ativa mas número não tem sufixo -R: {numero}")
                
                # ⭐⭐ CORREÇÃO: CALCULAR O NÚMERO CORRETO BASEADO NOS CONTRATOS EXISTENTES
                if self.contrato_original:
                    contrato_original_numero = self.contrato_original.get('numero', '') or self.contrato_original.get('id', '')
                    
                    # Buscar contratos existentes para calcular o próximo número
                    contratos_existentes = self.proposta_service.buscar_contratos_por_prefixo(contrato_original_numero, tipo_contrato)
                    
                    maior_reanalise = 0
                    for contrato in contratos_existentes:
                        numero_completo = contrato.get('numero', '')
                        if '-R' in numero_completo:
                            try:
                                partes = numero_completo.split('-R')
                                if len(partes) == 2:
                                    numero_str = ''.join(filter(str.isdigit, partes[1]))
                                    if numero_str:
                                        numero_reanalise = int(numero_str)
                                        if numero_reanalise > maior_reanalise:
                                            maior_reanalise = numero_reanalise
                            except:
                                continue
                    
                    # Calcular próximo número
                    proximo_numero = maior_reanalise + 1
                    novo_numero = f"{contrato_original_numero}-R{proximo_numero}"
                    print(f"🔄 Corrigindo número para reanálise: {novo_numero} (maior encontrado: R{maior_reanalise})")
                    numero = novo_numero
                    
                    # Atualizar o campo visualmente
                    self.numero_inputs[tipo_contrato].blockSignals(True)
                    self.numero_inputs[tipo_contrato].setText(numero)
                    self.numero_inputs[tipo_contrato].blockSignals(False)
                    QApplication.processEvents()
            
            # ⭐⭐ DEBUG: Verificar o número DEPOIS do processamento
            print(f"🔍 Número DEPOIS do processamento: '{numero}'")
            
            # Registrar data de conclusão
            self.data_conclusao = datetime.now()
            
            # Parar timer de duração
            self.timer_duracao.stop()
            
            # Calcular duração total
            duracao_total = self.calcular_duracao_total()
            print(f"   ⏱️  Duração total: {duracao_total}")
            
            # ⭐⭐ REMOVER LÓGICA ANTIGA DE ADICIONAR " - Reanalise" AO TIPO
            # Agora usamos apenas o tipo normal, pois a reanálise é identificada pelo número
            tipo_final = tipo_contrato
                
            # Obter dados dos filtros
            dados_filtro = self.get_dados_filtro_atual(tipo_contrato)
            
            # ⭐⭐ CORRIGIR: Obter o número correto do contrato original
            contrato_original_numero = ""
            if self.contrato_original:
                contrato_original_numero = self.contrato_original.get('numero', '')
                if not contrato_original_numero:
                    contrato_original_numero = self.contrato_original.get('id', '')
            
            # ⭐⭐ ADICIONAR CAMPO PARA IDENTIFICAR SE É REANÁLISE
            if self.eh_reanalise:
                dados_filtro['eh_reanalise'] = True
                dados_filtro['contrato_original'] = contrato_original_numero
                print(f"   🔄 Marcando como REANÁLISE do contrato: {contrato_original_numero}")
            
            # Adicionar motivo da recusa aos dados
            dados_filtro['motivo_recusa_id'] = motivo_id
            dados_filtro['motivo_recusa_descricao'] = motivo_descricao
            
            # Adicionar novos campos
            dados_filtro['cpf'] = self.cpf_inputs.get(tipo_contrato, "").text() if hasattr(self, 'cpf_inputs') and tipo_contrato in self.cpf_inputs else ""
            dados_filtro['valor_liberado'] = self.valor_inputs.get(tipo_contrato, "").text() if hasattr(self, 'valor_inputs') and tipo_contrato in self.valor_inputs else ""
            dados_filtro['moeda'] = "R$"
            dados_filtro['prazo'] = self.prazo_inputs.get(tipo_contrato, "").text() if hasattr(self, 'prazo_inputs') and tipo_contrato in self.prazo_inputs else ""
            dados_filtro['unidade_prazo'] = "Meses"
            dados_filtro['observacoes'] = self.observacoes_inputs.get(tipo_contrato, "").text() if hasattr(self, 'observacoes_inputs') and tipo_contrato in self.observacoes_inputs else ""
            
            # Adicionar Valor de Troco (apenas para Refin e Saque Direcionado)
            if tipo_contrato in ["Refin", "Saque Direcionado"]:
                dados_filtro['valor_troco'] = self.troco_inputs.get(tipo_contrato, "").text() if hasattr(self, 'troco_inputs') and tipo_contrato in self.troco_inputs else ""
                dados_filtro['moeda_troco'] = "R$"
            
            # ⭐⭐ PRINT PARA VERIFICAR O QUE SERÁ ENVIADO PARA O FIREBASE
            print(f"🔥 DADOS QUE SERÃO ENVIADOS PARA O FIREBASE:")
            print(f"   - Tipo: {tipo_final}")
            print(f"   - Número: {numero}")
            print(f"   - É Reanálise: {self.eh_reanalise}")
            print(f"   - Contrato Original: {contrato_original_numero}")
            print(f"   - Valor de Troco: '{dados_filtro.get('valor_troco', 'N/A')}'")
            print(f"   - Status: {status}")
            print(f"   - Motivo Recusa: {motivo_id} - {motivo_descricao}")
            
            # Criar e finalizar contrato incluindo dados dos filtros e motivo
            self.proposta_service.criar_e_finalizar_proposta(
                numero, 
                self.user_data['login'], 
                tipo_final,
                self.tarefas_concluidas,
                status,
                self.data_criacao,
                self.data_conclusao,
                duracao_total,
                dados_filtro,
                self.eh_reanalise,  # ⭐⭐ NOVO PARÂMETRO
                contrato_original_numero  # ⭐⭐ NOVO PARÂMETRO
            )
            
        except Exception as e:
            print(f"❌ ERRO ao finalizar contrato com motivo: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar contrato: {str(e)}")


    def finalizar_contrato_sem_motivo(self, tipo_contrato, status):
        """Finaliza contrato sem motivo (para aprovação)"""
        try:
            print(f"🎯 FINALIZANDO CONTRATO SEM MOTIVO - {tipo_contrato}, Status: {status}")
            
            # ⭐⭐ DEBUG: Verificar estado antes de finalizar
            self.verificar_estado_reanalise(tipo_contrato)
            
            # ⭐⭐ DEBUG EXTRA: Verificar o número ANTES de qualquer processamento
            numero_antes = self.numero_inputs[tipo_contrato].text().strip()
            print(f"🔍 Número ANTES de qualquer processamento: '{numero_antes}'")
            
            # VALIDAÇÃO OBRIGATÓRIA DOS FILTROS (para APROVAR e RECUSAR)
            if not self.verificar_filtros_preenchidos(tipo_contrato):
                mensagem_erro = "Preencha todos os filtros obrigatórios:\n• Região\n• Convênio\n• Produto"
                if tipo_contrato in ["Refin", "Saque Direcionado"]:
                    mensagem_erro += "\n• Valor de Troco"
                mensagem_erro += "\n\nAntes de finalizar o contrato."
                
                QMessageBox.warning(self, "Campos Obrigatórios", mensagem_erro)
                return
            
            numero = self.numero_inputs[tipo_contrato].text().strip()
            print(f"   📋 Número do contrato: {numero}")
            
            # ⭐⭐ CORREÇÃO: VERIFICAR SE O NÚMERO JÁ TEM O SUFIXO CORRETO (APROVAÇÃO TAMBÉM)
            if self.eh_reanalise and not numero.endswith(('-R1', '-R2', '-R3', '-R4', '-R5')):
                print(f"⚠️  ALERTA: Reanálise ativa mas número não tem sufixo -R: {numero}")
                
                # ⭐⭐ CORREÇÃO: CALCULAR O NÚMERO CORRETO BASEADO NOS CONTRATOS EXISTENTES
                if self.contrato_original:
                    contrato_original_numero = self.contrato_original.get('numero', '') or self.contrato_original.get('id', '')
                    
                    # Buscar contratos existentes para calcular o próximo número
                    contratos_existentes = self.proposta_service.buscar_contratos_por_prefixo(contrato_original_numero, tipo_contrato)
                    
                    maior_reanalise = 0
                    for contrato in contratos_existentes:
                        numero_completo = contrato.get('numero', '')
                        if '-R' in numero_completo:
                            try:
                                partes = numero_completo.split('-R')
                                if len(partes) == 2:
                                    numero_str = ''.join(filter(str.isdigit, partes[1]))
                                    if numero_str:
                                        numero_reanalise = int(numero_str)
                                        if numero_reanalise > maior_reanalise:
                                            maior_reanalise = numero_reanalise
                            except:
                                continue
                    
                    # Calcular próximo número
                    proximo_numero = maior_reanalise + 1
                    novo_numero = f"{contrato_original_numero}-R{proximo_numero}"
                    print(f"🔄 Corrigindo número para reanálise: {novo_numero} (maior encontrado: R{maior_reanalise})")
                    numero = novo_numero
                    
                    # Atualizar o campo visualmente
                    self.numero_inputs[tipo_contrato].blockSignals(True)
                    self.numero_inputs[tipo_contrato].setText(numero)
                    self.numero_inputs[tipo_contrato].blockSignals(False)
                    # ⭐⭐ Use a abordagem sem QApplication:
                    self.numero_inputs[tipo_contrato].repaint()
                    self.numero_inputs[tipo_contrato].update()
            
            if status == "Aprovada" and not self.verificar_todas_tarefas_concluidas(tipo_contrato):
                QMessageBox.warning(self, "Atenção", "Todas as tarefas devem ser concluídas para aprovar o contrato!")
                return
            
            # ⭐⭐ DEBUG: Verificar o número DEPOIS do processamento
            print(f"🔍 Número DEPOIS do processamento: '{numero}'")
            
            # Registrar data de conclusão
            self.data_conclusao = datetime.now()
            
            # Parar timer de duração
            self.timer_duracao.stop()
            
            # Calcular duração total
            duracao_total = self.calcular_duracao_total()
            print(f"   ⏱️  Duração total: {duracao_total}")
            
            # ⭐⭐ REMOVER LÓGICA ANTIGA DE ADICIONAR " - Reanalise" AO TIPO
            # Agora usamos apenas o tipo normal, pois a reanálise é identificada pelo número
            tipo_final = tipo_contrato
                    
            # Obter dados dos filtros
            dados_filtro = self.get_dados_filtro_atual(tipo_contrato)
            
            # ⭐⭐ CORRIGIR: Obter o número correto do contrato original
            contrato_original_numero = ""
            if self.contrato_original:
                contrato_original_numero = self.contrato_original.get('numero', '')
                if not contrato_original_numero:
                    contrato_original_numero = self.contrato_original.get('id', '')
            
            # ⭐⭐ ADICIONAR CAMPO PARA IDENTIFICAR SE É REANÁLISE
            if self.eh_reanalise:
                dados_filtro['eh_reanalise'] = True
                dados_filtro['contrato_original'] = contrato_original_numero
                print(f"   🔄 Marcando como REANÁLISE do contrato: {contrato_original_numero}")
            
            # ⭐⭐ ADICIONAR NOVOS CAMPOS AOS DADOS
            dados_filtro['cpf'] = self.cpf_inputs.get(tipo_contrato, "").text() if hasattr(self, 'cpf_inputs') and tipo_contrato in self.cpf_inputs else ""
            dados_filtro['valor_liberado'] = self.valor_inputs.get(tipo_contrato, "").text() if hasattr(self, 'valor_inputs') and tipo_contrato in self.valor_inputs else ""
            dados_filtro['moeda'] = "R$"
            dados_filtro['prazo'] = self.prazo_inputs.get(tipo_contrato, "").text() if hasattr(self, 'prazo_inputs') and tipo_contrato in self.prazo_inputs else ""
            dados_filtro['unidade_prazo'] = "Meses"
            dados_filtro['observacoes'] = self.observacoes_inputs.get(tipo_contrato, "").text() if hasattr(self, 'observacoes_inputs') and tipo_contrato in self.observacoes_inputs else ""
            
            # Adicionar Valor de Troco (apenas para Refin e Saque Direcionado)
            if tipo_contrato in ["Refin", "Saque Direcionado"]:
                dados_filtro['valor_troco'] = self.troco_inputs.get(tipo_contrato, "").text() if hasattr(self, 'troco_inputs') and tipo_contrato in self.troco_inputs else ""
                dados_filtro['moeda_troco'] = "R$"
            
            # ⭐⭐ PRINT PARA VERIFICAR O QUE SERÁ ENVIADO PARA O FIREBASE
            print(f"🔥 DADOS QUE SERÃO ENVIADOS PARA O FIREBASE:")
            print(f"   - Tipo: {tipo_final}")
            print(f"   - Número: {numero}")
            print(f"   - É Reanálise: {self.eh_reanalise}")
            print(f"   - Contrato Original: {contrato_original_numero}")
            print(f"   - Valor de Troco: '{dados_filtro.get('valor_troco', 'N/A')}'")
            print(f"   - Status: {status}")
            
            # Criar e finalizar contrato
            self.proposta_service.criar_e_finalizar_proposta(
                numero, 
                self.user_data['login'], 
                tipo_final,
                self.tarefas_concluidas,
                status,
                self.data_criacao,
                self.data_conclusao,
                duracao_total,
                dados_filtro,
                self.eh_reanalise,  # ⭐⭐ NOVO PARÂMETRO
                contrato_original_numero  # ⭐⭐ NOVO PARÂMETRO
            )
            
        except Exception as e:
            print(f"❌ ERRO ao finalizar contrato sem motivo: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar contrato: {str(e)}")

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