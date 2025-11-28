from config.firebase_config import FirebaseManager
from PyQt5.QtCore import QObject, pyqtSignal

class UserService(QObject):
    user_registered = pyqtSignal(bool, str)
    user_authenticated = pyqtSignal(dict, str)
    
    def __init__(self):
        super().__init__()
        self.firebase = FirebaseManager()
        self.db_login = self.firebase.get_db_login()
        self.db_principal = self.firebase.get_db_principal()
        
        # ⭐⭐ CONTADOR DE LEITURAS PARA LOGIN
        self.contador_leituras_login = 0
        self._dados_logins = None
        print("✅ UserService inicializado - contador de leituras ativo")

    def _incrementar_contador_login(self, operacao):
        """Incrementa e exibe o contador de leituras do login"""
        self.contador_leituras_login += 1
        print(f"🔐 LEITURA LOGIN #{self.contador_leituras_login} - {operacao}")
        return self.contador_leituras_login        

    def _fazer_leitura_unica_logins(self):
        """Faz APENAS 1 LEITURA no banco de login - REAPROVEITA SE JÁ FEZ"""
        try:
            # ⭐⭐ SE JÁ FEZ A LEITURA, REAPROVEITA
            if self._dados_logins is not None:
                print("📋 Reaproveitando dados de login da leitura anterior")
                return self._dados_logins
            
            print("🔍 Fazendo 1 LEITURA no banco de login...")
            
            # ⭐⭐ APENAS 1 LEITURA - pega todo o documento
            doc_ref = self.db_login.collection('logins').document('LOGINS_AVERBSYS')
            documento = doc_ref.get()
            
            if documento.exists:
                dados = documento.to_dict()
                print(f"✅ Dados carregados com 1 leitura! Campos: {len(dados)}")
                
                # ⭐⭐ SALVA OS DADOS PARA REAPROVEITAR
                self._dados_logins = dados
                return dados
            else:
                print("❌ Documento LOGINS_AVERBSYS não encontrado!")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados de login: {e}")
            return None

    def verificar_login(self, username, password):
        try:
            print(f"🔐 Iniciando verificação de login para: {username}")
            
            # ⭐⭐ USA A MESMA LEITURA DA VERIFICAÇÃO DE VERSÃO
            dados_logins = self._fazer_leitura_unica_logins()
            
            if not dados_logins:
                print("❌ Dados de login não disponíveis")
                self.user_authenticated.emit({}, "Sistema temporariamente indisponível")
                return
            
            # Buscar usuário nos dados carregados
            usuario_encontrado = None
            
            for campo, valor in dados_logins.items():
                if campo.startswith('user_') and campo.endswith('_logiin'):
                    if valor == username.strip():
                        user_num = campo.split('_')[1]
                        usuario_encontrado = {
                            'login': valor,
                            'nome_completo': dados_logins.get(f'user_{user_num}_nome_completo', ''),
                            'perfil': dados_logins.get(f'user_{user_num}_perfil', ''),
                            'status': dados_logins.get(f'user_{user_num}_status', ''),
                            'senha': dados_logins.get(f'user_{user_num}_senha', '')
                        }
                        print(f"✅ Usuário encontrado: {usuario_encontrado['nome_completo']}")
                        break
            
            # Verificar se usuário existe, senha está correta e está ativo
            if (usuario_encontrado and 
                usuario_encontrado['senha'] == password.strip() and
                usuario_encontrado.get('status') == 'Ativo'):
                
                user_info = {
                    'login': usuario_encontrado['login'],
                    'perfil': usuario_encontrado['perfil'],
                    'nome_completo': usuario_encontrado['nome_completo'],
                    'status': usuario_encontrado['status']
                }
                
                print(f"🎯 Login bem-sucedido, emitindo sinal...")
                # ⭐⭐ EMITIR SINAL COM DADOS DO USUÁRIO
                self.user_authenticated.emit(user_info, "")
                print(f"✅ Sinal user_authenticated emitido para: {user_info['nome_completo']}")
            else:
                print("❌ Credenciais inválidas ou usuário inativo")
                self.user_authenticated.emit({}, "Usuário ou senha incorretos")
            
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            self.user_authenticated.emit({}, f"Erro na autenticação: {str(e)}")

    def obter_versao_sistema(self):
        """Obtém versão do sistema - USA OS DADOS JÁ CARREGADOS"""
        try:
            dados_logins = self._fazer_leitura_unica_logins()
            if dados_logins:
                return dados_logins.get('ver')
            return None
        except Exception as e:
            print(f"❌ Erro ao obter versão: {e}")
            return None

    def buscar_desenvolvedores_firebase(self):
        """Busca dados dos desenvolvedores - USA OS DADOS JÁ CARREGADOS"""
        try:
            dados_logins = self._fazer_leitura_unica_logins()
            if not dados_logins:
                return []
            
            desenvolvedores = []
            
            # Buscar membros da equipe
            for campo, valor in dados_logins.items():
                if campo.startswith('Membro_'):
                    if campo.endswith('_Cargo'):
                        num = campo.split('_')[1]
                        cargo = valor
                        nome = dados_logins.get(f'Membro_{num}_nome', '')
                        if cargo and nome:
                            desenvolvedores.append(f"• {nome} - {cargo}")
            
            return desenvolvedores if desenvolvedores else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar desenvolvedores: {e}")
            return []