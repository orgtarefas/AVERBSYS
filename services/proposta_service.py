from config.firebase_config import FirebaseManager
from models.proposta_model import PropostaModel
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
                'Saque Direcionado': self.db.collection('tarefas3_saquedirecionado'),
                'Solicitação Interna': self.db.collection('tarefas4_solicitacao_interna')  # ⭐⭐ ADICIONADO
            }
            print("✅ PropostaService inicializado com sucesso!")
            print(f"📚 Coleções disponíveis: {list(self.colecoes.keys())}")
        except Exception as e:
            print(f"❌ Erro ao inicializar PropostaService: {e}")
            raise
    

    def criar_e_finalizar_proposta(self, numero_proposta, analista, tipo_proposta, 
                                        tarefas_concluidas, status, data_criacao, 
                                        data_conclusao, duracao_total, dados_filtro=None):
        """
        Cria e finaliza uma proposta na coleção correta baseada no tipo
        Inclui todos os novos campos: CPF, Valor Liberado, Prazo, Observações, Valor de Troco
        """
        try:
            # Mapear tipo de proposta para coleção
            colecoes_map = {
                'Saque Fácil': 'tarefas1_saquefacil',
                'Refin': 'tarefas2_refin', 
                'Saque Direcionado': 'tarefas3_saquedirecionado',
                'Solicitação Interna': 'tarefas4_solicitacao_interna',
                'Saque Fácil - Reanalise': 'tarefas1_saquefacil',
                'Refin - Reanalise': 'tarefas2_refin',
                'Saque Direcionado - Reanalise': 'tarefas3_saquedirecionado',
                'Solicitação Interna - Reanalise': 'tarefas4_solicitacao_interna'
            }
            
            colecao = colecoes_map.get(tipo_proposta)
            if not colecao:
                # Fallback: usar primeira coleção
                colecao = 'tarefas1_saquefacil'
                print(f"⚠️  Tipo de proposta não mapeado: {tipo_proposta}, usando coleção: {colecao}")
            
            print(f"💾 Salvando proposta na coleção: {colecao}")
            print(f"📋 Dados da proposta:")
            print(f"   Número: {numero_proposta}")
            print(f"   Analista: {analista}")
            print(f"   Tipo: {tipo_proposta}")
            print(f"   Status: {status}")
            print(f"   Data criação: {data_criacao}")
            print(f"   Data conclusão: {data_conclusao}")
            print(f"   Duração: {duracao_total}")
            print(f"   Tarefas: {tarefas_concluidas}")
            
            # Processar dados dos filtros
            filtros_processados = {}
            if dados_filtro:
                print(f"📍 Dados dos filtros:")
                
                # ⭐⭐ CAMPOS OBRIGATÓRIOS DOS FILTROS
                campos_obrigatorios = ['regiao', 'convenio', 'produto', 'status']
                for campo in campos_obrigatorios:
                    valor = dados_filtro.get(campo, '')
                    filtros_processados[campo] = valor if valor is not None else ""
                    print(f"   {campo}: {filtros_processados[campo]}")
                
                # ⭐⭐ NOVOS CAMPOS ADICIONAIS
                campos_adicionais = [
                    'cpf', 'valor_liberado', 'moeda', 'prazo', 'unidade_prazo', 
                    'observacoes', 'valor_troco', 'moeda_troco'
                ]
                
                for campo in campos_adicionais:
                    valor = dados_filtro.get(campo, '')
                    filtros_processados[campo] = valor if valor is not None else ""
                    if valor:  # Só printa se tiver valor
                        print(f"   {campo}: {valor}")
                
                # Campos de motivo de recusa
                campos_recusa = ['motivo_recusa_id', 'motivo_recusa_descricao']
                for campo in campos_recusa:
                    valor = dados_filtro.get(campo, '')
                    filtros_processados[campo] = valor if valor is not None else ""
                
            else:
                print("📍 Nenhum dado de filtro fornecido")
                # Inicializar com valores padrão para todos os campos
                filtros_processados = {
                    # Campos obrigatórios
                    'regiao': '',
                    'convenio': '',
                    'produto': '',
                    'status': '',
                    
                    # ⭐⭐ NOVOS CAMPOS
                    'cpf': '',
                    'valor_liberado': '',
                    'moeda': 'R$',
                    'prazo': '',
                    'unidade_prazo': 'Meses',
                    'observacoes': '',
                    'valor_troco': '',
                    'moeda_troco': 'R$',
                    
                    # Campos de recusa
                    'motivo_recusa_id': '',
                    'motivo_recusa_descricao': '',
                    'tipo_recusa': ''
                }
            
            # ⭐⭐ GARANTIR VALORES PADRÃO PARA OS NOVOS CAMPOS SE NÃO FORNECIDOS
            if 'moeda' not in filtros_processados or not filtros_processados['moeda']:
                filtros_processados['moeda'] = 'R$'
            if 'unidade_prazo' not in filtros_processados or not filtros_processados['unidade_prazo']:
                filtros_processados['unidade_prazo'] = 'Meses'
            if 'moeda_troco' not in filtros_processados or not filtros_processados['moeda_troco']:
                filtros_processados['moeda_troco'] = 'R$'
            
            # ⭐⭐ GARANTIR QUE TIPO_RECUSA EXISTE SEMPRE (mesmo para aprovações)
            if 'tipo_recusa' not in filtros_processados:
                filtros_processados['tipo_recusa'] = ''
            
            # Se for recusa e tiver motivo, adicionar tipo de recusa
            if status == "Recusada":
                motivo_id = filtros_processados.get('motivo_recusa_id', '')
                motivo_desc = filtros_processados.get('motivo_recusa_descricao', '')
                
                if motivo_id and motivo_desc:
                    # Criar string do tipo de recusa
                    tipo_recusa = f"{motivo_id} - {motivo_desc}"
                    filtros_processados['tipo_recusa'] = tipo_recusa
                    print(f"   Motivo de Recusa: {tipo_recusa}")
                else:
                    filtros_processados['tipo_recusa'] = ''
                
                # Garantir que os campos existam mesmo se vazios
                if 'motivo_recusa_id' not in filtros_processados:
                    filtros_processados['motivo_recusa_id'] = ''
                if 'motivo_recusa_descricao' not in filtros_processados:
                    filtros_processados['motivo_recusa_descricao'] = ''
            
            # ⭐⭐ MONTAR DADOS COMPLETOS DA PROPOSTA
            proposta_data = {
                'numero_proposta': numero_proposta,
                'analista': analista,
                'tipo_proposta': tipo_proposta,
                'tarefas_concluidas': tarefas_concluidas,
                'status': status,
                'data_criacao': data_criacao,
                'data_conclusao': data_conclusao,
                'duracao_total': duracao_total,
                'dados_filtro': filtros_processados,  # Inclui todos os novos campos
                'timestamp': datetime.now()
            }
            
            # ⭐⭐ VALIDAÇÃO FINAL DOS DADOS
            print(f"🔍 VALIDAÇÃO FINAL DOS DADOS:")
            print(f"   ✅ Número: {proposta_data['numero_proposta']}")
            print(f"   ✅ Analista: {proposta_data['analista']}")
            print(f"   ✅ Tipo: {proposta_data['tipo_proposta']}")
            print(f"   ✅ Status: {proposta_data['status']}")
            print(f"   ✅ CPF: {filtros_processados.get('cpf', 'N/A')}")
            print(f"   ✅ Valor Liberado: {filtros_processados.get('valor_liberado', 'N/A')} {filtros_processados.get('moeda', 'R$')}")
            print(f"   ✅ Prazo: {filtros_processados.get('prazo', 'N/A')} {filtros_processados.get('unidade_prazo', 'Meses')}")
            print(f"   ✅ Observações: {filtros_processados.get('observacoes', 'N/A')}")
            
            # Verificar se tem Valor de Troco (apenas para Refin e Solicitação Interna)
            if tipo_proposta in ["Refin", "Solicitação Interna", "Refin - Reanalise", "Solicitação Interna - Reanalise"]:
                valor_troco = filtros_processados.get('valor_troco', '')
                print(f"   ✅ Valor de Troco: {valor_troco} {filtros_processados.get('moeda_troco', 'R$')}")
            
            # ⭐⭐ VERIFICAR SE A COLEÇÃO EXISTE NO DB
            print(f"🔍 Verificando acesso à coleção {colecao}...")
            try:
                # Tentar acessar a coleção para ver se existe
                teste_docs = self.db.collection(colecao).limit(1).get()
                print(f"✅ Coleção {colecao} acessível, {len(teste_docs)} documentos encontrados")
            except Exception as e:
                print(f"⚠️  Aviso ao acessar coleção {colecao}: {e}")
            
            # Salvar na coleção correta
            print(f"💾 Iniciando salvamento na coleção {colecao}...")
            doc_ref = self.db.collection(colecao).document()
            doc_ref.set(proposta_data)
            
            print(f"✅ Proposta {numero_proposta} salva com sucesso na coleção {colecao}")
            print(f"📊 Todos os dados dos filtros salvos:")
            for key, value in filtros_processados.items():
                if value:  # Só mostra campos com valor
                    print(f"   📍 {key}: {value}")
            
            self.proposta_criada.emit(True, f"Proposta {numero_proposta} {status} com sucesso!")
            
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
        """Lista todas as propostas de todas as coleções"""
        try:
            propostas = []
            
            for colecao in self.colecoes.values():
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
                    
                    propostas.append(proposta_data)
            
            # Ordenar por data (mais recente primeiro)
            propostas.sort(key=lambda x: self._converter_para_datetime(x.get('data_criacao')), reverse=True)
            
            return propostas
            
        except Exception as e:
            print(f"Erro ao listar todas as propostas: {e}")
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
    
    def listar_propostas_simples_filtro(self, data_inicio=None, data_fim=None, analista=None, tipo_proposta=None):
        """Versão alternativa mais simples para filtros"""
        try:
            # ⭐⭐ CORREÇÃO: Remover o parâmetro tipo_proposta da chamada
            # Primeiro, buscar todas as propostas sem filtros complexos
            todas_propostas = self.listar_todas_propostas()
            
            # Aplicar filtros localmente
            propostas_filtradas = []
            
            for proposta in todas_propostas:
                # Filtro por tipo de proposta (se especificado)
                if tipo_proposta and proposta.get('tipo_proposta') != tipo_proposta:
                    continue
                
                # Filtro por data
                data_criacao = self._converter_para_datetime(proposta.get('data_criacao'))
                
                if data_inicio:
                    data_inicio_dt = data_inicio if isinstance(data_inicio, datetime) else datetime.combine(data_inicio, time.min)
                    # Tornar ambas as datas timezone-aware para comparação
                    data_inicio_dt = self._make_timezone_aware(data_inicio_dt)
                    data_criacao = self._make_timezone_aware(data_criacao)
                    
                    if data_criacao < data_inicio_dt:
                        continue
                
                if data_fim:
                    data_fim_dt = data_fim if isinstance(data_fim, datetime) else datetime.combine(data_fim, time.max)
                    # Tornar ambas as datas timezone-aware para comparação
                    data_fim_dt = self._make_timezone_aware(data_fim_dt)
                    data_criacao = self._make_timezone_aware(data_criacao)
                    
                    if data_criacao > data_fim_dt:
                        continue
                
                # Filtro por analista
                if analista and proposta.get('analista') != analista:
                    continue
                
                propostas_filtradas.append(proposta)
            
            # Ordenar por data
            propostas_filtradas.sort(key=lambda x: self._converter_para_datetime(x.get('data_criacao')), reverse=True)
            
            print(f"✅ Histórico filtrado: {len(propostas_filtradas)} propostas encontradas")
            
            return propostas_filtradas
            
        except Exception as e:
            print(f"❌ Erro ao listar propostas com filtros simples: {e}")
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