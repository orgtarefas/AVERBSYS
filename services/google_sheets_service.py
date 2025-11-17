import pandas as pd
import requests
from io import StringIO

class GoogleSheetsService:
    def __init__(self):
        self.dados = []
        self.carregar_dados_reais()
    
    def carregar_dados_reais(self):
        """Carrega dados reais da planilha Google Sheets pública"""
        try:
            sheet_id = "1p0hnhlLH_xGKLNZzGkpC52V2o9mkCBYSTHIcxVix_GQ"
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            print("Tentando carregar dados da planilha...")
            
            response = requests.get(url)
            response.raise_for_status()
            
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            print(f"Colunas encontradas: {df.columns.tolist()}")
            print(f"Total de linhas: {len(df)}")
            
            dados_processados = []
            
            for index, row in df.iterrows():
                if (len(row) > 7 and 
                    pd.notna(row.iloc[6]) and
                    pd.notna(row.iloc[2]) and 
                    pd.notna(row.iloc[5])):
                    
                    regiao = str(row.iloc[6]).strip()
                    convenio = str(row.iloc[2]).strip()
                    produto = str(row.iloc[5]).strip()
                    status = str(row.iloc[7]).strip() if len(row) > 7 and pd.notna(row.iloc[7]) else "N/A"
                    
                    dados_processados.append({
                        'Região': regiao,
                        'Convênio': convenio,
                        'Produto': produto,
                        'Status': status
                    })
            
            self.dados = dados_processados
            print(f"Dados reais carregados com sucesso: {len(self.dados)} registros")
                
        except Exception as e:
            print(f"Erro ao carregar dados reais: {e}")
            self.dados = []
    
    def get_regioes(self):
        """Retorna lista única de regiões"""
        regioes = set()
        for row in self.dados:
            if row.get('Região') and row['Região'] != 'N/A':
                regioes.add(row['Região'])
        return sorted(list(regioes))
    
    def get_convenios_por_regiao(self, regiao):
        """Retorna convênios filtrados por região"""
        convenios = set()
        for row in self.dados:
            if (row.get('Região') == regiao and 
                row.get('Convênio') and row['Convênio'] != 'N/A'):
                convenios.add(row['Convênio'])
        return sorted(list(convenios))
    
    def get_produtos_por_convenio(self, convenio):
        """Retorna produtos filtrados por convênio"""
        produtos = set()
        for row in self.dados:
            if (row.get('Convênio') == convenio and 
                row.get('Produto') and row['Produto'] != 'N/A'):
                produtos.add(row['Produto'])
        return sorted(list(produtos))
    
    def get_status_por_produto(self, produto):
        """Retorna status para um produto específico"""
        for row in self.dados:
            if row.get('Produto') == produto:
                status = row.get('Status', 'Status não encontrado')
                return status if status != 'N/A' else 'Status não informado'
        return "Produto não encontrado"