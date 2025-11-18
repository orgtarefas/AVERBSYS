import os
import sys

class PropostasWindowPart6:
    """Parte 6 - Métodos de validação e formatação (CPF, valor, contrato)"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def formatar_cpf(self, text):
        """Formata o CPF enquanto o usuário digita"""
        sender = self.sender()
        if not sender:
            return
            
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, text))
        
        # Aplica a formatação
        if len(cpf) <= 3:
            formatted_cpf = cpf
        elif len(cpf) <= 6:
            formatted_cpf = f"{cpf[:3]}.{cpf[3:]}"
        elif len(cpf) <= 9:
            formatted_cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
        else:
            formatted_cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
        
        # Atualiza o texto sem disparar o sinal novamente
        sender.blockSignals(True)
        sender.setText(formatted_cpf)
        sender.setCursorPosition(len(formatted_cpf))
        sender.blockSignals(False)

    def formatar_valor(self, text):
        """Formata o valor monetário enquanto o usuário digita"""
        sender = self.sender()
        if not sender:
            return
            
        # Remove caracteres não numéricos, exceto vírgula
        valor = ''.join(filter(lambda x: x.isdigit() or x == ',', text))
        
        # Se houver mais de uma vírgula, mantém apenas a primeira
        if valor.count(',') > 1:
            partes = valor.split(',')
            valor = partes[0] + ',' + ''.join(partes[1:])
        
        # Move o cursor para o final
        sender.blockSignals(True)
        sender.setText(valor)
        sender.setCursorPosition(len(valor))
        sender.blockSignals(False)

    def validar_formato_contrato(self, texto, tipo_proposta):
        """Valida o formato baseado no tipo de proposta"""
        input_field = self.numero_inputs[tipo_proposta]
        
        # Limpar estilo anterior
        input_field.setStyleSheet("")
        
        print(f"🔍 Validando formato: '{texto}' | Tipo: {tipo_proposta}")
        
        # Verificar se o formato está completo
        formato_completo = self.verificar_formato_completo(texto, tipo_proposta)
        print(f"📋 Formato completo: {formato_completo}")
        
        if formato_completo:
            # Formato válido - estilo verde
            input_field.setStyleSheet("border: 2px solid #28a745;")
            print(f"✅ Formato válido: {texto}")
            
            # Configurar proposta em andamento
            self.configurar_proposta_em_andamento(texto, tipo_proposta)
                
        else:
            # Formato incompleto ou inválido
            if texto:  # Só mostra vermelho se já digitou algo
                input_field.setStyleSheet("border: 2px solid #dc3545;")
            
            # Desabilitar tudo se formato não estiver completo
            self.regiao_combos[tipo_proposta].setEnabled(False)
            self.convenio_combos[tipo_proposta].setEnabled(False)
            self.produto_combos[tipo_proposta].setEnabled(False)
            
            # Resetar filtros dependentes
            self.convenio_combos[tipo_proposta].clear()
            self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
            
            self.produto_combos[tipo_proposta].clear()
            self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
            
            self.status_labels[tipo_proposta].setText("Não selecionado")
            self.status_labels[tipo_proposta].setStyleSheet("font-weight: bold; padding: 5px;")
            
            # ⭐⭐ CORREÇÃO: Desabilitar ambos os botões quando formato não está completo
            self.aprovar_buttons[tipo_proposta].setEnabled(False)
            self.recusar_buttons[tipo_proposta].setEnabled(False)
            
            # Se tinha proposta em andamento, limpar completamente
            if self.proposta_em_andamento and self.tipo_proposta_atual == tipo_proposta:
                print("🔄 Limpando proposta em andamento...")
                self.limpar_proposta(tipo_proposta)

    
    def verificar_formato_completo(self, texto, tipo_proposta):
        """Verifica se o formato está completo baseado no tipo"""
        
        if tipo_proposta == "Solicitação Interna":
            print(f"🔍 Analisando texto: '{texto}' | Comprimento: {len(texto)} | Hífens: {texto.count('-')}")
            
            # ⭐⭐ ACEITA 5 FORMATOS DIFERENTES ⭐⭐
            
            # Padrão 1: 00-0000000000 (2 dígitos + hífen + 10 dígitos) - 13 chars
            if len(texto) == 13 and texto.count('-') == 1:
                partes = texto.split('-')
                print(f"📝 Tentando Padrão 1 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 2 and partes[0].isdigit() and
                    len(partes[1]) == 10 and partes[1].isdigit()):
                    print("✅ Padrão 1 válido: 00-0000000000")
                    return True
            
            # Padrão 2: 00-00000000000 (2 dígitos + hífen + 11 dígitos) - 14 chars
            if len(texto) == 14 and texto.count('-') == 1:
                partes = texto.split('-')
                print(f"📝 Tentando Padrão 2 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 2 and partes[0].isdigit() and
                    len(partes[1]) == 11 and partes[1].isdigit()):
                    print("✅ Padrão 2 válido: 00-00000000000")
                    return True
            
            # Padrão 3: A00-0000000000 (Letra + 2 dígitos + hífen + 10 dígitos) - 14 chars
            if len(texto) == 14 and texto.count('-') == 1:
                partes = texto.split('-')
                print(f"📝 Tentando Padrão 3 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 3 and 
                    partes[0][0].isalpha() and  # Primeiro caractere é letra
                    partes[0][1:].isdigit() and  # Próximos 2 são dígitos
                    len(partes[1]) == 10 and partes[1].isdigit()):  # 10 dígitos após hífen
                    print("✅ Padrão 3 válido: A00-0000000000")
                    return True
            
            # ⭐⭐ PADRÃO 4: A00-00000000000 (Letra + 2 dígitos + hífen + 11 dígitos) - 15 chars
            if len(texto) == 15 and texto.count('-') == 1:
                partes = texto.split('-')
                print(f"📝 Tentando Padrão 4 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 3 and 
                    partes[0][0].isalpha() and  # Primeiro caractere é letra
                    partes[0][1:].isdigit() and  # Próximos 2 são dígitos
                    len(partes[1]) == 11 and partes[1].isdigit()):  # 11 dígitos após hífen
                    print("✅ Padrão 4 válido: A00-00000000000")
                    return True
            
            # ⭐⭐ PADRÃO 5: XXXXXXXX-XXXX-X (8 caracteres + hífen + 4 caracteres + hífen + 1 caractere) - 15 chars
            print(f"🔍 Verificando Padrão 5: len={len(texto)}, hífens={texto.count('-')}")
            if len(texto) == 15 and texto.count('-') == 2:
                partes = texto.split('-')
                print(f"📝 Tentando Padrão 5 - Partes: {partes}")
                print(f"   Parte 0: '{partes[0]}' (len={len(partes[0])}, alfanumérico={self._is_alphanumeric(partes[0])})")
                print(f"   Parte 1: '{partes[1]}' (len={len(partes[1])}, alfanumérico={self._is_alphanumeric(partes[1])})")
                print(f"   Parte 2: '{partes[2]}' (len={len(partes[2])}, alfanumérico={self._is_alphanumeric(partes[2])})")
                
                if (len(partes) == 3 and 
                    len(partes[0]) == 8 and self._is_alphanumeric(partes[0]) and  # 8 caracteres alfanuméricos
                    len(partes[1]) == 4 and self._is_alphanumeric(partes[1]) and  # 4 caracteres alfanuméricos
                    len(partes[2]) == 1 and self._is_alphanumeric(partes[2])):   # 1 caractere alfanumérico
                    print("✅ Padrão 5 válido: XXXXXXXX-XXXX-X")
                    return True
                else:
                    print(f"❌ Padrão 5 inválido - condições não atendidas")
                    return False
            else:
                print(f"❌ Não entrou no Padrão 5: len={len(texto)} (esperado 15), hífens={texto.count('-')} (esperado 2)")
            
            print("❌ Nenhum padrão válido para Solicitação Interna")
            return False
            
        else:
            # Outras abas: apenas formato XX-XXXXXXXXXXX (2 dígitos + hífen + 11 dígitos)
            if len(texto) == 14 and texto.count('-') == 1:
                partes = texto.split('-')
                print(f"📝 Outras abas - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 2 and partes[0].isdigit() and
                    len(partes[1]) == 11 and partes[1].isdigit()):
                    print("✅ Formato válido para outras abas: 00-00000000000")
                    return True
            
            return False


    def _is_alphanumeric(self, texto):
        """Verifica se todos os caracteres são alfanuméricos (letras ou números)"""
        return all(c.isalnum() for c in texto)
        
    def conectar_eventos_troco(self):
        """Conecta eventos de digitação nos inputs de troco para validação"""
        if hasattr(self, 'troco_inputs'):
            for tipo_proposta, input_field in self.troco_inputs.items():
                if input_field is not None:
                    # Conectar evento de texto alterado para validação
                    input_field.textChanged.connect(
                        lambda text, tp=tipo_proposta: self.validar_apos_troco(text, tp)
                    )
                    print(f"🔧 Evento de validação conectado para troco input: {tipo_proposta}")

    def validar_apos_troco(self, text, tipo_proposta):
        """Valida os botões após digitar no campo de troco"""
        print(f"💰 Digitando no Troco ({tipo_proposta}): '{text}'")
        
        # Validar estado dos botões após digitar no troco
        if hasattr(self, 'validar_botoes_apos_mudanca_filtro'):
            self.validar_botoes_apos_mudanca_filtro(tipo_proposta)