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
        
        # ⭐⭐ DESABILITAR CAMPOS ADICIONAIS (já que produto foi limpo)
        self.desabilitar_campos_adicionais(tipo_proposta)
        
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
        """Quando um produto é selecionado, mostra o status correspondente E libera campos adicionais"""
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
            
            # ⭐⭐ LIBERAR CAMPOS ADICIONAIS APÓS SELECIONAR PRODUTO
            self.liberar_campos_adicionais(tipo_proposta)
        else:
            status_label.setText("Não selecionado")
            status_label.setStyleSheet("font-weight: bold; padding: 5px;")
            
            # ⭐⭐ DESABILITAR CAMPOS ADICIONAIS SE PRODUTO NÃO SELECIONADO
            self.desabilitar_campos_adicionais(tipo_proposta)
        
        # Validar estado dos botões após mudança
        self.validar_botoes_apos_mudanca_filtro(tipo_proposta)

    def liberar_campos_adicionais(self, tipo_proposta):
        """Libera campos adicionais (Troco, CPF, Valor, Prazo, Observações) após selecionar produto"""
        # ⭐⭐ LIBERAR VALOR DE TROCO (apenas para Refin, Saque Direcionado e Solicitação Interna)
        if tipo_proposta in ["Refin", "Saque Direcionado", "Solicitação Interna"] and hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
            self.troco_inputs[tipo_proposta].setEnabled(True)
            self.troco_inputs[tipo_proposta].setPlaceholderText("Digite o valor do troco")
            print(f"✅ Campo de Troco liberado para {tipo_proposta}")
        
        # ⭐⭐ LIBERAR CAMPOS GERAIS (CPF, Valor, Prazo, Observações)
        if hasattr(self, 'cpf_inputs') and tipo_proposta in self.cpf_inputs:
            self.cpf_inputs[tipo_proposta].setEnabled(True)
            self.cpf_inputs[tipo_proposta].setPlaceholderText("Digite o CPF")
        
        if hasattr(self, 'valor_inputs') and tipo_proposta in self.valor_inputs:
            self.valor_inputs[tipo_proposta].setEnabled(True)
            self.valor_inputs[tipo_proposta].setPlaceholderText("Digite o valor liberado")
        
        if hasattr(self, 'prazo_inputs') and tipo_proposta in self.prazo_inputs:
            self.prazo_inputs[tipo_proposta].setEnabled(True)
            self.prazo_inputs[tipo_proposta].setPlaceholderText("Digite o prazo")
        
        if hasattr(self, 'observacoes_inputs') and tipo_proposta in self.observacoes_inputs:
            self.observacoes_inputs[tipo_proposta].setEnabled(True)
            self.observacoes_inputs[tipo_proposta].setPlaceholderText("Digite observações")

    def desabilitar_campos_adicionais(self, tipo_proposta):
        """Desabilita campos adicionais quando produto não está selecionado"""
        # ⭐⭐ DESABILITAR VALOR DE TROCO
        if tipo_proposta in ["Refin", "Saque Direcionado", "Solicitação Interna"] and hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
            self.troco_inputs[tipo_proposta].setEnabled(False)
            self.troco_inputs[tipo_proposta].setText("")
            self.troco_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        # ⭐⭐ DESABILITAR CAMPOS GERAIS
        if hasattr(self, 'cpf_inputs') and tipo_proposta in self.cpf_inputs:
            self.cpf_inputs[tipo_proposta].setEnabled(False)
            self.cpf_inputs[tipo_proposta].setText("")
            self.cpf_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'valor_inputs') and tipo_proposta in self.valor_inputs:
            self.valor_inputs[tipo_proposta].setEnabled(False)
            self.valor_inputs[tipo_proposta].setText("")
            self.valor_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'prazo_inputs') and tipo_proposta in self.prazo_inputs:
            self.prazo_inputs[tipo_proposta].setEnabled(False)
            self.prazo_inputs[tipo_proposta].setText("")
            self.prazo_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")
        
        if hasattr(self, 'observacoes_inputs') and tipo_proposta in self.observacoes_inputs:
            self.observacoes_inputs[tipo_proposta].setEnabled(False)
            self.observacoes_inputs[tipo_proposta].setText("")
            self.observacoes_inputs[tipo_proposta].setPlaceholderText("Selecione o produto primeiro")

    def validar_botoes_apos_mudanca_filtro(self, tipo_proposta):
        """Valida o estado dos botões após mudança nos filtros"""
        if self.proposta_em_andamento and tipo_proposta == self.tipo_proposta_atual:
            todas_concluidas = self.verificar_todas_tarefas_concluidas(tipo_proposta)
            filtros_preenchidos = self.verificar_filtros_preenchidos(tipo_proposta)
            
            # ⭐⭐ VERIFICAR SE VALOR DE TROCO FOI PREENCHIDO (para habilitar flags)
            troco_preenchido = True
            if tipo_proposta in ["Refin", "Saque Direcionado", "Solicitação Interna"]:
                if hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
                    valor_troco = self.troco_inputs[tipo_proposta].text().strip()
                    troco_preenchido = bool(valor_troco and valor_troco != "0,00")
            
            # ⭐⭐ HABILITAR/DESABILITAR FLAGS BASEADO NO TROCO
            if hasattr(self, 'checkboxes_dict') and tipo_proposta in self.checkboxes_dict:
                for checkbox in self.checkboxes_dict[tipo_proposta].values():
                    checkbox.setEnabled(troco_preenchido)
            
            self.aprovar_buttons[tipo_proposta].setEnabled(todas_concluidas and filtros_preenchidos)
            self.recusar_buttons[tipo_proposta].setEnabled(filtros_preenchidos)
            
            print(f"🔍 Validação após filtro - {tipo_proposta}:")
            print(f"   - Troco preenchido: {troco_preenchido}")
            print(f"   - Flags habilitados: {troco_preenchido}")
            print(f"   - Recusar habilitado: {filtros_preenchidos}")

    def validar_apos_troco(self, text, tipo_proposta):
        """Valida os flags após digitar no campo de troco"""
        print(f"💰 Digitando no Troco ({tipo_proposta}): '{text}'")
        
        # ⭐⭐ VERIFICAR SE TROCO FOI PREENCHIDO
        troco_preenchido = bool(text.strip() and text != "0,00")
        
        # ⭐⭐ HABILITAR/DESABILITAR FLAGS BASEADO NO TROCO
        if hasattr(self, 'checkboxes_dict') and tipo_proposta in self.checkboxes_dict:
            for checkbox in self.checkboxes_dict[tipo_proposta].values():
                checkbox.setEnabled(troco_preenchido)
        
        print(f"   → Flags habilitados: {troco_preenchido}")
        
        # Validar estado dos botões após digitar no troco
        if hasattr(self, 'validar_botoes_apos_mudanca_filtro'):
            self.validar_botoes_apos_mudanca_filtro(tipo_proposta)            

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

        if tipo_proposta in ["Refin", "Saque Direcionado", "Solicitação Interna"] and hasattr(self, 'troco_inputs') and tipo_proposta in self.troco_inputs:
            valor_troco = self.troco_inputs[tipo_proposta].text().strip()
            
            # ⭐⭐ PRINT DO VALOR DIGITADO
            print(f"🔍 Valor de Troco Digitado ({tipo_proposta}): '{valor_troco}'")
            
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
                    print(f"✅ Valor de Troco Ajustado ({tipo_proposta}): '{valor_formatado}'")
                    
                    # ⭐⭐ ATUALIZAR O CAMPO VISUALMENTE
                    self.troco_inputs[tipo_proposta].blockSignals(True)
                    self.troco_inputs[tipo_proposta].setText(valor_formatado)
                    self.troco_inputs[tipo_proposta].blockSignals(False)
                    
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