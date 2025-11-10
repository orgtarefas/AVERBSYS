def get_motivos_recusa():
    """Retorna a lista completa de motivos de recusa"""
    return [
        ("101", "MARGEM"),
        ("102", "VÍNCULO/CATEGORIA"),
        ("103", "POLÍTICA DE IDADE"),
        ("104", "ÓRGÃO"),
        ("105", "EMPREGADOR"),
        ("106", "MATRÍCULA"),
        ("107", "SERVIDOR NÃO LOCALIZADO"),
        ("108", "CONTRATO EM ATRASO FUNÇÃO"),
        ("109", "LIBERAR DADOS FUNCIONAIS"),
        ("110", "CARGO"),
        ("111", "PROBLEMAS NA AVERBAÇÃO"),
        ("112", "PORTAL INDISPONÍVEL"),
        ("113", "TROCA DE PROCESSADORA"),
        ("114", "VALIDAÇÃO DE VÍNCULO"),
        ("115", "VALIDAÇÃO DE ÓRGÃO"),
        ("116", "AGUARDANDO ANUÊNCIA"),
        ("117", "NOME DIVERGENTE"),
        ("118", "SITUAÇÃO CPF IRREGULAR"),
        ("119", "DATA DE NASCIMENTO INCORRETA"),
        ("120", "IDADE X PRAZO"),
        ("121", "ATRELADO A OUTRA CONSIGNATÁRIA"),
        ("122", "REFIN CONTEMPLAR CONTRATOS EM ABERTOS"),
        ("123", "REFIN PARCELAS BAIXADAS"),
        ("124", "TEMPO MINÍMO DE VÍNCULO"),
        ("125", "VALOR DA OPERAÇÃO MAIOR DO QUE O PERMITIDO")
    ]

def get_motivo_por_id(motivo_id):
    """Retorna a descrição de um motivo específico pelo ID"""
    motivos = get_motivos_recusa()
    for id_motivo, descricao in motivos:
        if id_motivo == motivo_id:
            return descricao
    return None

def get_motivo_por_descricao(descricao):
    """Retorna o ID de um motivo específico pela descrição"""
    motivos = get_motivos_recusa()
    for id_motivo, desc in motivos:
        if desc == descricao:
            return id_motivo
    return None