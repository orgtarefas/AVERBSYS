from PyQt5.QtWidgets import (QMessageBox)

class PropostasWindowPart1:
    """Parte 1 - Métodos de inicialização e configuração básica"""
    
    def center_window(self):
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def ajustar_tamanho_responsivo(self):
        """Ajusta o tamanho da janela baseado no tamanho da tela - OTIMIZADO PARA 1366x768"""
        screen = self.screen().availableGeometry()
        
        # ⭐⭐ OTIMIZADO PARA 1366x768 - ALTURA REDUZIDA
        if screen.width() <= 1366:
            # Modo compacto para telas pequenas
            width = int(screen.width() * 0.95)  # 95% da largura
            height = int(screen.height() * 0.85)  # ⭐⭐ REDUZIDO de 0.9 para 0.85
            
            # Limites específicos para 1366x768
            width = min(width, 1300)
            height = min(height, 650)  # ⭐⭐ REDUZIDO de 700 para 650
            
            # Mínimos para usabilidade
            width = max(width, 1000)
            height = max(height, 550)  # ⭐⭐ REDUZIDO de 600 para 550
        else:
            # Modo normal para telas maiores
            width = int(screen.width() * 0.85)
            height = int(screen.height() * 0.75)  # ⭐⭐ REDUZIDO de 0.8 para 0.75
            
            width = max(1000, min(width, 1400))
            height = max(550, min(height, 700))  # ⭐⭐ REDUZIDO de 600/800 para 550/700
        
        print(f"🖥️  Tela: {screen.width()}x{screen.height()}")
        print(f"📐 Ajustando janela para: {width}x{height}")
        
        self.resize(width, height)
    
    def carregar_filtros_iniciais(self):
        """Carrega os dados reais nos filtros de todas as abas"""
        try:
            if self.google_sheets_service is None:
                print("⚠️ Google Sheets Service não disponível - usando dados mock")
                regioes = ["Região 1", "Região 2", "Região 3"]  # Dados mock
            else:
                regioes = self.google_sheets_service.get_regioes()
            
            print(f"📍 Regiões carregadas: {regioes}")
            
            if not regioes:
                QMessageBox.warning(self, "Aviso", 
                                "Nenhuma região encontrada na planilha. "
                                "Verifique se a planilha possui dados nas colunas G (Região), C (Convênio) e F (Produto).")
                return
            
            for tipo_proposta in ['Saque Fácil', 'Refin', 'Saque Direcionado', 'Solicitação Interna']:
                print(f"🔄 Carregando filtros para: {tipo_proposta}")
                
                if tipo_proposta in self.regiao_combos:
                    self.regiao_combos[tipo_proposta].clear()
                    self.regiao_combos[tipo_proposta].addItem("Selecione uma região", "")
                    for regiao in regioes:
                        self.regiao_combos[tipo_proposta].addItem(regiao, regiao)
                    
                    # ⭐⭐ INICIAR COM REGIÃO DESABILITADA ⭐⭐
                    self.regiao_combos[tipo_proposta].setEnabled(False)
                    print(f"   ✅ Regiões carregadas: {self.regiao_combos[tipo_proposta].count()} itens (Desabilitada)")
                    
                    # Garantir que convênio e produto também tenham "Selecione" e desabilitados
                    self.convenio_combos[tipo_proposta].clear()
                    self.convenio_combos[tipo_proposta].addItem("Selecione um convênio", "")
                    self.convenio_combos[tipo_proposta].setEnabled(False)
                    
                    self.produto_combos[tipo_proposta].clear()
                    self.produto_combos[tipo_proposta].addItem("Selecione um produto", "")
                    self.produto_combos[tipo_proposta].setEnabled(False)
            
            print(f"✅ Filtros carregados com {len(regioes)} regiões (todos desabilitados inicialmente)")
            
        except Exception as e:
            print(f"❌ Erro ao carregar filtros: {e}")
            QMessageBox.warning(self, "Erro", 
                            f"Erro ao carregar dados da planilha: {str(e)}")