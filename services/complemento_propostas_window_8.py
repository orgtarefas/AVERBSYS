from PyQt5.QtWidgets import (QMessageBox)
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

    def configurar_proposta_em_andamento(self, numero_contrato, tipo_proposta):
        """Configura o estado quando uma proposta está em andamento"""
        print(f"🔍 Verificando contrato: {numero_contrato} na aba: {tipo_proposta}")
        
        # EXCEÇÃO: Para Solicitação Interna, não verifica se já existe
        if tipo_proposta != "Solicitação Interna":
            try:
                # ⭐⭐ VERIFICAR APENAS NA COLEÇÃO ESPECÍFICA DA ABA ATUAL
                proposta_existente = self.proposta_service.verificar_proposta_existente(numero_contrato, tipo_proposta)
                
                if proposta_existente:
                    print("⚠️ Contrato já existe - mostrando popup reanálise")
                    # Contrato já existe - mostrar popup de reanálise
                    self.mostrar_popup_reanalise(numero_contrato, proposta_existente, tipo_proposta)
                    return
                else:
                    print("✅ Contrato novo - prosseguindo normalmente")
            except Exception as e:
                print(f"❌ Erro ao verificar contrato existente: {e}")
                QMessageBox.warning(self, "Aviso", "Erro ao verificar contrato existente. Prosseguindo como novo contrato.")
        else:
            print("✅ Solicitação Interna - não verifica existência")
            
        print("✅ Configurando proposta em andamento")
        
        # TRAVAR o campo de entrada
        self.numero_inputs[tipo_proposta].setEnabled(False)
        
        # HABILITAR os filtros (já que é um contrato válido)
        self.regiao_combos[tipo_proposta].setEnabled(True)
        print("✅ Filtro de região habilitado")
        
        # Registrar dados internos
        self.data_criacao = datetime.now()
        self.tipo_proposta_atual = tipo_proposta
        self.proposta_em_andamento = True
        
        # Iniciar timer para atualizar duração
        self.timer_duracao.start(1000)
        
        self.data_info_labels[tipo_proposta].setText(
            f"Data/Hora Criação: {self.data_criacao.strftime('%d/%m/%Y %H:%M:%S')}"
        )
        
        # HABILITAR os checkboxes
        for checkbox in self.checkboxes_dict[tipo_proposta].values():
            checkbox.setEnabled(True)
        
        # VALIDAR ESTADO INICIAL DOS BOTÕES
        self.validar_botoes_apos_mudanca_filtro(tipo_proposta)
        
        # TRAVANDO as outras abas
        self.travar_outras_abas(tipo_proposta)
        
        print(f"✅ Proposta em andamento: {tipo_proposta}")