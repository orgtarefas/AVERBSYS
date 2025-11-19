from config.firebase_config import FirebaseManager
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime, time
from google.cloud.firestore_v1 import FieldFilter
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PropostaService(QObject):
    proposta_criada = pyqtSignal(bool, str)
    proposta_atualizada = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        try:
            self.firebase = FirebaseManager()
            self.db = self.firebase.get_db()
            self.colecoes = {
                'Saque Fácil': self.db.collection('tarefas1_saquefacil'),
                'Refin': self.db.collection('tarefas2_refin'),
                'Saque Direcionado': self.db.collection('tarefas3_saquedirecionado')
            }
            print("✅ PropostaService inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar PropostaService: {e}")
            raise

    def obter_versao_sistema(self):
        """Obtém a versão do sistema da coleção 'info' no Firebase"""
        try:
            # Buscar a coleção 'info'
            info_ref = self.db.collection('info')
            docs = info_ref.limit(1).get()
            
            for doc in docs:
                info_data = doc.to_dict()
                versao = info_data.get('ver')
                print(f"🔍 Versão encontrada no Firebase: {versao}")
                return versao
            
            print("❌ Nenhuma versão encontrada na coleção 'info'")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar versão do sistema: {e}")
            return None        
    
    def criar_e_finalizar_proposta(self, numero_proposta, analista, tipo_proposta, 
                                    tarefas_concluidas, status, data_criacao, 
                                    data_conclusao, duracao_total, dados_filtro=None):
        """
        Cria e finaliza uma proposta na coleção correta baseada no tipo
        """
        try:
            # ⭐⭐ CORREÇÃO: MAPEAMENTO CORRETO DAS COLEÇÕES ⭐⭐
            colecoes_map = {
                'Saque Fácil': 'tarefas1_saquefacil',
                'Refin': 'tarefas2_refin', 
                'Saque Direcionado': 'tarefas3_saquedirecionado',
                'Solicitação Interna': 'tarefas4_solicitacao_interna',  # ⭐⭐ CORRETO
                'Saque Fácil - Reanalise': 'tarefas1_saquefacil',
                'Refin - Reanalise': 'tarefas2_refin',
                'Saque Direcionado - Reanalise': 'tarefas3_saquedirecionado'
            }
            
            colecao = colecoes_map.get(tipo_proposta)
            

            if not colecao:
                # ⭐⭐ CORREÇÃO: Não usar fallback, mostrar erro
                error_msg = f"Tipo de proposta não mapeado: {tipo_proposta}"
                print(f"❌ {error_msg}")
                self.proposta_criada.emit(False, error_msg)
                return
            
            
            # Processar dados dos filtros
            filtros_processados = {}
            if dados_filtro:
                print(f"📍 Dados dos filtros:")
                for key, value in dados_filtro.items():
                    # Garantir que valores None sejam convertidos para string vazia
                    valor_final = value if value is not None else ""
                    filtros_processados[key] = valor_final
                    print(f"   {key}: {valor_final}")
            else:
                print("📍 Nenhum dado de filtro fornecido")
                # Inicializar com valores padrão
                filtros_processados = {
                    'regiao': '',
                    'convenio': '',
                    'produto': '',
                    'status': '',
                    'motivo_recusa_id': '',
                    'motivo_recusa_descricao': '',
                    'tipo_recusa': ''  # NOVO CAMPO
                }
            
            # Se for recusa e tiver motivo, adicionar tipo de recusa
            if status == "Recusada":
                motivo_id = filtros_processados.get('motivo_recusa_id', '')
                motivo_desc = filtros_processados.get('motivo_recusa_descricao', '')
                
                if motivo_id and motivo_desc:
                    # Criar string do tipo de recusa
                    tipo_recusa = f"{motivo_id} - {motivo_desc}"
                    filtros_processados['tipo_recusa'] = tipo_recusa
                    print(f"   Motivo de Recusa: {tipo_recusa}")
                
                # Garantir que os campos existam mesmo se vazios
                if 'motivo_recusa_id' not in filtros_processados:
                    filtros_processados['motivo_recusa_id'] = ''
                if 'motivo_recusa_descricao' not in filtros_processados:
                    filtros_processados['motivo_recusa_descricao'] = ''
                if 'tipo_recusa' not in filtros_processados:
                    filtros_processados['tipo_recusa'] = ''
            
            proposta_data = {
                'numero_proposta': numero_proposta,
                'analista': analista,
                'tipo_proposta': tipo_proposta,
                'tarefas_concluidas': tarefas_concluidas,
                'status': status,
                'data_criacao': data_criacao,
                'data_conclusao': data_conclusao,
                'duracao_total': duracao_total,
                'dados_filtro': filtros_processados,  # Agora inclui tipo_recusa
                'timestamp': datetime.now()
            }
            
            # Salvar na coleção correta
            doc_ref = self.db.collection(colecao).document()
            doc_ref.set(proposta_data)
            
            print(f"✅ Contrato {numero_proposta} salvo com sucesso na coleção {colecao}")
            print(f"📊 Dados dos filtros salvos: {filtros_processados}")
            self.proposta_criada.emit(True, f"Contrato {numero_proposta} {status} com sucesso!")
            
        except Exception as e:
            print(f"❌ ERRO AO SALVAR PROPOSTA: {e}")
            import traceback
            print(f"🔍 TRACEBACK COMPLETO:")
            traceback.print_exc()
            self.proposta_criada.emit(False, f"Erro ao salvar proposta: {str(e)}")
    
    def listar_propostas_por_analista(self, analista):
        """Lista todas as propostas de um analista específico"""
        try:
            propostas = []
            
            for colecao in self.colecoes.values():
                # Buscar todas as propostas da coleção
                docs = colecao.limit(500).get()
                
                for doc in docs:
                    proposta_data = doc.to_dict()
                    proposta_data['id'] = doc.id
                    
                    # Converter timestamps do Firestore para datetime
                    proposta_data = self._converter_datas_proposta(proposta_data)
                    
                    # GARANTIR QUE DADOS_FILTRO EXISTE
                    if 'dados_filtro' not in proposta_data:
                        proposta_data['dados_filtro'] = {
                            'regiao': '',
                            'convenio': '',
                            'produto': '',
                            'status': ''
                        }
                    else:
                        # Garantir que todos os campos existem no dados_filtro
                        dados_filtro = proposta_data['dados_filtro']
                        campos_necessarios = ['regiao', 'convenio', 'produto', 'status']
                        for campo in campos_necessarios:
                            if campo not in dados_filtro:
                                dados_filtro[campo] = ''
                    
                    # Filtrar por analista localmente
                    if proposta_data.get('analista') == analista:
                        propostas.append(proposta_data)
            
            # Ordenar por data (mais recente primeiro)
            propostas.sort(key=lambda x: self._converter_para_datetime(x.get('data_criacao')), reverse=True)
            
            return propostas
            
        except Exception as e:
            print(f"Erro ao listar propostas por analista: {e}")
            return []
        
    def listar_todas_propostas(self):
        """Lista todas as propostas do sistema"""
        try:
            print("📋 Buscando todas as propostas no Firebase...")
            
            propostas = []
            
            # ⭐⭐ USAR AS COLEÇÕES REAIS DO SEU FIREBASE ⭐⭐
            colecoes_reais = {
                'tarefas1_saquefacil': 'Saque Fácil',
                'tarefas2_refin': 'Refin', 
                'tarefas3_saquedirecionado': 'Saque Direcionado',
                'tarefas4_solicitacao_interna': 'Solicitação Interna'  # Se existir
            }
            
            for colecao_nome, tipo_proposta in colecoes_reais.items():
                try:
                    docs = self.db.collection(colecao_nome).get()
                    
                    for doc in docs:
                        proposta_data = doc.to_dict()
                        
                        # Converter datas
                        proposta_data = self._converter_datas_proposta(proposta_data)
                        
                        # Garantir que dados_filtro existe
                        if 'dados_filtro' not in proposta_data:
                            proposta_data['dados_filtro'] = {
                                'regiao': '', 'convenio': '', 'produto': '', 'status': '',
                                'cpf': '', 'valor_liberado': '', 'prazo': '', 'observacoes': '',
                                'valor_troco': '', 'motivo_recusa_descricao': ''
                            }
                        
                        proposta_formatada = {
                            'id': doc.id,
                            'numero_proposta': proposta_data.get('numero_proposta', doc.id),
                            'analista': proposta_data.get('analista', ''),
                            'tipo_proposta': proposta_data.get('tipo_proposta', tipo_proposta),
                            'status': proposta_data.get('status', ''),
                            'data_criacao': proposta_data.get('data_criacao'),
                            'data_conclusao': proposta_data.get('data_conclusao'),
                            'duracao_total': proposta_data.get('duracao_total', ''),
                            'dados_filtro': proposta_data.get('dados_filtro', {})
                        }
                        
                        propostas.append(proposta_formatada)

                        
                except Exception as e:
                    print(f"❌ Erro ao buscar na coleção {colecao_nome}: {e}")
                    continue
            
            print(f"✅ Total de {len(propostas)} propostas encontradas")
            
            # Mostrar estatísticas
            if propostas:
                tipos = {}
                status_count = {}
                for proposta in propostas:
                    tipo = proposta['tipo_proposta']
                    status = proposta['status']
                    tipos[tipo] = tipos.get(tipo, 0) + 1
                    status_count[status] = status_count.get(status, 0) + 1
                
                print("📊 Estatísticas das propostas:")
                for tipo, count in tipos.items():
                    print(f"   • {tipo}: {count} propostas")
                for status, count in status_count.items():
                    print(f"   • Status '{status}': {count} propostas")
            
            return propostas
            
        except Exception as e:
            print(f"❌ Erro ao listar propostas: {e}")
            import traceback
            traceback.print_exc()
            return []
        
    def listar_propostas_com_filtros(self, data_inicio=None, data_fim=None, analista=None, tipo_proposta=None):
        """Lista propostas com filtros aplicados - versão sem índices compostos"""
        try:
            propostas = []
            
            colecoes_a_buscar = []
            if tipo_proposta:
                colecoes_a_buscar = [self.colecoes[tipo_proposta]]
            else:
                colecoes_a_buscar = self.colecoes.values()
            
            for colecao in colecoes_a_buscar:
                # Primeiro filtro: por data
                query_data = colecao
                
                # Aplicar filtro por data
                if data_inicio:
                    if isinstance(data_inicio, datetime):
                        data_inicio_dt = data_inicio
                    else:
                        data_inicio_dt = datetime.combine(data_inicio, time.min)
                    # Tornar timezone-aware
                    data_inicio_dt = self._make_timezone_aware(data_inicio_dt)
                    query_data = query_data.where(filter=FieldFilter('data_criacao', '>=', data_inicio_dt))
                
                if data_fim:
                    if isinstance(data_fim, datetime):
                        data_fim_dt = data_fim
                    else:
                        data_fim_dt = datetime.combine(data_fim, time.max)
                    # Tornar timezone-aware
                    data_fim_dt = self._make_timezone_aware(data_fim_dt)
                    query_data = query_data.where(filter=FieldFilter('data_criacao', '<=', data_fim_dt))
                
                # Executar query de data primeiro
                resultados_data = query_data.limit(500).get()
                
                # Aplicar filtro por analista localmente (para evitar índices compostos)
                for doc in resultados_data:
                    proposta_data = doc.to_dict()
                    proposta_data['id'] = doc.id
                    
                    # Converter timestamps do Firestore para datetime
                    proposta_data = self._converter_datas_proposta(proposta_data)
                    
                    # GARANTIR QUE DADOS_FILTRO EXISTE
                    if 'dados_filtro' not in proposta_data:
                        proposta_data['dados_filtro'] = {
                            'regiao': '',
                            'convenio': '',
                            'produto': '',
                            'status': ''
                        }
                    else:
                        # Garantir que todos os campos existem no dados_filtro
                        dados_filtro = proposta_data['dados_filtro']
                        campos_necessarios = ['regiao', 'convenio', 'produto', 'status']
                        for campo in campos_necessarios:
                            if campo not in dados_filtro:
                                dados_filtro[campo] = ''
                    
                    # Aplicar filtro de analista localmente
                    if analista:
                        if proposta_data.get('analista') == analista:
                            propostas.append(proposta_data)
                    else:
                        propostas.append(proposta_data)
            
            # Ordenar por data (mais recente primeiro)
            propostas.sort(key=lambda x: self._converter_para_datetime(x.get('data_criacao')), reverse=True)
            
            return propostas
            
        except Exception as e:
            print(f"Erro ao listar propostas com filtros: {e}")
            return []
    
    # services/proposta_service.py (MÉTODO MELHORADO)
    def listar_propostas_simples_filtro(self, data_inicio=None, data_fim=None, analista=None):
        """Lista propostas com filtros simples para o histórico - VERSÃO MELHORADA"""
        try:
            print(f"🔍 Filtrando propostas - Data: {data_inicio} a {data_fim}, Analista: {analista}")
            
            todas_propostas = self.listar_todas_propostas()
            propostas_filtradas = []
            
            for proposta in todas_propostas:
                # Converter data_criacao se for string
                data_criacao = proposta.get('data_criacao')
                if isinstance(data_criacao, str):
                    try:
                        data_criacao = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            data_criacao = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
                        except:
                            continue
                
                # Aplicar filtro de data
                if data_inicio and data_criacao:
                    if hasattr(data_criacao, 'date'):
                        data_criacao_date = data_criacao.date()
                    else:
                        data_criacao_date = data_criacao
                        
                    if data_criacao_date < data_inicio:
                        continue
                
                if data_fim and data_criacao:
                    if hasattr(data_criacao, 'date'):
                        data_criacao_date = data_criacao.date()
                    else:
                        data_criacao_date = data_criacao
                        
                    if data_criacao_date > data_fim:
                        continue
                
                # Aplicar filtro de analista
                if analista and analista != "todos":
                    if proposta.get('analista') != analista:
                        continue
                
                propostas_filtradas.append(proposta)
            
            print(f"✅ {len(propostas_filtradas)} propostas após filtro")
            return propostas_filtradas
            
        except Exception as e:
            print(f"❌ Erro ao filtrar propostas: {e}")
            import traceback
            traceback.print_exc()
            return []
        
    def _converter_datas_proposta(self, proposta_data):
        """Converte as datas do Firestore para objetos Python datetime"""
        try:
            # Converter data_criacao
            if 'data_criacao' in proposta_data:
                data_criacao = proposta_data['data_criacao']
                # Para DatetimeWithNanoseconds, usar diretamente
                if hasattr(data_criacao, 'year'):  # Já é um objeto datetime-like
                    proposta_data['data_criacao'] = data_criacao
                elif hasattr(data_criacao, 'timestamp'):
                    # Para objetos timestamp do Firestore
                    proposta_data['data_criacao'] = data_criacao.to_pydatetime()
                elif isinstance(data_criacao, str):
                    # Tentar converter string para datetime
                    try:
                        proposta_data['data_criacao'] = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
                    except:
                        # Tentar outros formatos
                        try:
                            proposta_data['data_criacao'] = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
                        except:
                            pass
            
            # Converter data_conclusao
            if 'data_conclusao' in proposta_data:
                data_conclusao = proposta_data['data_conclusao']
                # Para DatetimeWithNanoseconds, usar diretamente
                if hasattr(data_conclusao, 'year'):  # Já é um objeto datetime-like
                    proposta_data['data_conclusao'] = data_conclusao
                elif hasattr(data_conclusao, 'timestamp'):
                    # Para objetos timestamp do Firestore
                    proposta_data['data_conclusao'] = data_conclusao.to_pydatetime()
                elif isinstance(data_conclusao, str):
                    # Tentar converter string para datetime
                    try:
                        proposta_data['data_conclusao'] = datetime.strptime(data_conclusao, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            proposta_data['data_conclusao'] = datetime.fromisoformat(data_conclusao.replace('Z', '+00:00'))
                        except:
                            pass
            
            return proposta_data
            
        except Exception as e:
            print(f"Erro ao converter datas: {e}")
            return proposta_data
    
    def _converter_para_datetime(self, data):
        """Converte uma data para datetime para ordenação"""
        if data is None:
            return datetime.min.replace(tzinfo=None)
        
        # Se já for datetime, retornar
        if isinstance(data, datetime):
            return data.replace(tzinfo=None) if data.tzinfo else data
        
        # Para DatetimeWithNanoseconds do Firestore
        if hasattr(data, 'year'):
            try:
                # Tentar converter para datetime simples
                return datetime(
                    data.year, data.month, data.day,
                    data.hour, data.minute, data.second,
                    data.microsecond
                )
            except:
                return datetime.min.replace(tzinfo=None)
        
        if hasattr(data, 'timestamp'):
            return data.to_pydatetime().replace(tzinfo=None)
        
        if isinstance(data, str):
            try:
                return datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    dt = datetime.fromisoformat(data.replace('Z', '+00:00'))
                    return dt.replace(tzinfo=None)
                except:
                    pass
        
        return datetime.min.replace(tzinfo=None)
    
    def _make_timezone_aware(self, dt):
        """Converte datetime para timezone-aware se necessário"""
        if dt.tzinfo is None:
            # Adicionar UTC como timezone padrão
            from datetime import timezone
            return dt.replace(tzinfo=timezone.utc)
        return dt
    

    
    
    def verificar_proposta_existente(self, numero_proposta):
        """Verifica se uma proposta já existe em qualquer coleção"""
        try:
            for colecao in self.colecoes.values():
                # Buscar por número da proposta
                docs = colecao.where(filter=FieldFilter('numero_proposta', '==', numero_proposta)).limit(1).get()
                
                for doc in docs:
                    proposta_data = doc.to_dict()
                    proposta_data['id'] = doc.id
                    
                    # Converter timestamps do Firestore para datetime
                    proposta_data = self._converter_datas_proposta(proposta_data)
                    
                    # GARANTIR QUE DADOS_FILTRO EXISTE
                    if 'dados_filtro' not in proposta_data:
                        proposta_data['dados_filtro'] = {
                            'regiao': '',
                            'convenio': '',
                            'produto': '',
                            'status': ''
                        }
                    else:
                        # Garantir que todos os campos existem no dados_filtro
                        dados_filtro = proposta_data['dados_filtro']
                        campos_necessarios = ['regiao', 'convenio', 'produto', 'status']
                        for campo in campos_necessarios:
                            if campo not in dados_filtro:
                                dados_filtro[campo] = ''
                    
                    return proposta_data
            
            return None
            
        except Exception as e:
            print(f"Erro ao verificar proposta existente: {e}")
            return None
        
    def obter_dados_tma(self, data_inicio, data_fim, analista, user_data):
        """Obtém dados para cálculo do TMA - VERSÃO FIREBASE CORRIGIDA"""
        try:
            print(f"🔍 Buscando dados TMA - Período: {data_inicio} a {data_fim}, Analista: {analista}")
            
            # Coleções do Firebase
            colecoes_reais = {
                'tarefas1_saquefacil': 'Saque Fácil',
                'tarefas2_refin': 'Refin', 
                'tarefas3_saquedirecionado': 'Saque Direcionado',
                'tarefas4_solicitacao_interna': 'Solicitação Interna'
            }
            
            dados_agrupados = {}
            total_propostas_processadas = 0
            
            for colecao_nome, tipo_proposta in colecoes_reais.items():
                try:
                    # Buscar documentos na coleção
                    docs = self.db.collection(colecao_nome).get()
                    
                    for doc in docs:
                        proposta_data = doc.to_dict()
                        
                        # Converter datas
                        proposta_data = self._converter_datas_proposta(proposta_data)
                        
                        # ⭐⭐ CORREÇÃO: Aceitar apenas status "Aprovada" e "Recusada"
                        status_proposta = proposta_data.get('status', '')
                        if status_proposta not in ['Aprovada', 'Recusada']:
                            continue
                        
                        # Filtrar por data de conclusão
                        data_conclusao = proposta_data.get('data_conclusao')
                        if not data_conclusao:
                            print(f"   ⚠️ Proposta sem data_conclusao: {proposta_data.get('numero_proposta', '')}")
                            continue
                        
                        # Converter para string para comparação
                        if hasattr(data_conclusao, 'strftime'):
                            data_conclusao_str = data_conclusao.strftime('%Y-%m-%d')
                        else:
                            data_conclusao_str = str(data_conclusao)
                        
                        # Aplicar filtro de data
                        if data_conclusao_str < data_inicio or data_conclusao_str > data_fim:
                            continue
                        
                        # Filtrar por analista
                        analista_proposta = proposta_data.get('analista', '')
                        perfil = user_data.get('perfil', '').lower()
                        
                        if analista and analista != 'todos':
                            if analista_proposta != analista:
                                continue
                        elif perfil not in ['gerente', 'dev']:
                            # Para outros perfis, mostra apenas seu próprio login
                            login_atual = user_data.get('login', '')
                            if analista_proposta != login_atual:
                                continue
                        
                        # Calcular duração em segundos
                        duracao = proposta_data.get('duracao_total', '00:00:00')
                        segundos = self._converter_duracao_para_segundos(duracao)
                        
                        # Agrupar por analista
                        if analista_proposta not in dados_agrupados:
                            dados_agrupados[analista_proposta] = {
                                'qtd_contratos': 0,
                                'duracao_total': 0
                            }
                        
                        dados_agrupados[analista_proposta]['qtd_contratos'] += 1
                        dados_agrupados[analista_proposta]['duracao_total'] += segundos
                        total_propostas_processadas += 1
                        
                        # DEBUG: Mostrar proposta processada
                        print(f"   ✅ Proposta processada: {analista_proposta} - {proposta_data.get('numero_proposta', '')} - Status: {status_proposta} - Duração: {duracao} ({segundos} segundos) - Data: {data_conclusao_str}")
                        
                except Exception as e:
                    print(f"❌ Erro ao processar coleção {colecao_nome}: {e}")
                    continue
            
            # Converter para o formato esperado
            dados_tma = []
            for analista_nome, dados in dados_agrupados.items():
                dados_tma.append({
                    'analista': analista_nome,
                    'qtd_contratos': dados['qtd_contratos'],
                    'duracao_total': dados['duracao_total']
                })
            
            # Ordenar por nome do analista
            dados_tma.sort(key=lambda x: x['analista'])
            
            print(f"✅ Dados TMA encontrados: {len(dados_tma)} analistas, {total_propostas_processadas} propostas processadas")
            for item in dados_tma:
                tma_formatado = self.calcular_tma_formatado(item['duracao_total'], item['qtd_contratos'])
                print(f"   • {item['analista']}: {item['qtd_contratos']} contratos, {self.formatar_duracao(item['duracao_total'])} total, TMA: {tma_formatado}")
            
            return dados_tma
            
        except Exception as e:
            print(f"❌ Erro ao obter dados TMA: {e}")
            import traceback
            traceback.print_exc()
            return []

    def calcular_tma_formatado(self, duracao_total_segundos, qtd_contratos):
        """Calcula o TMA formatado para debug"""
        if qtd_contratos == 0:
            return "00:00:00"
        
        tma_segundos = duracao_total_segundos / qtd_contratos
        horas = int(tma_segundos // 3600)
        minutos = int((tma_segundos % 3600) // 60)
        segundos = int(tma_segundos % 60)
        
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    def formatar_duracao(self, segundos):
        """Formata segundos para HH:MM:SS (para debug)"""
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos = int(segundos % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


    def _converter_duracao_para_segundos(self, duracao_str):
        """Converte string de duração (HH:MM:SS) para segundos"""
        try:
            if not duracao_str:
                return 0
                
            partes = str(duracao_str).split(':')
            if len(partes) == 3:
                horas = int(partes[0])
                minutos = int(partes[1])
                segundos = int(partes[2])
                return horas * 3600 + minutos * 60 + segundos
            elif len(partes) == 2:
                minutos = int(partes[0])
                segundos = int(partes[1])
                return minutos * 60 + segundos
            else:
                return int(duracao_str) if duracao_str.isdigit() else 0
        except:
            return 0

    def obter_analistas_tma(self):
        """Obtém lista de analistas para TMA (apenas Gerentes e Devs) - VERSÃO FIREBASE"""
        try:
            # Buscar usuários diretamente do Firebase
            usuarios_ref = self.db.collection('usuarios')
            docs = usuarios_ref.get()
            
            analistas = []
            for doc in docs:
                usuario_data = doc.to_dict()
                perfil = usuario_data.get('perfil', '').lower()
                status = usuario_data.get('status', '').lower()
                
                # Filtrar apenas Gerentes e Devs ativos
                if perfil in ['gerente', 'dev'] and status == 'ativo':
                    login = usuario_data.get('login', '')
                    if login:
                        analistas.append({'login': login})
            
            # Ordenar por login
            analistas.sort(key=lambda x: x['login'])
            
            print(f"✅ Analistas TMA encontrados: {len(analistas)}")
            for analista in analistas:
                print(f"   • {analista['login']}")
            
            return analistas
            
        except Exception as e:
            print(f"❌ Erro ao obter analistas TMA: {e}")
            return []