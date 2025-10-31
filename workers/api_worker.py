import pandas as pd
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import time

class WorkerThread(QThread):
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)
    
    def __init__(self, worker_function, *args, **kwargs):
        super().__init__()
        self.worker_function = worker_function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.worker_function(*self.args, **self.kwargs)
            self.finished_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))

class APIWorker(QObject):
    data_loaded = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    login_verified = pyqtSignal(dict, str)  # user_data, error
    user_registered = pyqtSignal(bool, str)  # success, message
    
    def __init__(self):
        super().__init__()
        self.data = None
        # URL alternativa para CSV
        self.sheet_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFe7Ui1HQtmUKVDopL2u7Amm2Ja4LsSpMZLQBHQYrLUvlsGaRKkFzGrOVPLu988Q/pub?output=csv"
        self.sheet_html_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFe7Ui1HQtmUKVDopL2u7Amm2Ja4LsSpMZLQBHQYrLUvlsGaRKkFzGrOVPLu988Q/pubhtml"
        self.threads = []
    
    def load_data(self):
        def worker():
            try:
                # Tentar primeiro como CSV (mais confiável)
                print("Tentando carregar como CSV...")
                data = pd.read_csv(self.sheet_csv_url)
                
                # Verificar se as colunas esperadas estão presentes
                expected_columns = ['LOGIN', 'SENHA', 'PERFIL', 'STATUS', 'NOME COMPLETO', 'DATA CADASTRO']
                
                # Se não tiver os cabeçalhos corretos, tentar inferir
                if not all(col in data.columns for col in expected_columns):
                    print("Cabeçalhos não encontrados, tentando ajustar...")
                    # Tentar usar a primeira linha como cabeçalho
                    data = pd.read_csv(self.sheet_csv_url, header=0)
                    
                    # Renomear colunas se necessário - mapear para maiúsculas
                    rename_dict = {}
                    for i, col in enumerate(data.columns):
                        col_upper = col.upper().strip()
                        if col_upper in expected_columns:
                            rename_dict[col] = col_upper
                    
                    if rename_dict:
                        data = data.rename(columns=rename_dict)
                        print(f"Colunas renomeadas: {rename_dict}")
                
                # Garantir que temos todas as colunas esperadas
                for col in expected_columns:
                    if col not in data.columns:
                        print(f"Aviso: Coluna {col} não encontrada nos dados")
                
                print("Dados carregados com sucesso via CSV")
                print(f"Colunas: {list(data.columns)}")
                print(f"Primeiras linhas:\n{data.head()}")
                
                return {'data': data, 'type': 'load'}
                    
            except Exception as csv_error:
                print(f"Erro com CSV: {csv_error}, tentando HTML...")
                try:
                    # Tentar como HTML fallback
                    tables = pd.read_html(self.sheet_html_url)
                    if tables:
                        data = tables[0]
                        
                        # Remover linhas extras e cabeçalhos duplicados
                        if not data.empty:
                            # Verificar se a primeira linha é cabeçalho
                            first_row = data.iloc[0]
                            if first_row.astype(str).str.contains('LOGIN|SENHA|PERFIL', case=False).any():
                                data = data[1:]  # Remove a primeira linha se for cabeçalho
                                data.columns = first_row.values
                            
                            # Renomear colunas para maiúsculas
                            rename_dict = {}
                            for col in data.columns:
                                col_upper = str(col).upper().strip()
                                if col_upper in expected_columns:
                                    rename_dict[col] = col_upper
                            
                            if rename_dict:
                                data = data.rename(columns=rename_dict)
                            
                            print("Dados carregados com sucesso via HTML")
                            print(f"Colunas: {list(data.columns)}")
                            return {'data': data, 'type': 'load'}
                        else:
                            raise Exception("Tabela HTML vazia")
                    else:
                        raise Exception("Nenhuma tabela encontrada na URL HTML")
                        
                except Exception as html_error:
                    raise Exception(f"Erro ao carregar dados: CSV: {csv_error}, HTML: {html_error}")
        
        thread = WorkerThread(worker)
        thread.finished_signal.connect(self._on_load_finished)
        thread.error_signal.connect(self.error_occurred)
        thread.start()
        self.threads.append(thread)
    
    def _on_load_finished(self, result):
        if result['type'] == 'load':
            self.data = result['data']
            self.data_loaded.emit(self.data)
    
    def verify_login(self, username, password):
        def worker():
            try:
                if self.data is None:
                    return {'success': False, 'error': "Dados não carregados", 'type': 'login'}
                
                # Limpar dados - remover linhas com NaN
                clean_data = self.data.dropna(subset=['LOGIN', 'SENHA'])
                
                # Converter para string para comparação
                clean_data['LOGIN'] = clean_data['LOGIN'].astype(str).str.strip()
                clean_data['SENHA'] = clean_data['SENHA'].astype(str).str.strip()
                
                # Verificar se a coluna STATUS existe, caso contrário usar Status
                status_column = 'STATUS' if 'STATUS' in clean_data.columns else 'Status'
                if status_column not in clean_data.columns:
                    return {'success': False, 'error': "Coluna STATUS não encontrada nos dados", 'type': 'login'}
                
                clean_data[status_column] = clean_data[status_column].astype(str).str.strip()
                
                user_row = clean_data[
                    (clean_data['LOGIN'] == username.strip()) & 
                    (clean_data['SENHA'] == password.strip())
                ]
                
                if user_row.empty:
                    return {'success': False, 'error': "Login ou senha incorretos", 'type': 'login'}
                
                user_data = user_row.iloc[0]
                
                # Verificar status
                status = str(user_data.get(status_column, '')).strip()
                if status.upper() != 'ATIVO':
                    return {'success': False, 'error': "Usuário bloqueado ou inativo", 'type': 'login'}
                
                result_data = {
                    'login': str(user_data['LOGIN']),
                    'perfil': str(user_data.get('PERFIL', '')),
                    'nome_completo': str(user_data.get('NOME COMPLETO', '')),
                    'status': status
                }
                
                return {'success': True, 'data': result_data, 'type': 'login'}
                
            except Exception as e:
                return {'success': False, 'error': f"Erro na verificação: {str(e)}", 'type': 'login'}
        
        thread = WorkerThread(worker)
        thread.finished_signal.connect(self._on_login_finished)
        thread.error_signal.connect(self.error_occurred)
        thread.start()
        self.threads.append(thread)
    
    def _on_login_finished(self, result):
        if result['type'] == 'login':
            if result['success']:
                self.login_verified.emit(result['data'], "")
            else:
                # Emitir dicionário vazio para o primeiro argumento e erro no segundo
                self.login_verified.emit({}, result['error'])
    
    def register_user(self, user_data):
        def worker(user_data_param):
            try:
                if self.data is None:
                    return {'success': False, 'error': "Dados não carregados", 'type': 'register'}
                
                # Limpar dados
                clean_data = self.data.dropna(subset=['LOGIN', 'NOME COMPLETO'])
                clean_data['LOGIN'] = clean_data['LOGIN'].astype(str).str.strip()
                clean_data['NOME COMPLETO'] = clean_data['NOME COMPLETO'].astype(str).str.strip()
                
                # Verificar se usuário já existe
                login_exists = not clean_data[clean_data['LOGIN'] == user_data_param['login'].strip()].empty
                nome_exists = not clean_data[clean_data['NOME COMPLETO'] == user_data_param['nome_completo'].strip()].empty
                
                if login_exists and nome_exists:
                    return {'success': False, 'error': "Login e Nome Completo já existem", 'type': 'register'}
                elif login_exists:
                    return {'success': False, 'error': "Login já existe", 'type': 'register'}
                elif nome_exists:
                    return {'success': False, 'error': "Nome Completo já existe", 'type': 'register'}
                else:
                    # Aqui você implementaria a escrita na planilha
                    # Por enquanto, apenas simula sucesso
                    return {'success': True, 'message': "Usuário cadastrado com sucesso", 'type': 'register'}
                    
            except Exception as e:
                return {'success': False, 'error': f"Erro no cadastro: {str(e)}", 'type': 'register'}
        
        thread = WorkerThread(worker, user_data)
        thread.finished_signal.connect(self._on_register_finished)
        thread.error_signal.connect(self.error_occurred)
        thread.start()
        self.threads.append(thread)
    
    def _on_register_finished(self, result):
        if result['type'] == 'register':
            if result['success']:
                self.user_registered.emit(True, result['message'])
            else:
                self.user_registered.emit(False, result['error'])
    
    def cleanup_threads(self):
        """Limpa threads finalizadas"""
        self.threads = [thread for thread in self.threads if thread.isRunning()]