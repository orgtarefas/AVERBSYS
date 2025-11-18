from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt
import os
import sys
from datetime import datetime, timedelta

# ⭐⭐ ADICIONAR IMPORTS NECESSÁRIOS
import pandas as pd

class PropostasWindowPart10:
    """Parte 10 - Métodos de histórico, exportação e eventos diversos"""
    
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def aba_mudou(self, index):
        """Quando muda de aba, reseta o estado"""
        # Só permite mudar de aba se não houver proposta em andamento
        if self.proposta_em_andamento:
            # Volta para a aba anterior
            current_index = self.tabs.currentIndex()
            if current_index != index:
                self.tabs.setCurrentIndex(current_index)
                QMessageBox.warning(self, "Atenção", "Finalize a proposta atual antes de mudar de aba!")
        else:
            self.tipo_proposta_atual = None
            self.data_criacao = None
            self.tarefas_concluidas = {}
    
    def travar_outras_abas(self, aba_atual):
        """Trava todas as abas exceto a atual quando uma proposta está em andamento"""
        current_index = self.tabs.indexOf(self.tabs.currentWidget())
        
        for i in range(self.tabs.count()):
            if i != current_index:
                self.tabs.setTabEnabled(i, False)
        
        print("🔒 Abas travadas - proposta em andamento")
    
    def destravar_todas_abas(self):
        """Destrava todas as abas quando não há proposta em andamento"""
        for i in range(self.tabs.count()):
            self.tabs.setTabEnabled(i, True)
        
        print("🔓 Todas as abas destravadas")
    
    def on_proposta_criada(self, success, message):
        if success:
            QMessageBox.information(self, "Sucesso", message)
            
            # Limpar formulário da aba atual
            if self.tipo_proposta_atual:
                self.limpar_proposta(self.tipo_proposta_atual)
            
            # Atualizar histórico
            self.carregar_historico()
        else:
            QMessageBox.warning(self, "Erro", message)
    
    def carregar_historico(self):
        """Carrega o histórico inicial baseado no perfil do usuário"""
        try:
            if self.user_data['perfil'] == 'Analista':
                # Para analistas, carrega apenas suas próprias propostas
                propostas = self.proposta_service.listar_propostas_por_analista(self.user_data['login'])
            else:
                # Para outros perfis, carrega todas as propostas dos últimos 30 dias
                data_inicio = datetime.now() - timedelta(days=30)
                propostas = self.proposta_service.listar_propostas_com_filtros(
                    data_inicio=data_inicio,
                    data_fim=datetime.now()
                )
            
            self.preencher_tabela_historico(propostas)
            
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    def preencher_tabela_historico(self, propostas):
        """Preenche a tabela de histórico com todas as propostas incluindo os novos campos"""
        self.historico_table.setRowCount(len(propostas))
        
        for row, proposta in enumerate(propostas):
            # CAMPOS ORIGINAIS
            self.historico_table.setItem(row, 0, QTableWidgetItem(proposta['tipo_proposta']))
            self.historico_table.setItem(row, 1, QTableWidgetItem(str(proposta['numero_proposta'])))
            self.historico_table.setItem(row, 2, QTableWidgetItem(proposta['analista']))
            
            status_item = QTableWidgetItem(proposta['status'])
            if proposta['status'] == 'Aprovada':
                status_item.setBackground(Qt.green)
            elif proposta['status'] == 'Recusada':
                status_item.setBackground(Qt.red)
            elif proposta['status'] == 'Pendente':
                status_item.setBackground(Qt.yellow)
            
            self.historico_table.setItem(row, 3, status_item)
            
            # Formatar datas
            data_criacao = proposta['data_criacao']
            if hasattr(data_criacao, 'strftime'):
                self.historico_table.setItem(row, 4, QTableWidgetItem(data_criacao.strftime("%d/%m/%Y %H:%M:%S")))
            else:
                self.historico_table.setItem(row, 4, QTableWidgetItem(str(data_criacao)))
            
            data_conclusao = proposta.get('data_conclusao')
            if data_conclusao and hasattr(data_conclusao, 'strftime'):
                self.historico_table.setItem(row, 5, QTableWidgetItem(data_conclusao.strftime("%d/%m/%Y %H:%M:%S")))
            else:
                self.historico_table.setItem(row, 5, QTableWidgetItem(" - "))
            
            # Exibir duração
            duracao = proposta.get('duracao_total', ' - ')
            self.historico_table.setItem(row, 6, QTableWidgetItem(duracao))
            
            # CAMPOS DOS FILTROS
            dados_filtro = proposta.get('dados_filtro', {})
            
            regiao = dados_filtro.get('regiao', 'N/A')
            convenio = dados_filtro.get('convenio', 'N/A')
            produto = dados_filtro.get('produto', 'N/A')
            status_produto = dados_filtro.get('status', 'N/A')
            
            self.historico_table.setItem(row, 7, QTableWidgetItem(regiao))
            self.historico_table.setItem(row, 8, QTableWidgetItem(convenio))
            self.historico_table.setItem(row, 9, QTableWidgetItem(produto))
            
            # Status do produto com formatação
            status_produto_item = QTableWidgetItem(status_produto)
            if 'ativo' in status_produto.lower():
                status_produto_item.setBackground(Qt.green)
            elif 'inativo' in status_produto.lower():
                status_produto_item.setBackground(Qt.red)
            self.historico_table.setItem(row, 10, status_produto_item)
            
            # ⭐⭐ NOVOS CAMPOS ADICIONADOS
            cpf = dados_filtro.get('cpf', 'N/A')
            valor_liberado = dados_filtro.get('valor_liberado', 'N/A')
            prazo = dados_filtro.get('prazo', 'N/A')
            observacoes = dados_filtro.get('observacoes', 'N/A')
            valor_troco = dados_filtro.get('valor_troco', 'N/A')
            motivo_recusa = dados_filtro.get('motivo_recusa_descricao', 'N/A')
            
            self.historico_table.setItem(row, 11, QTableWidgetItem(cpf))
            self.historico_table.setItem(row, 12, QTableWidgetItem(valor_liberado))
            self.historico_table.setItem(row, 13, QTableWidgetItem(prazo))
            self.historico_table.setItem(row, 14, QTableWidgetItem(observacoes))
            self.historico_table.setItem(row, 15, QTableWidgetItem(valor_troco))
            self.historico_table.setItem(row, 16, QTableWidgetItem(motivo_recusa))
        
        # ⭐⭐ AJUSTAR AUTOMATICAMENTE AS COLUNAS AO CONTEÚDO (opcional)
        self.historico_table.resizeColumnsToContents()

    def aplicar_filtros(self):
        """Aplica os filtros selecionados na tabela de histórico"""
        try:
            # Obter datas do período - já são objetos QDate
            data_inicio_qdate = self.data_inicio.date()
            data_fim_qdate = self.data_fim.date()
            
            # Converter QDate para Python date
            data_inicio = data_inicio_qdate.toPyDate()
            data_fim = data_fim_qdate.toPyDate()
            
            # Obter analista selecionado
            analista_selecionado = None
            if self.user_data['perfil'] == 'Analista':
                analista_selecionado = self.user_data['login']
            else:
                analista_data = self.combo_analista.currentData()
                if analista_data != "todos":
                    analista_selecionado = analista_data
            
            # Buscar propostas com filtros usando o método mais simples
            propostas = self.proposta_service.listar_propostas_simples_filtro(
                data_inicio=data_inicio,
                data_fim=data_fim,
                analista=analista_selecionado
            )
            
            self.preencher_tabela_historico(propostas)
            
            # Mostrar quantidades de resultados
            QMessageBox.information(self, "Filtro Aplicado", f"Encontradas {len(propostas)} propostas no período selecionado.")
            
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao aplicar filtros: {str(e)}")

    def exportar_para_xlsx(self):
        """Exporta os dados da tabela para XLSX incluindo todos os novos campos"""
        try:
            if self.historico_table.rowCount() == 0:
                QMessageBox.warning(self, "Aviso", "Não há dados para exportar!")
                return
            
            # Solicitar local para salvar o arquivo
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Salvar Arquivo Excel", 
                f"propostas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", 
                "Excel Files (*.xlsx)"
            )
            
            if not file_path:
                return
            
            # Importar pandas para criar o Excel
            import pandas as pd
            
            # Preparar dados para exportação
            headers = []
            for col in range(self.historico_table.columnCount()):
                headers.append(self.historico_table.horizontalHeaderItem(col).text())
            
            data = []
            for row in range(self.historico_table.rowCount()):
                row_data = []
                for col in range(self.historico_table.columnCount()):
                    item = self.historico_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            # Criar DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # Salvar como Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Contratos', index=False)
                
                # Ajustar largura das colunas automaticamente
                worksheet = writer.sheets['Contratos']
                for idx, col in enumerate(df.columns):
                    max_length = max(df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
            
            QMessageBox.information(self, "Sucesso", f"Dados exportados com sucesso!\n{file_path}")
            
        except ImportError:
            QMessageBox.warning(self, "Erro", 
                            "Biblioteca pandas ou openpyxl não encontrada. "
                            "Instale com: pip install pandas openpyxl")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao exportar XLSX: {str(e)}")