from datetime import datetime

class PropostaModel:
    def __init__(self, numero_proposta, analista, tipo_proposta):
        self.numero_proposta = numero_proposta
        self.analista = analista
        self.tipo_proposta = tipo_proposta
        self.data_criacao = datetime.now()
        self.data_conclusao = None
        self.duracao_total = None
        self.status = "Pendente"
        self.tarefas_concluidas = {}
    
    def finalizar_proposta(self, status):
        self.status = status
        self.data_conclusao = datetime.now()
        
        # Calcular duração se ambas as datas existirem
        if self.data_criacao and self.data_conclusao:
            duracao = self.data_conclusao - self.data_criacao
            horas = duracao.seconds // 3600
            minutos = (duracao.seconds % 3600) // 60
            segundos = duracao.seconds % 60
            self.duracao_total = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
    def to_dict(self):
        return {
            'numero_proposta': self.numero_proposta,
            'analista': self.analista,
            'tipo_proposta': self.tipo_proposta,
            'data_criacao': self.data_criacao,
            'data_conclusao': self.data_conclusao,
            'duracao_total': self.duracao_total,
            'status': self.status,
            'tarefas_concluidas': self.tarefas_concluidas
        }