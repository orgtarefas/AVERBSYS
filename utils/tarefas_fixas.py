# Tarefas fixas para cada tipo de proposta 
TAREFAS_SAQUE_FACIL = {
    "tarefa_1": "RECEITA FEDERAL - Nome do Titular",
    "tarefa_2": "RECEITA FEDERAL - Data de Nascimento", 
    "tarefa_3": "RECEITA FEDERAL - Situação do CPF",
    "tarefa_4": "QISTA - Duplicidade",
    "tarefa_5": "QISTA - Atraso de Saque",
    "tarefa_6": "CALCULADORA - Idade x Prazo",
    "tarefa_7": "ROTEIRO OPERACIONAL - Idade x Prazo",
    "tarefa_8": "GESTORA - Localizar Servidor",
    "tarefa_9": "GESTORA x ESPELHO PROPOSTA- Validar Matricula",
    "tarefa_10": "GESTORA x ESPELHO PROPOSTA- Orgão",
    "tarefa_11": "GESTORA x ESPELHO PROPOSTA- Empregador",
    "tarefa_12": "GESTORA - Tipo de Servidor",
    "tarefa_13": "PLATAFORMA PLENO - Data de Corte",
    "tarefa_14": "GESTORA - Pré reserva Saque",
    "tarefa_15": "GESTORA - Pré reserva Compras",
    "tarefa_16": "GESTORA - Confirmar reserva Saque",
    "tarefa_17": "GESTORA - Confirmar reserva Compra",
    "tarefa_18": "QISTA - Inserir Observação da Proposta",
    "tarefa_19": "QISTA - Integrar / Recusar Proposta"
}

TAREFAS_REFIN = {
    "tarefa_1": "RECEITA FEDERAL - Nome do Titular",
    "tarefa_2": "RECEITA FEDERAL - Data de Nascimento", 
    "tarefa_3": "RECEITA FEDERAL - Situação do CPF",
    "tarefa_4": "QISTA - Duplicidade",
    "tarefa_5": "QISTA - Atraso de Saque",
    "tarefa_6": "CALCULADORA - Idade x Prazo",
    "tarefa_7": "ROTEIRO OPERACIONAL - Idade x Prazo",
    "tarefa_8": "GESTORA - Localizar Servidor",
    "tarefa_9": "GESTORA x ESPELHO PROPOSTA- Validar Matricula",
    "tarefa_10": "GESTORA x ESPELHO PROPOSTA- Orgão",
    "tarefa_11": "GESTORA x ESPELHO PROPOSTA- Empregador",
    "tarefa_12": "GESTORA - Tipo de Servidor",
    "tarefa_13": "PLATAFORMA PLENO - Data de Corte",
    "tarefa_14": "QISTA -  Validar contratos elegíveis para operação",
    "tarefa_15": "ESPELHO DA PROPOSTA  x GESTORA -  Validar se contratos elegíveis foram todos contemplados",
    "tarefa_16": "GESTORA - Pré reserva Saque",
    "tarefa_17": "GESTORA - Pré reserva Compras",
    "tarefa_18": "GESTORA - Confirmar reserva Saque",
    "tarefa_19": "GESTORA - Confirmar reserva Compra",
    "tarefa_20": "QISTA - Inserir Observação da Proposta",
    "tarefa_21": "QISTA - Integrar / Recusar Proposta"
}


TAREFAS_SAQUE_DIRECIONADO = {
    "tarefa_1": "RECEITA FEDERAL - Nome do Titular",
    "tarefa_2": "RECEITA FEDERAL - Data de Nascimento", 
    "tarefa_3": "RECEITA FEDERAL - Situação do CPF",
    "tarefa_4": "QISTA - Duplicidade",
    "tarefa_5": "QISTA - Atraso de Saque",
    "tarefa_6": "CALCULADORA - Idade x Prazo",
    "tarefa_7": "ROTEIRO OPERACIONAL - Idade x Prazo",
    "tarefa_8": "GESTORA - Localizar Servidor",
    "tarefa_9": "GESTORA x ESPELHO PROPOSTA- Validar Matricula",
    "tarefa_10": "GESTORA x ESPELHO PROPOSTA- Orgão",
    "tarefa_11": "GESTORA x ESPELHO PROPOSTA- Empregador",
    "tarefa_12": "GESTORA - Tipo de Servidor",
    "tarefa_13": "PLATAFORMA PLENO - Data de Corte",
    "tarefa_14": "QISTA -  Validar contratos elegíveis para operação",
    "tarefa_15": "ESPELHO DA PROPOSTA  x GESTORA -  Validar se contratos elegíveis foram todos contemplados",
    "tarefa_16": "GESTORA - Pré reserva Saque",
    "tarefa_17": "GESTORA - Pré reserva Compras",
    "tarefa_18": "GESTORA - Confirmar reserva Saque",
    "tarefa_19": "GESTORA - Confirmar reserva Compra",
    "tarefa_20": "QISTA - Inserir Observação da Proposta",
    "tarefa_21": "QISTA - Integrar / Recusar Proposta"
}

TAREFAS_SOLICITAÇÃO_INTERNA = {
    "tarefa_1": "RECEITA FEDERAL - Nome do Titular",
    "tarefa_2": "RECEITA FEDERAL - Data de Nascimento", 
    "tarefa_8": "GESTORA - Localizar Servidor",
    "tarefa_9": "GESTORA x ESPELHO PROPOSTA- Validar Matricula",
    "tarefa_10": "GESTORA x ESPELHO PROPOSTA- Orgão",
    "tarefa_11": "GESTORA x ESPELHO PROPOSTA- Empregador",
    "tarefa_12": "GESTORA - Tipo de Servidor",
    "tarefa_13": "QISTA -  Validar contratos elegíveis para ajustes",
    "tarefa_14": "QISTA -  Validar novo prazo",
    "tarefa_15": "QISTA -  Validar novo valor liberado",
    "tarefa_16": "GESTORA - validar margem suficiente para ajuste",
    "tarefa_17": "GESTORA - liquidar parcela incorreta",
    "tarefa_18": "GESTORA - Pré reserva Saque",
    "tarefa_19": "GESTORA - Confirmar reserva Saque"
}    

def get_tarefas_por_tipo(tipo_proposta):
    """Retorna as tarefas específicas para cada tipo de proposta"""
    tarefas_map = {
        'Saque Fácil': TAREFAS_SAQUE_FACIL,
        'Refin': TAREFAS_REFIN, 
        'Saque Direcionado': TAREFAS_SAQUE_DIRECIONADO,
        'Solicitação Interna': TAREFAS_SOLICITAÇÃO_INTERNA
    }
    return tarefas_map.get(tipo_proposta, {})