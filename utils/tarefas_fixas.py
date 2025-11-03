# Tarefas fixas para cada tipo de proposta
TAREFAS_SAQUE_FACIL = {
    "tarefa_1": "Verificar elegibilidade do cliente",
    "tarefa_2": "Confirmar documentação completa", 
    "tarefa_3": "Validar score de crédito",
    "tarefa_4": "Analisar histórico bancário",
    "tarefa_5": "Verificar limite disponível",
    "tarefa_6": "Confirmar taxa de juros",
    "tarefa_7": "Validar prazo de pagamento",
    "tarefa_8": "Emitir contrato digital"
}

TAREFAS_REFIN = {
    "tarefa_1": "Analisar proposta atual",
    "tarefa_2": "Verificar histórico de pagamentos",
    "tarefa_3": "Calcular nova taxa de juros",
    "tarefa_4": "Validar documentação para refin",
    "tarefa_5": "Simular novas condições",
    "tarefa_6": "Verificar elegibilidade para melhoria",
    "tarefa_7": "Confirmar redução de parcelas",
    "tarefa_8": "Emitir nova proposta"
}

TAREFAS_SAQUE_DIRECIONADO = {
    "tarefa_1": "Identificar finalidade do saque",
    "tarefa_2": "Validar destino dos recursos", 
    "tarefa_3": "Verificar documentação específica",
    "tarefa_4": "Analisar compatibilidade com produto",
    "tarefa_5": "Confirmar limites setoriais",
    "tarefa_6": "Validar restrições legais",
    "tarefa_7": "Verificar aprovação prévia",
    "tarefa_8": "Emitir autorização direcionada"
}

def get_tarefas_por_tipo(tipo_proposta):
    """Retorna as tarefas específicas para cada tipo de proposta"""
    tarefas_map = {
        'Saque Fácil': TAREFAS_SAQUE_FACIL,
        'Refin': TAREFAS_REFIN, 
        'Saque Direcionado': TAREFAS_SAQUE_DIRECIONADO
    }
    return tarefas_map.get(tipo_proposta, {})