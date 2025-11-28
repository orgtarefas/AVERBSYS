import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import re

# Inicializar o Firebase
def inicializar_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey2.json")
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Erro ao inicializar Firebase: {e}")
        return None

# Função para ler APENAS 1 documento com TODOS os dados
def ler_todos_dados():
    db = inicializar_firebase()
    if db is None:
        return None
    
    try:
        print("🔍 Fazendo UMA leitura no banco...")
        
        # APENAS 1 LEITURA: Pegar o documento específico
        doc_ref = db.collection('logins').document('LOGINS_AVERBSYS')
        documento = doc_ref.get()
        
        if documento.exists:
            dados = documento.to_dict()
            print("✅ LEITURA ÚNICA REALIZADA COM SUCESSO!")
            print(f"📄 Documento: LOGINS_AVERBSYS")
            print(f"📊 Total de campos encontrados: {len(dados)}")
            print("\n" + "="*60)
            
            # Organizar os dados dinamicamente
            membros = {}
            usuarios = {}
            outros = {}
            
            for campo, valor in dados.items():
                # Identificar membros
                if campo.startswith('Membro_'):
                    num = campo.split('_')[1]
                    if num not in membros:
                        membros[num] = {}
                    if 'Cargo' in campo:
                        membros[num]['cargo'] = valor
                    elif 'nome' in campo:
                        membros[num]['nome'] = valor
                
                # Identificar usuários dinamicamente (user_1, user_2, user_3...)
                elif campo.startswith('user_'):
                    parts = campo.split('_')
                    if len(parts) >= 3:
                        user_num = parts[1]
                        campo_type = '_'.join(parts[2:])
                        
                        if user_num not in usuarios:
                            usuarios[user_num] = {}
                        usuarios[user_num][campo_type] = valor
                
                # Outros campos
                else:
                    outros[campo] = valor
            
            # Exibir membros
            if membros:
                print("\n👥 DADOS DOS MEMBROS:")
                for num, info in sorted(membros.items()):
                    if 'cargo' in info and 'nome' in info:
                        print(f"   {info['cargo']}: {info['nome']}")
            
            # Exibir usuários dinamicamente
            if usuarios:
                print(f"\n👤 USUÁRIOS ENCONTRADOS ({len(usuarios)}):")
                for num, user_data in sorted(usuarios.items()):
                    print(f"\n   Usuário {num}:")
                    print(f"      Login: {user_data.get('logiin', 'N/A')}")
                    print(f"      Nome: {user_data.get('nome_completo', 'N/A')}")
                    print(f"      Perfil: {user_data.get('perfil', 'N/A')}")
                    print(f"      Status: {user_data.get('status', 'N/A')}")
                    print(f"      Data Cadastro: {user_data.get('data_cadastro', 'N/A')}")
            
            # Exibir outros campos
            if outros:
                print(f"\n📋 OUTRAS INFORMAÇÕES:")
                for campo, valor in outros.items():
                    print(f"   {campo}: {valor}")
            
            print(f"\n📈 RESUMO:")
            print(f"   • Membros: {len(membros)}")
            print(f"   • Usuários: {len(usuarios)}")
            print(f"   • Campos totais: {len(dados)}")
            
            return dados
            
        else:
            print("❌ Documento 'LOGINS_AVERBSYS' não encontrado!")
            return None
        
    except Exception as e:
        print(f"❌ Erro ao ler dados do Firebase: {e}")
        return None

# Função para usar os dados no sistema
def processar_dados(dados):
    if not dados:
        return
    
    print("\n🔄 PROCESSANDO DADOS PARA USO NO SISTEMA...")
    
    # Exemplo: Criar lista de usuários para login
    usuarios_login = []
    
    for campo, valor in dados.items():
        if campo.startswith('user_') and campo.endswith('_logiin'):
            user_num = campo.split('_')[1]
            usuario = {
                'login': valor,
                'nome': dados.get(f'user_{user_num}_nome_completo', ''),
                'perfil': dados.get(f'user_{user_num}_perfil', ''),
                'status': dados.get(f'user_{user_num}_status', ''),
                'senha': dados.get(f'user_{user_num}_senha', '')
            }
            usuarios_login.append(usuario)
    
    print(f"👤 Usuários carregados para sistema: {len(usuarios_login)}")
    for usuario in usuarios_login:
        print(f"   → {usuario['login']} ({usuario['perfil']}) - {usuario['status']}")

# Função principal
def main():
    print("🚀 INICIANDO LEITURA ÚNICA DO BANCO")
    print("=" * 50)
    
    # APENAS 1 LEITURA aqui
    dados = ler_todos_dados()
    
    if dados:
        print(f"\n🎯 DADOS CARREGADOS COM SUCESSO EM 1 LEITURA!")
        
        # Processar os dados para uso
        processar_dados(dados)
    else:
        print("\n❌ Falha ao carregar dados.")

if __name__ == "__main__":
    main()