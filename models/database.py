import pandas as pd
from PyQt5.QtCore import QObject

class DatabaseManager(QObject):
    def __init__(self):
        super().__init__()
        self.data = None
        self.columns = {
            'login': 'LOGIN',
            'senha': 'SENHA', 
            'perfil': 'PERFIL',
            'status': 'STATUS',  # Alterado para STATUS
            'nome_completo': 'NOME COMPLETO',
            'data_cadastro': 'DATA CADASTRO'
        }
    
    def set_data(self, data):
        self.data = data
    
    def verify_login(self, username, password):
        if self.data is None:
            return None, "Dados não carregados"
        
        try:
            # Usar STATUS em maiúsculo
            status_column = 'STATUS' if 'STATUS' in self.data.columns else 'Status'
            
            user_row = self.data[
                (self.data[self.columns['login']] == username) & 
                (self.data[self.columns['senha']] == password)
            ]
            
            if user_row.empty:
                return None, "Login ou senha incorretos"
            
            user_data = user_row.iloc[0]
            
            if user_data[status_column] != 'Ativo':
                return None, "Usuário bloqueado ou inativo"
            
            return {
                'login': user_data[self.columns['login']],
                'perfil': user_data[self.columns['perfil']],
                'nome_completo': user_data[self.columns['nome_completo']],
                'status': user_data[status_column]
            }, None
            
        except Exception as e:
            return None, f"Erro na verificação: {str(e)}"
    
    def user_exists(self, login, nome_completo):
        if self.data is None:
            return True, "Dados não carregados"
        
        try:
            login_exists = not self.data[
                self.data[self.columns['login']] == login
            ].empty
            
            nome_exists = not self.data[
                self.data[self.columns['nome_completo']] == nome_completo
            ].empty
            
            if login_exists and nome_exists:
                return True, "Login e Nome Completo já existem"
            elif login_exists:
                return True, "Login já existe"
            elif nome_exists:
                return True, "Nome Completo já existe"
            else:
                return False, None
                
        except Exception as e:
            return True, f"Erro na verificação: {str(e)}"