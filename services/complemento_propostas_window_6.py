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
                print(f"❌ Formato inválido: {texto}")
            
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
        print(f"🔎 Verificando formato completo: '{texto}' | Tipo: {tipo_proposta}")
        
        if tipo_proposta == "Solicitação Interna":
            # ⭐⭐ ACEITA DOIS FORMATOS ⭐⭐
            
            # Formato 1: A00-00000000000 (Letra + 2 dígitos + hífen + 11 dígitos)
            if len(texto) == 15 and '-' in texto:
                partes = texto.split('-')
                print(f"📝 Formato 1 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 3 and 
                    partes[0][0].isalpha() and  # Primeiro caractere é letra
                    partes[0][1:].isdigit() and  # Próximos 2 são dígitos
                    len(partes[1]) == 11 and partes[1].isdigit()):  # 11 dígitos após hífen
                    print("✅ Formato 1 válido: A00-00000000000")
                    return True
            
            # Formato 2: 00-00000000000 (2 dígitos + hífen + 11 dígitos)
            if len(texto) == 14 and '-' in texto:
                partes = texto.split('-')
                print(f"📝 Formato 2 - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 2 and partes[0].isdigit() and
                    len(partes[1]) == 11 and partes[1].isdigit()):
                    print("✅ Formato 2 válido: 00-00000000000")
                    return True
            
            print("❌ Nenhum formato válido para Solicitação Interna")
            return False
            
        else:
            # Outras abas: apenas formato XX-XXXXXXXXXXX
            if len(texto) == 14 and '-' in texto:
                partes = texto.split('-')
                print(f"📝 Outras abas - Partes: {partes}")
                if (len(partes) == 2 and 
                    len(partes[0]) == 2 and partes[0].isdigit() and
                    len(partes[1]) == 11 and partes[1].isdigit()):
                    print("✅ Formato válido para outras abas: 00-00000000000")
                    return True
            
            print("❌ Formato inválido para outras abas")
            return False