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
    
    def verificar_login(self, username, password):
        try:
            # Buscar usuário pelo login
            query = self.users_ref.where('login', '==', username.strip()).limit(1)
            results = query.get()
            
            if not results:
                self.user_authenticated.emit({}, "Usuário não encontrado")
                return
            
            user_doc = results[0]
            user_data = user_doc.to_dict()
            
            # Verificar senha
            if user_data['senha'] != password.strip():
                self.user_authenticated.emit({}, "Senha incorreta")
                return
            
            # Verificar status
            if user_data.get('status') != 'Ativo':
                self.user_authenticated.emit({}, "Usuário bloqueado ou inativo")
                return
            
            # Login bem-sucedido
            user_info = {
                'login': user_data['login'],
                'perfil': user_data['perfil'],
                'nome_completo': user_data['nome_completo'],
                'status': user_data.get('status', 'Ativo'),
                'id': user_doc.id
            }
            
            self.user_authenticated.emit(user_info, "")
            
        except Exception as e:
            self.user_authenticated.emit({}, f"Erro na autenticação: {str(e)}")
    
    def cadastrar_usuario(self, user_data):
        try:
            # Verificar se login já existe
            login_query = self.users_ref.where('login', '==', user_data['login'].strip()).limit(1)
            login_results = login_query.get()
            
            if login_results:
                self.user_registered.emit(False, "Login já existe")
                return
            
            # Verificar se nome completo já existe
            nome_query = self.users_ref.where('nome_completo', '==', user_data['nome_completo'].strip()).limit(1)
            nome_results = nome_query.get()
            
            if nome_results:
                self.user_registered.emit(False, "Nome completo já existe")
                return
            
            # Criar novo usuário
            new_user = UserModel(
                login=user_data['login'].strip(),
                senha=user_data['senha'],
                perfil=user_data['perfil'],
                nome_completo=user_data['nome_completo'].strip()
            )
            
            # Salvar no Firestore
            self.users_ref.add(new_user.to_dict())
            
            self.user_registered.emit(True, "Usuário cadastrado com sucesso!")
            
        except Exception as e:
            self.user_registered.emit(False, f"Erro no cadastro: {str(e)}")
    
    def listar_usuarios(self):
        try:
            users = self.users_ref.stream()
            return [doc.to_dict() for doc in users]
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
        

    def buscar_desenvolvedores_firebase(self):
        """Busca os dados dos desenvolvedores no Firebase - MOSTRA TODOS OS CAMPOS SEM PREVISÕES"""
        try:
            # Referência para a subcoleção de membros
            membros_ref = self.db.collection('info').document('vQXIyU3YQhJcqff9TCoj').collection('Membros_da_Equipe')
            
            # Buscar todos os documentos da subcoleção
            docs = membros_ref.stream()
            
            desenvolvedores = []
            
            for doc in docs:
                dados = doc.to_dict()
                print(f"🔍 Processando documento: {doc.id}")
                print(f"📋 Todos os campos encontrados: {list(dados.keys())}")
                
                # ⭐⭐ IDENTIFICAR OS MEMBROS PRINCIPAIS (Membro_1, Membro_2, etc.)
                membros_principais = {}
                
                for chave, valor in dados.items():
                    if chave.startswith('Membro_'):
                        # Verificar se é um campo de nome principal (não tem sufixo com underscore)
                        partes = chave.split('_')
                        if len(partes) == 2 and partes[1].isdigit():
                            # É um membro principal (Membro_1, Membro_2, etc.)
                            numero = partes[1]
                            membros_principais[numero] = valor
                
                # ⭐⭐ SE NÃO ENCONTRAR MEMBROS PRINCIPAIS, MOSTRAR TODOS OS CAMPOS DO DOCUMENTO
                if not membros_principais:
                    print("   ℹ️  Nenhum membro principal encontrado, mostrando todos os campos:")
                    for chave, valor in dados.items():
                        nome_campo = chave.replace('_', ' ').title()
                        desenvolvedores.append(f"  {nome_campo}: {valor}")
                    desenvolvedores.append("")  # Linha em branco entre documentos
                    continue
                
                # ⭐⭐ PROCESSAR CADA MEMBRO PRINCIPAL
                for numero, nome in membros_principais.items():
                    print(f"   👤 Processando Membro_{numero}: {nome}")
                    
                    # Linha com o nome principal
                    desenvolvedores.append(f"• {nome}")
                    
                    # ⭐⭐ BUSCAR TODOS OS CAMPOS RELACIONADOS A ESTE MEMBRO
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
                        # Se começa com "Membro_" mas é de outro membro, ignoramos
                        # (será processado quando chegar naquele membro)
                    
                    desenvolvedores.append("")  # Linha em branco entre membros
            
            print(f"✅ Total de linhas formatadas: {len(desenvolvedores)}")
            
            return desenvolvedores if desenvolvedores else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar desenvolvedores do Firebase: {e}")
            return []

    # NOVOS MÉTODOS PARA MANUTENÇÃO DE USUÁRIOS
    def listar_todos_usuarios(self):
        """Lista todos os usuários do sistema"""
        try:
            docs = self.users_ref.stream()
            
            usuarios = []
            for doc in docs:
                usuario_data = doc.to_dict()
                usuario_data['id'] = doc.id
                usuarios.append(usuario_data)
            
            return usuarios
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []

    def resetar_senha(self, login, nova_senha):
        """Reseta a senha de um usuário"""
        try:
            query = self.users_ref.where('login', '==', login)
            docs = query.get()
            
            if not docs:
                return False
            
            for doc in docs:
                doc.reference.update({'senha': nova_senha})
            
            return True
        except Exception as e:
            print(f"Erro ao resetar senha: {e}")
            return False

    def atualizar_usuario(self, login, dados_atualizados):
        """Atualiza os dados de um usuário"""
        try:
            query = self.users_ref.where('login', '==', login)
            docs = query.get()
            
            if not docs:
                return False
            
            for doc in docs:
                doc.reference.update(dados_atualizados)
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar usuário: {e}")
            return False