from datetime import datetime

class PropostaModel:
    def __init__(self, numero_proposta, analista, tipo_proposta, status="Pendente"):
        self.numero_proposta = numero_proposta
        self.analista = analista
        self.tipo_proposta = tipo_proposta  # "Saque Fácil", "Refin", "Saque Direcionado"
        self.status = status
        self.data_criacao = datetime.now()
        self.data_conclusao = None
        self.duracao_total = None
        self.tarefas_concluidas = {}  # Dicionário para armazenar tarefas concluídas
    
    def to_dict(self):
        return {
            'numero_proposta': self.numero_proposta,
            'analista': self.analista,
            'tipo_proposta': self.tipo_proposta,
            'status': self.status,
            'data_criacao': self.data_criacao,
            'data_conclusao': self.data_conclusao,
            'duracao_total': self.duracao_total,
            'tarefas_concluidas': self.tarefas_concluidas
        }
    
    def finalizar_proposta(self, status_final):
        self.status = status_final
        self.data_conclusao = datetime.now()
        
        # Calcular duração
        duracao = self.data_conclusao - self.data_criacao
        horas = duracao.seconds // 3600
        minutos = (duracao.seconds % 3600) // 60
        segundos = duracao.seconds % 60
        
        self.duracao_total = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
    @staticmethod
    def from_dict(data):
        proposta = PropostaModel(
            data['numero_proposta'],
            data['analista'],
            data['tipo_proposta'],
            data.get('status', 'Pendente')
        )
        proposta.data_criacao = data.get('data_criacao')
        proposta.data_conclusao = data.get('data_conclusao')
        proposta.duracao_total = data.get('duracao_total')
        proposta.tarefas_concluidas = data.get('tarefas_concluidas', {})
        return proposta