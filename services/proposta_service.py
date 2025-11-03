from config.firebase_config import FirebaseManager
from models.proposta_model import PropostaModel
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime

class PropostaService(QObject):
    proposta_criada = pyqtSignal(bool, str)
    proposta_atualizada = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        try:
            self.firebase = FirebaseManager()
            self.db = self.firebase.get_db()
            # Coleções separadas para cada tipo de proposta
            self.colecoes = {
                'Saque Fácil': self.db.collection('tarefas1_saquefacil'),
                'Refin': self.db.collection('tarefas2_refin'),
                'Saque Direcionado': self.db.collection('tarefas3_saquedirecionado')
            }
            print("✅ PropostaService inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar PropostaService: {e}")
            raise
    
    def criar_e_finalizar_proposta(self, numero_proposta, analista, tipo_proposta, tarefas_concluidas, status):
        """Cria a proposta e já finaliza com o status"""
        try:
            colecao = self.colecoes[tipo_proposta]
            
            # Verificar se número já existe
            query = colecao.where('numero_proposta', '==', numero_proposta)
            resultados = list(query.limit(1).get())
            
            if resultados:
                self.proposta_criada.emit(False, "Número da proposta já existe!")
                return
            
            # Criar nova proposta
            nova_proposta = PropostaModel(numero_proposta, analista, tipo_proposta)
            nova_proposta.tarefas_concluidas = tarefas_concluidas
            nova_proposta.finalizar_proposta(status)  # Já finaliza com o status
            
            # Salvar na coleção específica
            colecao.add(nova_proposta.to_dict())
            
            self.proposta_criada.emit(True, f"Proposta {status} com sucesso!")
            
        except Exception as e:
            self.proposta_criada.emit(False, f"Erro ao criar proposta: {str(e)}")
    
    def listar_propostas_por_analista(self, analista, tipo_proposta=None):
        try:
            propostas = []
            
            if tipo_proposta:
                # Listar de uma coleção específica
                colecao = self.colecoes[tipo_proposta]
                query = colecao.where('analista', '==', analista)
                resultados = query.get()
                
                for doc in resultados:
                    proposta_data = doc.to_dict()
                    proposta_data['id'] = doc.id
                    propostas.append(proposta_data)
            else:
                # Listar de todas as coleções
                for tipo, colecao in self.colecoes.items():
                    query = colecao.where('analista', '==', analista)
                    resultados = query.get()
                    
                    for doc in resultados:
                        proposta_data = doc.to_dict()
                        proposta_data['id'] = doc.id
                        propostas.append(proposta_data)
            
            # Ordenar por data (mais recente primeiro)
            propostas.sort(key=lambda x: x.get('data_criacao', datetime.min), reverse=True)
            
            return propostas
            
        except Exception as e:
            print(f"Erro ao listar propostas: {e}")
            return []
    
    def listar_todas_propostas(self, tipo_proposta=None):
        try:
            propostas = []
            
            if tipo_proposta:
                # Listar de uma coleção específica
                colecao = self.colecoes[tipo_proposta]
                query = colecao.order_by('data_criacao', direction='DESCENDING')
                resultados = query.limit(100).get()
                
                for doc in resultados:
                    proposta_data = doc.to_dict()
                    proposta_data['id'] = doc.id
                    propostas.append(proposta_data)
            else:
                # Listar de todas as coleções
                for tipo, colecao in self.colecoes.items():
                    query = colecao.order_by('data_criacao', direction='DESCENDING')
                    resultados = query.limit(50).get()
                    
                    for doc in resultados:
                        proposta_data = doc.to_dict()
                        proposta_data['id'] = doc.id
                        propostas.append(proposta_data)
            
            return propostas
            
        except Exception as e:
            print(f"Erro ao listar propostas: {e}")
            return []