import os
import sys

class PropostasWindowPart7:
    """Parte 7 - Métodos de manipulação de filtros (região, convênio, produto)"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def on_regiao_selecionada(self, tipo_contrato):
        """Quando uma região é selecionada, carrega os convênios correspondentes"""
        regiao_combo = self.regiao_combos[tipo_contrato]
        convenio_combo = self.convenio_combos[tipo_contrato]
        produto_combo = self.produto_combos[tipo_contrato]
        status_label = self.status_labels[tipo_contrato]
        
        # Limpar dependências
        convenio_combo.clear()
        convenio_combo.addItem("Selecione um convênio", "")
        produto_combo.clear()
        produto_combo.addItem("Selecione um produto", "")
        status_label.setText("Não selecionado")
        status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        # ⭐⭐ DESABILITAR CAMPOS ADICIONAIS (já que produto foi limpo)
        self.desabilitar_campos_adicionais(tipo_contrato)
        
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
        self.validar_botoes_apos_mudanca_filtro(tipo_contrato)

    def on_convenio_selecionado(self, tipo_contrato):
        """Quando um convênio é selecionado, carrega produtos e já verifica o status"""
        convenio_combo = self.convenio_combos[tipo_contrato]
        produto_combo = self.produto_combos[tipo_contrato]
        status_label = self.status_labels[tipo_contrato]
        
        convenio_selecionado = convenio_combo.currentData()
        
        if convenio_selecionado:
            # ⭐⭐ VERIFICAR STATUS DO CONVÊNIO IMEDIATAMENTE
            status = self.google_sheets_service.get_status_por_convenio(convenio_selecionado)
            
            # Atualizar status label
            if status and status.strip().lower() == 'liberado':
                status_label.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 3px;")
            else:
                status_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 3px;")
                # ⭐⭐ DESABILITAR FLAGS E BOTÃO RECUSAR SE NÃO FOR LIBERADO
                self.desabilitar_flags_e_botoes(tipo_contrato)
            
            status_label.setText(status)
            
            # Carregar produtos para este convênio
            produtos = self.google_sheets_service.get_produtos_por_convenio(convenio_selecionado)
            
            produto_combo.clear()
            produto_combo.setEnabled(True)
            produto_combo.addItem("Selecione um produto", "")
            
            for produto in produtos:
                produto_combo.addItem(produto, produto)
            
            print(f"✅ Produtos carregados para convênio '{convenio_selecionado}': {len(produtos)} produtos")
        else:
            produto_combo.clear()
            produto_combo.setEnabled(False)
            produto_combo.addItem("Selecione um produto", "")
            status_label.setText("Não selecionado")
            status_label.setStyleSheet("color: #6c757d; font-weight: bold; padding: 5px; background-color: #e2e3e5; border: 1px solid #d6d8db; border-radius: 3px;")
            # ⭐⭐ DESABILITAR FLAGS E BOTÃO RECUSAR
            self.desabilitar_flags_e_botoes(tipo_contrato)

    def on_produto_selecionado(self, tipo_contrato):
        """Quando um produto é selecionado, mostra o status correspondente E controla campos adicionais"""
        produto_combo = self.produto_combos[tipo_contrato]
        convenio_combo = self.convenio_combos[tipo_contrato]
        status_label = self.status_labels[tipo_contrato]
        
        produto_selecionado = produto_combo.currentData()
        convenio_selecionado = convenio_combo.currentData()
        
        if produto_selecionado and convenio_selecionado:
            # ⭐⭐ AGORA VERIFICAMOS O STATUS PELO CONVÊNIO, NÃO PELO PRODUTO
            status = self.google_sheets_service.get_status_por_convenio(convenio_selecionado)
            
            # ⭐⭐ DEBUG: Mostrar informações detalhadas
            print(f"🔍 Convênio: '{convenio_selecionado}' | Produto: '{produto_selecionado}' | Status retornado: '{status}'")
            
            # ⭐⭐ MODIFICAÇÃO: Verificar se o status é EXATAMENTE "Liberado" (case insensitive)
            if status and status.strip().lower() == 'liberado':
                # Status Liberado - Verde e campos habilitados
                status_label.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 3px;")
                
                # ⭐⭐ LIBERAR CAMPOS ADICIONAIS APÓS SELECIONAR PRODUTO COM STATUS LIBERADO
                self.liberar_campos_adicionais(tipo_contrato)
                # ⭐⭐ LIBERAR FLAGS E BOTÃO RECUSAR
                self.liberar_flags_e_botoes(tipo_contrato)
                print(f"✅ Status 'Liberado' - Todos os campos habilitados para {tipo_contrato}")
                
            else:
                # Status NÃO Liberado - Vermelho e campos desabilitados
                status_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 3px;")
                
                # ⭐⭐ DESABILITAR CAMPOS ADICIONAIS SE STATUS NÃO FOR LIBERADO
                self.desabilitar_campos_adicionais(tipo_contrato)
                # ⭐⭐ DESABILITAR FLAGS E BOTÃO RECUSAR
                self.desabilitar_flags_e_botoes(tipo_contrato)
                print(f"❌ Status '{status}' - Todos os campos desabilitados para {tipo_contrato}")
            
            status_label.setText(status)
        else:
            # Nenhum produto ou convênio selecionado - Estado neutro
            status_label.setText("Não selecionado")
            status_label.setStyleSheet("color: #6c757d; font-weight: bold; padding: 5px; background-color: #e2e3e5; border: 1px solid #d6d8db; border-radius: 3px;")
            
            # ⭐⭐ DESABILITAR CAMPOS ADICIONAIS SE PRODUTO/CONVÊNIO NÃO SELECIONADO
            self.desabilitar_campos_adicionais(tipo_contrato)
            self.desabilitar_flags_e_botoes(tipo_contrato)
            #print(f"ℹ️  Produto ou convênio não selecionado - Todos os campos desabilitados para {tipo_contrato}")
        
        # Validar estado dos botões após mudança
        self.validar_botoes_apos_mudanca_filtro(tipo_contrato)

    def liberar_flags_e_botoes(self, tipo_contrato):
        """Habilita os campos de FLAG e botão Recusar quando status é Liberado"""
        # ⭐⭐ HABILITAR CHECKBOXES (FLAGS)
        if tipo_contrato in self.checkboxes_dict:
            for checkbox in self.checkboxes_dict[tipo_contrato].values():
                checkbox.setEnabled(True)
        
        # ⭐⭐ HABILITAR BOTÃO RECUSAR
        if tipo_contrato in self.recusar_buttons:
            self.recusar_buttons[tipo_contrato].setEnabled(True)
        
        print(f"✅ Flags e botão Recusar habilitados para {tipo_contrato}")

    def desabilitar_flags_e_botoes(self, tipo_contrato):
        """Desabilita os campos de FLAG e botão Recusar quando status NÃO é Liberado"""
        # ⭐⭐ DESABILITAR CHECKBOXES (FLAGS)
        if tipo_contrato in self.checkboxes_dict:
            for checkbox in self.checkboxes_dict[tipo_contrato].values():
                checkbox.setEnabled(False)
                checkbox.setChecked(False)  # ⭐⭐ TAMBÉM DESMARCAR OS CHECKBOXES
        
        # ⭐⭐ DESABILITAR BOTÃO RECUSAR
        if tipo_contrato in self.recusar_buttons:
            self.recusar_buttons[tipo_contrato].setEnabled(False)
        
        #print(f"❌ Flags e botão Recusar desabilitados para {tipo_contrato}")

    def liberar_campos_adicionais(self, tipo_contrato):
        """Libera campos adicionais (Troco, CPF, Valor, Prazo, Observações) após selecionar produto"""
        # ⭐⭐ LIBERAR VALOR DE TROCO (apenas para Refin, Saque Direcionado e Solicitação Interna)
        if tipo_contrato in ["Refin", "Saque Direcionado", "Solicitação Interna"] and hasattr(self, 'troco_inputs') and tipo_contrato in self.troco_inputs:
            self.troco_inputs[tipo_contrato].setEnabled(True)
            self.troco_inputs[tipo_contrato].setPlaceholderText("Digite o valor do troco")
            print(f"✅ Campo de Troco liberado para {tipo_contrato}")
        
        # ⭐⭐ LIBERAR CAMPOS GERAIS (CPF, Valor, Prazo, Observações)
        if hasattr(self, 'cpf_inputs') and tipo_contrato in self.cpf_inputs:
            self.cpf_inputs[tipo_contrato].setEnabled(True)
            self.cpf_inputs[tipo_contrato].setPlaceholderText("Digite o CPF")
        
        if hasattr(self, 'valor_inputs') and tipo_contrato in self.valor_inputs:
            self.valor_inputs[tipo_contrato].setEnabled(True)
            self.valor_inputs[tipo_contrato].setPlaceholderText("Digite o valor liberado")
        
        if hasattr(self, 'prazo_inputs') and tipo_contrato in self.prazo_inputs:
            self.prazo_inputs[tipo_contrato].setEnabled(True)
            self.prazo_inputs[tipo_contrato].setPlaceholderText("Digite o prazo")
        
        if hasattr(self, 'observacoes_inputs') and tipo_contrato in self.observacoes_inputs:
            self.observacoes_inputs[tipo_contrato].setEnabled(True)
            self.observacoes_inputs[tipo_contrato].setPlaceholderText("Digite observações")

    def desabilitar_campos_adicionais(self, tipo_contrato):
        """Desabilita campos adicionais quando produto não está selecionado"""
        # ⭐⭐ DESABILITAR VALOR DE TROCO
        if tipo_contrato in ["Refin", "Saque Direcionado", "Solicitação Interna"] and hasattr(self, 'troco_inputs') and tipo_contrato in self.troco_inputs:
            self.troco_inputs[tipo_contrato].setEnabled(False)
            self.troco_inputs[tipo_contrato].setText("")
            self.troco_inputs[tipo_contrato].setPlaceholderText("Selecione o produto primeiro")
        
        # ⭐⭐ DESABILITAR CAMPOS GERAIS
        if hasattr(self, 'cpf_inputs') and tipo_contrato in self.cpf_inputs:
            self.cpf_inputs[tipo_contrato].setEnabled(False)
            self.cpf_inputs[tipo_contrato].setText("")
            self.cpf_inputs[tipo_contrato].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'valor_inputs') and tipo_contrato in self.valor_inputs:
            self.valor_inputs[tipo_contrato].setEnabled(False)
            self.valor_inputs[tipo_contrato].setText("")
            self.valor_inputs[tipo_contrato].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'prazo_inputs') and tipo_contrato in self.prazo_inputs:
            self.prazo_inputs[tipo_contrato].setEnabled(False)
            self.prazo_inputs[tipo_contrato].setText("")
            self.prazo_inputs[tipo_contrato].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'observacoes_inputs') and tipo_contrato in self.observacoes_inputs:
            self.observacoes_inputs[tipo_contrato].setEnabled(False)
            self.observacoes_inputs[tipo_contrato].setText("")
            self.observacoes_inputs[tipo_contrato].setPlaceholderText("Selecione o produto primeiro")

    def validar_botoes_apos_mudanca_filtro(self, tipo_contrato):
        """Valida o estado dos botões após mudança nos filtros"""
        if self.contrato_em_andamento and tipo_contrato == self.tipo_contrato_atual:
            todas_concluidas = self.verificar_todas_tarefas_concluidas(tipo_contrato)
            filtros_preenchidos = self.verificar_filtros_preenchidos(tipo_contrato)
            
            # ⭐⭐ VERIFICAR SE O CONVÊNIO ESTÁ COM STATUS "LIBERADO"
            status_liberado = False
            convenio_combo = self.convenio_combos.get(tipo_contrato)
            if convenio_combo and convenio_combo.currentData():
                status = self.google_sheets_service.get_status_por_convenio(convenio_combo.currentData())
                status_liberado = status and status.strip().lower() == 'liberado'
            
            # ⭐⭐ VERIFICAR SE VALOR DE TROCO FOI PREENCHIDO (para habilitar flags)
            troco_preenchido = True
            if tipo_contrato in ["Refin", "Saque Direcionado", "Solicitação Interna"]:
                if hasattr(self, 'troco_inputs') and tipo_contrato in self.troco_inputs:
                    valor_troco = self.troco_inputs[tipo_contrato].text().strip()
                    troco_preenchido = bool(valor_troco and valor_troco != "0,00")
            
            # ⭐⭐ HABILITAR/DESABILITAR FLAGS BASEADO NO TROCO E STATUS
            if hasattr(self, 'checkboxes_dict') and tipo_contrato in self.checkboxes_dict:
                for checkbox in self.checkboxes_dict[tipo_contrato].values():
                    checkbox.setEnabled(troco_preenchido and status_liberado)
            
            # ⭐⭐ HABILITAR BOTÕES APENAS SE STATUS FOR LIBERADO
            self.aprovar_buttons[tipo_contrato].setEnabled(todas_concluidas and filtros_preenchidos and status_liberado)
            self.recusar_buttons[tipo_contrato].setEnabled(filtros_preenchidos and status_liberado)
            
            #print(f"🔍 Validação após filtro - {tipo_contrato}:")
            print(f"   - Status Liberado: {status_liberado}")
            print(f"   - Troco preenchido: {troco_preenchido}")
            print(f"   - Flags habilitados: {troco_preenchido and status_liberado}")
            print(f"   - Recusar habilitado: {filtros_preenchidos and status_liberado}")
            print(f"   - Aprovar habilitado: {todas_concluidas and filtros_preenchidos and status_liberado}")
        else:
            # ⭐⭐ SE NÃO HÁ CONTRATO EM ANDAMENTO, DESABILITAR TUDO
            if hasattr(self, 'checkboxes_dict') and tipo_contrato in self.checkboxes_dict:
                for checkbox in self.checkboxes_dict[tipo_contrato].values():
                    checkbox.setEnabled(False)
            
            if hasattr(self, 'aprovar_buttons') and tipo_contrato in self.aprovar_buttons:
                self.aprovar_buttons[tipo_contrato].setEnabled(False)
            
            if hasattr(self, 'recusar_buttons') and tipo_contrato in self.recusar_buttons:
                self.recusar_buttons[tipo_contrato].setEnabled(False)
            
            #print(f"🔍 Validação após filtro - {tipo_contrato}: Sem contrato em andamento - tudo desabilitado")

    def validar_apos_troco(self, text, tipo_contrato):
        """Valida os flags após digitar no campo de troco"""
        print(f"💰 Digitando no Troco ({tipo_contrato}): '{text}'")
        
        # ⭐⭐ VERIFICAR SE TROCO FOI PREENCHIDO
        troco_preenchido = bool(text.strip() and text != "0,00")
        
        # ⭐⭐ HABILITAR/DESABILITAR FLAGS BASEADO NO TROCO
        if hasattr(self, 'checkboxes_dict') and tipo_contrato in self.checkboxes_dict:
            for checkbox in self.checkboxes_dict[tipo_contrato].values():
                checkbox.setEnabled(troco_preenchido)
        
        print(f"   → Flags habilitados: {troco_preenchido}")
        
        # Validar estado dos botões após digitar no troco
        if hasattr(self, 'validar_botoes_apos_mudanca_filtro'):
            self.validar_botoes_apos_mudanca_filtro(tipo_contrato)            

    def get_dados_filtro_atual(self, tipo_contrato):
        """Retorna os dados atualmente selecionados nos filtros E novos campos"""
        dados = {
            'regiao': self.regiao_combos[tipo_contrato].currentData(),
            'convenio': self.convenio_combos[tipo_contrato].currentData(),
            'produto': self.produto_combos[tipo_contrato].currentData(),
            'status': self.status_labels[tipo_contrato].text()
        }

        if hasattr(self, 'cpf_inputs') and tipo_contrato in self.cpf_inputs:
            dados['cpf'] = self.cpf_inputs[tipo_contrato].text()
        
        if hasattr(self, 'valor_inputs') and tipo_contrato in self.valor_inputs:
            dados['valor_liberado'] = self.valor_inputs[tipo_contrato].text()
            dados['moeda'] = "R$"
        
        if hasattr(self, 'prazo_inputs') and tipo_contrato in self.prazo_inputs:
            dados['prazo'] = self.prazo_inputs[tipo_contrato].text()
            dados['unidade_prazo'] = "Meses"
        
        if hasattr(self, 'observacoes_inputs') and tipo_contrato in self.observacoes_inputs:
            dados['observacoes'] = self.observacoes_inputs[tipo_contrato].text()

        if tipo_contrato in ["Refin", "Saque Direcionado"] and hasattr(self, 'troco_inputs') and tipo_contrato in self.troco_inputs:
            valor_troco = self.troco_inputs[tipo_contrato].text().strip()
            
            # ⭐⭐ PRINT DO VALOR DIGITADO
            print(f"🔍 Valor de Troco Digitado ({tipo_contrato}): '{valor_troco}'")
            
            # ⭐⭐ VALIDAÇÃO E FORMATAÇÃO (SÓ SE TIVER VALOR DIGITADO)
            if valor_troco:
                # Remover pontos e outros caracteres não numéricos, exceto vírgula
                valor_limpo = ''.join(c for c in valor_troco if c.isdigit() or c == ',')
                
                # Garantir formatação básica
                if valor_limpo:
                    # Se não tiver vírgula, adicionar ",00"
                    if ',' not in valor_limpo:
                        valor_formatado = valor_limpo + ",00"
                    else:
                        # Garantir que tenha exatamente 2 dígitos decimais
                        partes = valor_limpo.split(',')
                        parte_inteira = partes[0] if partes[0] else "0"
                        parte_decimal = partes[1] if len(partes) > 1 else "00"
                        
                        # Completar com zeros se necessário
                        parte_decimal = parte_decimal.ljust(2, '0')
                        valor_formatado = parte_inteira + "," + parte_decimal
                    
                    # ⭐⭐ PRINT DO VALOR AJUSTADO
                    print(f"✅ Valor de Troco Ajustado ({tipo_contrato}): '{valor_formatado}'")
                    
                    # ⭐⭐ ATUALIZAR O CAMPO VISUALMENTE
                    self.troco_inputs[tipo_contrato].blockSignals(True)
                    self.troco_inputs[tipo_contrato].setText(valor_formatado)
                    self.troco_inputs[tipo_contrato].blockSignals(False)
                    
                    # ⭐⭐ SALVAR O VALOR FORMATADO
                    dados['valor_troco'] = valor_formatado
                else:
                    # Se depois da limpeza ficou vazio, não salva
                    dados['valor_troco'] = ""
            else:
                # Campo vazio - não salva "0,00"
                dados['valor_troco'] = ""
            
            dados['moeda_troco'] = "R$" if dados.get('valor_troco') else ""
        
        return dados