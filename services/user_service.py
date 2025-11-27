from config.firebase_config import FirebaseManager
from models.user_model import UserModel
from PyQt5.QtCore import QObject, pyqtSignal

class UserService(QObject):
    user_registered = pyqtSignal(bool, str)
    user_authenticated = pyqtSignal(dict, str)
    
    def __init__(self):
        super().__init__()
        self.firebase = FirebaseManager()
        self.db = self.firebase.get_db()
        self.users_ref = self.db.collection('usuarios')
        # ⭐⭐ CACHE DE USUÁRIOS
        self._usuarios_cache = None
        self._cache_timestamp = None

    def verificar_login(self, username, password):
        try:
            # ⭐⭐ USAR CACHE DE USUÁRIOS
            usuarios = self._obter_usuarios_cache()
            
            for user_data in usuarios:
                if (user_data['login'] == username.strip() and 
                    user_data['senha'] == password.strip() and
                    user_data.get('status') == 'Ativo'):
                    
                    user_info = {
                        'login': user_data['login'],
                        'perfil': user_data['perfil'],
                        'nome_completo': user_data['nome_completo'],
                        'status': user_data.get('status', 'Ativo'),
                        'id': user_data.get('id', '')
                    }
                    
                    self.user_authenticated.emit(user_info, "")
                    return
            
            self.user_authenticated.emit({}, "Usuário ou senha incorretos")
            
        except Exception as e:
            self.user_authenticated.emit({}, f"Erro na autenticação: {str(e)}")

    def _obter_usuarios_cache(self):
        """Obtém usuários do cache ou do Firebase"""
        import time
        current_time = time.time()
        
        # ⭐⭐ CACHE DE 10 MINUTOS
        if (self._usuarios_cache and self._cache_timestamp and 
            (current_time - self._cache_timestamp) < 600):
            return self._usuarios_cache
        
        # Buscar do Firebase
        try:
            users = self.users_ref.stream()
            usuarios_list = []
            for doc in users:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                usuarios_list.append(user_data)
            
            self._usuarios_cache = usuarios_list
            self._cache_timestamp = current_time
            return usuarios_list
            
        except Exception as e:
            print(f"❌ Erro ao buscar usuários: {e}")
            return []

    def buscar_desenvolvedores_firebase(self):
        """Busca os dados dos desenvolvedores no Firebase - APENAS QUANDO SOLICITADO"""
        try:
            print("🔍 Buscando desenvolvedores no Firebase (sob demanda)...")
            
            # Referência para a subcoleção de membros
            membros_ref = self.db.collection('info').document('vQXIyU3YQhJcqff9TCoj').collection('Membros_da_Equipe')
            
            # ⭐⭐ BUSCAR APENAS QUANDO CHAMADO - LIMITAR A 10 DOCUMENTOS
            docs = membros_ref.limit(10).get()
            
            desenvolvedores = []
            
            for doc in docs:
                dados = doc.to_dict()
                print(f"🔍 Processando documento: {doc.id}")
                print(f"📋 Todos os campos encontrados: {list(dados.keys())}")
                
                # Identificar os membros principais
                membros_principais = {}
                
                for chave, valor in dados.items():
                    if chave.startswith('Membro_'):
                        partes = chave.split('_')
                        if len(partes) == 2 and partes[1].isdigit():
                            numero = partes[1]
                            membros_principais[numero] = valor
                
                # Se não encontrar membros principais, mostrar todos os campos
                if not membros_principais:
                    print("   ℹ️  Nenhum membro principal encontrado, mostrando todos os campos:")
                    for chave, valor in dados.items():
                        nome_campo = chave.replace('_', ' ').title()
                        desenvolvedores.append(f"  {nome_campo}: {valor}")
                    desenvolvedores.append("")  # Linha em branco entre documentos
                    continue
                
                # Processar cada membro principal
                for numero, nome in membros_principais.items():
                    print(f"   👤 Processando Membro_{numero}: {nome}")
                    
                    # Linha com o nome principal
                    desenvolvedores.append(f"• {nome}")
                    
                    # Buscar todos os campos relacionados a este membro
                    for chave, valor in dados.items():
                        if chave == f'Membro_{numero}':
                            continue  # Já usamos o nome principal
                        
                        nome_campo = chave.replace('_', ' ').title()
                        
                        # Se o campo começa com o número do membro, é específico dele
                        if chave.startswith(f'Membro_{numero}_'):
                            nome_campo_limpo = nome_campo.replace(f'Membro {numero} ', '')
                            desenvolvedores.append(f"  {nome_campo_limpo}: {valor}")
                        # Se não começa com "Membro_", é um campo geral
                        elif not chave.startswith('Membro_'):
                            desenvolvedores.append(f"  {nome_campo}: {valor}")
                    
                    desenvolvedores.append("")  # Linha em branco entre membros
            
            print(f"✅ Total de linhas formatadas: {len(desenvolvedores)}")
            
            return desenvolvedores if desenvolvedores else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar desenvolvedores do Firebase: {e}")
            return []