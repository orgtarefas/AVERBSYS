import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

# Inicializar o Firebase
def inicializar_firebase():
    try:
        # Verificar se o Firebase já foi inicializado
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Erro ao inicializar Firebase: {e}")
        return None

# Função para ler todos os dados da coleção LOGINS_AVERBSYS
def ler_todos_logins():
    db = inicializar_firebase()
    if db is None:
        return None
    
    try:
        # Fazer uma única leitura de todos os documentos da coleção
        logins_ref = db.collection('LOGINS_AVERBSYS')
        documentos = logins_ref.stream()
        
        dados_logins = []
        
        for doc in documentos:
            dados_doc = doc.to_dict()
            dados_doc['id'] = doc.id  # Adicionar o ID do documento
            dados_logins.append(dados_doc)
            
            # Exibir os dados no console
            print(f"\n=== Documento: {doc.id} ===")
            for campo, valor in dados_doc.items():
                print(f"{campo}: {valor}")
        
        print(f"\nTotal de documentos lidos: {len(dados_logins)}")
        return dados_logins
        
    except Exception as e:
        print(f"Erro ao ler dados do Firebase: {e}")
        return None

# Função principal
def main():
    print("Iniciando leitura da coleção LOGINS_AVERBSYS...")
    print("=" * 50)
    
    dados = ler_todos_logins()
    
    if dados:
        print(f"\nLeitura concluída com sucesso!")
        print(f"Foram encontrados {len(dados)} documento(s) na coleção.")
    else:
        print("\nFalha na leitura dos dados.")

if __name__ == "__main__":
    main()