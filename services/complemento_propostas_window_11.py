from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFrame, QFileDialog)
from PyQt5.QtCore import QDate
import pandas as pd
from datetime import datetime


class PropostasWindowPart11:
    """Parte 11 - Funcionalidade TMA no Histórico"""
    
    def init_tma_tab(self):
        """Inicializa a funcionalidade TMA na aba de Histórico"""
        try:
            self.criar_layout_tma()
            # Conectar o botão TMA que já foi criado na Part5
            if hasattr(self, 'btn_tma_historico'):
                self.btn_tma_historico.clicked.connect(self.mostrar_tma)
                print("✅ Botão TMA conectado com sucesso")
            else:
                print("❌ Botão TMA não encontrado")
        except Exception as e:
            print(f"❌ Erro ao inicializar TMA: {e}")
    
    def criar_layout_tma(self):
        """Cria o layout específico para TMA"""
        try:
            # Layout principal do TMA
            self.tma_widget = QWidget()
            self.tma_layout = QVBoxLayout(self.tma_widget)
            
            # Frame para os controles do TMA
            tma_frame = QFrame()
            tma_frame.setFrameStyle(QFrame.StyledPanel)
            tma_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            
            tma_frame_layout = QVBoxLayout(tma_frame)
            
            # Cabeçalho do TMA
            header_layout = QHBoxLayout()
            
            # Período
            header_layout.addWidget(QLabel("Período:"))
            self.tma_data_inicio = QDateEdit()
            self.tma_data_inicio.setDate(QDate.currentDate().addDays(-30))
            self.tma_data_inicio.setCalendarPopup(True)
            self.tma_data_inicio.setFixedWidth(140) 
            header_layout.addWidget(self.tma_data_inicio)
            
            header_layout.addWidget(QLabel("até"))
            self.tma_data_fim = QDateEdit()
            self.tma_data_fim.setDate(QDate.currentDate())
            self.tma_data_fim.setCalendarPopup(True)
            self.tma_data_fim.setFixedWidth(140) 
            header_layout.addWidget(self.tma_data_fim)
            
            # Analista
            header_layout.addWidget(QLabel("Analista:"))
            self.tma_analista_combo = QComboBox()
            self.tma_analista_combo.setFixedWidth(160)  
            header_layout.addWidget(self.tma_analista_combo)
            
            # Botões
            self.btn_extrair_tma = QPushButton("Extrair Relatório")
            self.btn_extrair_tma.setFixedWidth(140)  
            self.btn_extrair_tma.clicked.connect(self.extrair_relatorio_tma)
            header_layout.addWidget(self.btn_extrair_tma)
            
            # ⭐⭐ BOTÃO ENVIAR TEAMS - APENAS PARA GERENTE E DEV
            perfil = self.user_data.get('perfil', '').lower()
            if perfil not in ['supervisor']:
                self.btn_enviar_teams = QPushButton("Enviar TEAMS")
                self.btn_enviar_teams.setFixedWidth(140)  
                self.btn_enviar_teams.clicked.connect(self.enviar_teams_tma)
                header_layout.addWidget(self.btn_enviar_teams)
            
            # ⭐⭐ BOTÃO SAIR TMA
            self.btn_sair_tma = QPushButton("🚪 SAIR TMA")
            self.btn_sair_tma.setFixedWidth(120)  
            self.btn_sair_tma.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    font-weight: bold;
                    border: 1px solid #c82333;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.btn_sair_tma.clicked.connect(self.sair_tma)
            header_layout.addWidget(self.btn_sair_tma)
            
            header_layout.addStretch()
            tma_frame_layout.addLayout(header_layout)
            
            # Tabela TMA
            self.tabela_tma = QTableWidget()
            self.tabela_tma.setColumnCount(4)
            self.tabela_tma.setHorizontalHeaderLabels(["Analista", "Qtd Contratos", "Duração Total", "TMA"])
            
            # ⭐⭐ AUMENTAR ALTURA DO CABEÇALHO DA TABELA
            header = self.tabela_tma.horizontalHeader()
            header.setDefaultSectionSize(120)  # ⭐⭐ NOVO: largura padrão das colunas
            header.setMinimumSectionSize(100)  # ⭐⭐ NOVO: largura mínima
            
            # Configurar cabeçalho individualmente
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            # ⭐⭐ ALTURA DAS LINHAS DO CABEÇALHO
            self.tabela_tma.verticalHeader().setDefaultSectionSize(20)  
            self.tabela_tma.setStyleSheet("""
                QTableWidget {
                    font-size: 11px;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 8px;
                    border: 1px solid #dee2e6;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
            
            tma_frame_layout.addWidget(self.tabela_tma)
            
            self.tma_layout.addWidget(tma_frame)
            
            # Inicialmente escondido
            self.tma_widget.setVisible(False)
            
            # Adiciona o widget TMA ao layout do histórico
            if hasattr(self, 'historico_table'):
                parent_layout = self.historico_table.parent().layout()
                for i in range(parent_layout.count()):
                    if parent_layout.itemAt(i).widget() == self.historico_table:
                        parent_layout.insertWidget(i, self.tma_widget)
                        break
            
            print("✅ Layout TMA criado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao criar layout TMA: {e}")
    
    def mostrar_tma(self):
        """Mostra/oculta a seção TMA e trava as abas"""
        try:
            if self.tma_widget.isVisible():
                self.sair_tma()
            else:
                self.entrar_modo_tma()
                
        except Exception as e:
            print(f"❌ Erro ao mostrar/ocultar TMA: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar TMA: {str(e)}")
    
    def entrar_modo_tma(self):
        """Entra no modo TMA - trava abas e mostra relatório"""
        try:
            # Mostrar widget TMA
            self.tma_widget.setVisible(True)
            
            # ⭐⭐ OCULTAR BOTÃO TMA E MOSTRAR SAIR TMA
            if hasattr(self, 'btn_tma_historico'):
                self.btn_tma_historico.setVisible(False)
            
            # ⭐⭐ TRAVAR TODAS AS ABAS EXCETO HISTÓRICO
            self.travar_abas(True)
            
            # ⭐⭐ REMOVIDO: self.btn_tma_historico.setText("📈 TMA ATIVO")
            
            # ⭐⭐ OCULTAR OUTROS ELEMENTOS DO HISTÓRICO
            if hasattr(self, 'historico_table'):
                self.historico_table.setVisible(False)
            
            # Carregar dados TMA
            self.carregar_analistas_tma()
            self.carregar_dados_tma()
            
            print("🔧 Modo TMA ativado - abas travadas")
            
        except Exception as e:
            print(f"❌ Erro ao entrar no modo TMA: {e}")

    def sair_tma(self):
        """Sai do modo TMA - destrava abas e volta ao normal"""
        try:
            # Esconder widget TMA
            self.tma_widget.setVisible(False)
            
            # ⭐⭐ MOSTRAR BOTÃO TMA E OCULTAR SAIR TMA
            if hasattr(self, 'btn_tma_historico'):
                self.btn_tma_historico.setVisible(True)
            
            # ⭐⭐ DESTRAVAR TODAS AS ABAS
            self.travar_abas(False)
            
            # ⭐⭐ REMOVIDO: self.btn_tma_historico.setText("📈 TMA")
            
            # ⭐⭐ MOSTRAR ELEMENTOS DO HISTÓRICO NOVAMENTE
            if hasattr(self, 'historico_table'):
                self.historico_table.setVisible(True)
            
            print("🔧 Modo TMA desativado - abas liberadas")
            
        except Exception as e:
            print(f"❌ Erro ao sair do modo TMA: {e}")
    
    def travar_abas(self, travar=True):
        """Trava ou destrava todas as abas do sistema"""
        try:
            # Travar/destravar todas as abas principais
            for i in range(self.tabs.count()):
                if travar:
                    # Travar todas as abas exceto Histórico
                    if self.tabs.tabText(i) != "Histórico":
                        self.tabs.setTabEnabled(i, False)
                else:
                    # Destravar todas as abas
                    self.tabs.setTabEnabled(i, True)
            
            # ⭐⭐ TRAVAR TAMBÉM OS FILTROS DO HISTÓRICO (exceto TMA)
            if hasattr(self, 'data_inicio'):
                self.data_inicio.setEnabled(not travar)
            if hasattr(self, 'data_fim'):
                self.data_fim.setEnabled(not travar)
            if hasattr(self, 'combo_analista'):
                self.combo_analista.setEnabled(not travar)
            if hasattr(self, 'btn_filtrar_historico'):
                self.btn_filtrar_historico.setEnabled(not travar)
            if hasattr(self, 'exportar_button'):
                self.exportar_button.setEnabled(not travar)
        
                
        except Exception as e:
            print(f"❌ Erro ao {'travar' if travar else 'destravar'} abas: {e}")
    
    def carregar_analistas_tma(self):
        print(f"comentada def carregar_analistas_tma")
        """Carrega os analistas no combo box baseado no perfil do usuário"""
    #    try:
    #        self.tma_analista_combo.clear()
            
    #        perfil = self.user_data.get('perfil', '').lower()
            
            # Se for Gerente ou Dev, mostra TODOS + analistas específicos
    #        if perfil in ['gerente', 'dev']:
    #            self.tma_analista_combo.addItem("TODOS", "todos")
                
                # ⭐⭐ CORREÇÃO: Usar proposta_service em vez de user_service
    #            analistas = self.proposta_service.obter_analistas_tma()
    #            for analista in analistas:
    #                self.tma_analista_combo.addItem(analista['login'], analista['login'])
    #        else:
                # Para outros perfis, mostra apenas o próprio login
    #            login_atual = self.user_data.get('login', '')
    #            self.tma_analista_combo.addItem(login_atual, login_atual)
            
    #        print(f"✅ Analistas TMA carregados: {self.tma_analista_combo.count()} itens")
            
    #    except Exception as e:
    #        print(f"❌ Erro ao carregar analistas TMA: {e}")
    #        QMessageBox.warning(self, "Erro", f"Erro ao carregar analistas: {str(e)}")
    
    def carregar_dados_tma(self):
        """Carrega os dados TMA na tabela"""
        print(f"✅ Dados TMA comentado carregamento def carregar_dados_tma")
    #    try:
    #        # Obter parâmetros
    #        data_inicio = self.tma_data_inicio.date().toString("yyyy-MM-dd")
    #        data_fim = self.tma_data_fim.date().toString("yyyy-MM-dd")
    #        analista_selecionado = self.tma_analista_combo.currentData()
        
        #    print(f"🔍 Carregando dados TMA: {data_inicio} a {data_fim}, Analista: {analista_selecionado}")
            
            # Buscar dados do TMA
        #    dados_tma = self.proposta_service.obter_dados_tma(
        #        data_inicio, data_fim, analista_selecionado, self.user_data
        #    )
            
            # Preencher tabela
        #    self.tabela_tma.setRowCount(len(dados_tma))
            
        #    for row, item in enumerate(dados_tma):
                # Analista
        #        self.tabela_tma.setItem(row, 0, QTableWidgetItem(item['analista']))
                
                # Qtd Contratos
        #        self.tabela_tma.setItem(row, 1, QTableWidgetItem(str(item['qtd_contratos'])))
                
                # Duração Total (formato HH:MM:SS)
        #        duracao_total = self.formatar_duracao(item['duracao_total'])
        #        self.tabela_tma.setItem(row, 2, QTableWidgetItem(duracao_total))
                
                # TMA (média por contrato)
        #        tma = self.calcular_tma(item['duracao_total'], item['qtd_contratos'])
        #        self.tabela_tma.setItem(row, 3, QTableWidgetItem(tma))
            
        #    print(f"✅ Dados TMA carregados: {len(dados_tma)} registros")
            
        #except Exception as e:
        #    print(f"❌ Erro ao carregar dados TMA: {e}")
        #    QMessageBox.warning(self, "Erro", f"Erro ao carregar dados TMA: {str(e)}")
    
    def calcular_tma(self, duracao_total_segundos, qtd_contratos):
        """Calcula o TMA (Tempo Médio de Atendimento)"""
        try:
            if qtd_contratos == 0:
                return "00:00:00"
            
            # Calcular média em segundos
            tma_segundos = duracao_total_segundos / qtd_contratos
            
            # Converter para formato HH:MM:SS
            horas = int(tma_segundos // 3600)
            minutos = int((tma_segundos % 3600) // 60)
            segundos = int(tma_segundos % 60)
            
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        except:
            return "00:00:00"
    
    def formatar_duracao(self, segundos):
        """Formata duração de segundos para HH:MM:SS"""
        try:
            horas = int(segundos // 3600)
            minutos = int((segundos % 3600) // 60)
            segundos = int(segundos % 60)
            
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        except:
            return "00:00:00"
    
    def extrair_relatorio_tma(self):
        """Extrai relatório TMA em Excel - usuário escolhe local"""
        try:
            # Obter dados atuais da tabela
            dados = []
            for row in range(self.tabela_tma.rowCount()):
                item = {
                    'analista': self.tabela_tma.item(row, 0).text(),
                    'qtd_contratos': int(self.tabela_tma.item(row, 1).text()),
                    'duracao_total': self.tabela_tma.item(row, 2).text(),
                    'tma': self.tabela_tma.item(row, 3).text()
                }
                dados.append(item)
            
            if not dados:
                QMessageBox.information(self, "Aviso", "Nenhum dado para exportar.")
                return
            
            # ⭐⭐ USUÁRIO ESCOLHE O LOCAL E NOME DO ARQUIVO
            data_hoje = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"Relatorio_TMA_{data_hoje}.xlsx"
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Relatório TMA",
                default_filename,
                "Arquivos Excel (*.xlsx);;Todos os arquivos (*)"
            )
            
            # Se o usuário cancelou a seleção
            if not filename:
                print("❌ Exportação cancelada pelo usuário")
                return
            
            # ⭐⭐ GARANTIR EXTENSÃO .xlsx
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Criar DataFrame
            df = pd.DataFrame(dados)
            
            # Salvar arquivo
            df.to_excel(filename, index=False, engine='openpyxl')
            
            QMessageBox.information(self, "Sucesso", 
                                f"Relatório exportado com sucesso!\n\n"
                                f"Local: {filename}")
            
            print(f"✅ Relatório TMA salvo em: {filename}")
                
        except Exception as e:
            print(f"❌ Erro ao exportar relatório: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao exportar relatório: {str(e)}")
    
    def enviar_teams_tma(self):
        """Função para enviar relatório para Teams (futura implementação)"""
        QMessageBox.information(self, "Em Desenvolvimento", 
                               "Funcionalidade de envio para Teams será implementada em breve.")
        

    def limpar_contrato(self, tipo_contrato):
        """Limpa todos os campos do contrato específico"""
        try:
            print(f"🧹 Limpando contrato: {tipo_contrato}")
            
            # Limpar número do contrato
            if tipo_contrato in self.numero_inputs:
                self.numero_inputs[tipo_contrato].clear()
                self.numero_inputs[tipo_contrato].setEnabled(True)
                self.numero_inputs[tipo_contrato].setStyleSheet("")
            
            # Resetar filtros
            if tipo_contrato in self.regiao_combos:
                self.regiao_combos[tipo_contrato].setCurrentIndex(0)
                self.regiao_combos[tipo_contrato].setEnabled(False)
            
            if tipo_contrato in self.convenio_combos:
                self.convenio_combos[tipo_contrato].clear()
                self.convenio_combos[tipo_contrato].addItem("Selecione um convênio", "")
                self.convenio_combos[tipo_contrato].setEnabled(False)
            
            if tipo_contrato in self.produto_combos:
                self.produto_combos[tipo_contrato].clear()
                self.produto_combos[tipo_contrato].addItem("Selecione um produto", "")
                self.produto_combos[tipo_contrato].setEnabled(False)
            
            # Resetar status
            if tipo_contrato in self.status_labels:
                self.status_labels[tipo_contrato].setText("Não selecionado")
                self.status_labels[tipo_contrato].setStyleSheet("""
                    QLabel {
                        font-weight: bold; 
                        padding: 5px; 
                        background-color: #f8f9fa; 
                        border: 1px solid #dee2e6; 
                        border-radius: 3px;
                        color: #6c757d;
                    }
                """)
            
            # Limpar checkboxes
            if tipo_contrato in self.checkboxes_dict:
                for checkbox in self.checkboxes_dict[tipo_contrato].values():
                    checkbox.setChecked(False)
                    checkbox.setEnabled(False)
            
            # Limpar campos adicionais
            if hasattr(self, 'cpf_inputs') and tipo_contrato in self.cpf_inputs:
                self.cpf_inputs[tipo_contrato].clear()
                self.cpf_inputs[tipo_contrato].setEnabled(False)
            
            if hasattr(self, 'valor_inputs') and tipo_contrato in self.valor_inputs:
                self.valor_inputs[tipo_contrato].clear()
                self.valor_inputs[tipo_contrato].setEnabled(False)
            
            if hasattr(self, 'troco_inputs') and tipo_contrato in self.troco_inputs:
                self.troco_inputs[tipo_contrato].clear()
                self.troco_inputs[tipo_contrato].setEnabled(False)
            
            if hasattr(self, 'prazo_inputs') and tipo_contrato in self.prazo_inputs:
                self.prazo_inputs[tipo_contrato].clear()
                self.prazo_inputs[tipo_contrato].setEnabled(False)
            
            if hasattr(self, 'observacoes_inputs') and tipo_contrato in self.observacoes_inputs:
                self.observacoes_inputs[tipo_contrato].clear()
                self.observacoes_inputs[tipo_contrato].setEnabled(False)
            
            # Resetar dados internos
            self.contrato_em_andamento = False
            self.tipo_contrato_atual = None
            self.data_criacao = None
            self.data_conclusao = None
            self.tarefas_concluidas = {}
            self.eh_reanalise = False
            self.contrato_original = None
            
            # Parar timer
            self.timer_duracao.stop()
            
            # Resetar info de data
            if tipo_contrato in self.data_info_labels:
                self.data_info_labels[tipo_contrato].setText("Data/Hora Criação: --/--/-- --:--:--")
            
            # Destravar todas as abas
            self.destravar_todas_abas()
            
            # Desabilitar botões
            if tipo_contrato in self.aprovar_buttons:
                self.aprovar_buttons[tipo_contrato].setEnabled(False)
            
            if tipo_contrato in self.recusar_buttons:
                self.recusar_buttons[tipo_contrato].setEnabled(False)
            
            print(f"✅ Contrato {tipo_contrato} limpo com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao limpar contrato: {e}")        
                                