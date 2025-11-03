import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleSheetsAPI:
    def __init__(self, spreadsheet_id, credentials_file='credentials.json', token_file='token.pickle'):
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self.authenticate()
    
    def authenticate(self):
        """Autentica com a API do Google Sheets"""
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        # O arquivo token.pickle armazena os tokens de acesso e atualização
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não há credenciais válidas disponíveis, faz o login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salva as credenciais para a próxima execução
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('sheets', 'v4', credentials=creds)
    
    def append_row(self, range_name, values):
        """Adiciona uma nova linha na planilha"""
        try:
            body = {
                'values': [values]
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True, "Linha adicionada com sucesso"
        except Exception as e:
            return False, f"Erro ao adicionar linha: {str(e)}"
    
    def get_data(self, range_name):
        """Obtém dados da planilha"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return []