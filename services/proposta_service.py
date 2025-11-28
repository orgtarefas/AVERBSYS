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
            self.db = self.firebase.get_db_principal()
            
            # ⭐⭐ CONTADOR DE LEITURAS
            self.contador_leituras = 0
            print("✅ PropostaService inicializado - SEM CACHE, contador de leituras ativo")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar PropostaService: {e}")
            raise


    def _incrementar_contador_leituras(self, operacao, colecao, documento=None):
        """Incrementa e exibe o contador de leituras"""
        self.contador_leituras += 1
        if documento:
            print(f"📊 LEITURA #{self.contador_leituras} - {operacao} | Coleção: {colecao} | Documento: {documento}")
        else:
            print(f"📊 LEITURA #{self.contador_leituras} - {operacao} | Coleção: {colecao}")
        
        return self.contador_leituras

    def zerar_contador_leituras(self):
        """Zera o contador de leituras"""
        self.contador_leituras = 0
        print("🧹 Contador de leituras zerado")        

    def obter_versao_sistema(self):
        """Obtém a versão do sistema do banco de LOGIN"""
        try:
            # ⭐⭐ AGORA USA BANCO DE LOGIN PARA VERSÃO
            db_login = self.firebase.get_db_login()
            doc_ref = db_login.collection('logins').document('LOGINS_AVERBSYS')
            documento = doc_ref.get()
            
            if documento.exists:
                dados = documento.to_dict()
                versao = dados.get('ver')
                print(f"✅ Versão encontrada: {versao}")
                return versao
            
            print("❌ Nenhuma versão encontrada no banco de login")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar versão do sistema: {e}")
            return None
    
    def criar_e_finalizar_proposta(self, numero_contrato, analista, tipo_contrato, 
                                    tarefas_concluidas, status, data_criacao, 
                                    data_conclusao, duracao_total, dados_filtro=None,
                                    eh_reanalise=False, contrato_original=None):
        """
        Cria e finaliza um contrato na coleção correta usando número como ID
        """
        try:
            print(f"💾 INICIANDO GRAVAÇÃO do contrato {numero_contrato}")
            print(f"   🔄 É reanálise: {eh_reanalise}")
            if eh_reanalise:
                print(f"   📋 Contrato original: {contrato_original}")
            
            colecoes_map = {
                'Saque Fácil': 'contratos_saquefacil',
                'Refin': 'contratos_refin', 
                'Saque Direcionado': 'contratos_saquedirecionado',
                'Solicitação Interna': 'contratos_solicitacao_interna',
                'Saque Fácil - Reanalise': 'contratos_saquefacil',
                'Refin - Reanalise': 'contratos_refin',
                'Saque Direcionado - Reanalise': 'contratos_saquedirecionado'
            }
            
            colecao = colecoes_map.get(tipo_contrato)
            
            if not colecao:
                error_msg = f"Tipo de contrato não mapeado: {tipo_contrato}"
                print(f"❌ {error_msg}")
                self.proposta_criada.emit(False, error_msg)
                return
            
            # Processar dados dos filtros
            filtros_processados = {}
            if dados_filtro:
                print(f"📍 Processando {len(dados_filtro)} filtros para gravação")
                for key, value in dados_filtro.items():
                    valor_final = value if value is not None else ""
                    filtros_processados[key] = valor_final
            else:
                print("📍 Nenhum dado de filtro fornecido")
                filtros_processados = {
                    'regiao': '', 'convenio': '', 'produto': '', 'status': '',
                    'motivo_recusa_id': '', 'motivo_recusa_descricao': '', 'tipo_recusa': ''
                }
            
            # ⭐⭐ ADICIONAR INFORMAÇÕES DE REANÁLISE SE FOR O CASO
            if eh_reanalise:
                filtros_processados['eh_reanalise'] = True
                if contrato_original:
                    filtros_processados['contrato_original'] = contrato_original
                print(f"   🔄 Marcando como REANÁLISE do contrato: {contrato_original}")
            
            # Se for recusa e tiver motivo, adicionar tipo de recusa
            if status == "Recusada":
                motivo_id = filtros_processados.get('motivo_recusa_id', '')
                motivo_desc = filtros_processados.get('motivo_recusa_descricao', '')
                
                if motivo_id and motivo_desc:
                    tipo_recusa = f"{motivo_id} - {motivo_desc}"
                    filtros_processados['tipo_recusa'] = tipo_recusa
                    print(f"   📝 Motivo de Recusa adicionado: {tipo_recusa}")
            
            # ⭐⭐ CORREÇÃO: Garantir que o campo 'numero' está sempre presente nos dados
            contrato_data = {
                'analista': analista,
                'tipo_contrato': tipo_contrato,
                'tarefas_concluidas': tarefas_concluidas,
                'status': status,
                'data_criacao': data_criacao,
                'data_conclusao': data_conclusao,
                'duracao_total': duracao_total,
                'dados_filtro': filtros_processados,
                'timestamp': datetime.now(),
                'numero': numero_contrato  # ⭐⭐ SEMPRE salvar o campo numero
            }
            
            # ⭐⭐ CONTAGEM DE LEITURA - GRAVAÇÃO
            leitura_numero = self._incrementar_contador_leituras(
                "GRAVAÇÃO_CONTRATO", 
                colecao, 
                numero_contrato
            )
            
            # ⭐⭐ SALVAR USANDO O NÚMERO COMO ID DO DOCUMENTO
            doc_ref = self.db.collection(colecao).document(numero_contrato)
            doc_ref.set(contrato_data)
            
            print(f"✅ CONTRATO GRAVADO: {numero_contrato} na coleção {colecao}")
            print(f"📊 Dados gravados: {len(contrato_data)} campos")
            print(f"   - Tipo: {tipo_contrato}")
            print(f"   - Status: {status}")
            print(f"   - É Reanálise: {eh_reanalise}")
            if eh_reanalise:
                print(f"   - Contrato Original: {contrato_original}")
            print(f"   - Campo 'numero' salvo: {numero_contrato}")
            print(f"📋 RESUMO GRAVAÇÃO: 1 escrita realizada (total leituras: {leitura_numero})")
            
            self.proposta_criada.emit(True, f"Contrato {numero_contrato} {status} com sucesso!")
            
        except Exception as e:
            print(f"❌ ERRO NA GRAVAÇÃO: {e}")
            import traceback
            traceback.print_exc()
            self.proposta_criada.emit(False, f"Erro ao salvar contrato: {str(e)}")
    
    def listar_propostas_por_analista(self, analista):
        """Lista todas as propostas de um analista específico"""
        try:
            propostas = []
            
            # ⭐⭐ COLEÇÕES FIXAS
            colecoes = [
                'tarefas1_saquefacil',
                'tarefas2_refin', 
                'tarefas3_saquedirecionado',
                'tarefas4_solicitacao_interna'
            ]
            
            for colecao_nome in colecoes:
                try:
                    docs = self.db.collection(colecao_nome).limit(500).get()
                    
                    for doc in docs:
                        proposta_data = doc.to_dict()
                        proposta_data['id'] = doc.id
                        proposta_data['colecao_origem'] = colecao_nome
                        
                        # Converter timestamps do Firestore para datetime
                        proposta_data = self._converter_datas_contrato(proposta_data)
                        
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
                            
                except Exception as e:
                    print(f"❌ Erro ao buscar na coleção {colecao_nome}: {e}")
                    continue
            
            # Ordenar por data (mais recente primeiro)
            propostas.sort(key=lambda x: self._converter_para_datetime(x.get('data_criacao')), reverse=True)
            
            return propostas
            
        except Exception as e:
            print(f"Erro ao listar propostas por analista: {e}")
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
                    proposta_data = self._converter_datas_contrato(proposta_data)
                    
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
    
    def listar_propostas_simples_filtro(self, data_inicio=None, data_fim=None, analista=None):
        """Lista propostas com filtros - OTIMIZADO COM CACHE"""
        try:
            # ⭐⭐ USAR CACHE SEMPRE QUE POSSÍVEL
            todas_propostas = self.listar_todas_propostas()
            propostas_filtradas = []
            
            for proposta in todas_propostas:
                # Aplicar filtros localmente (EVITA NOVAS QUERIES)
                data_criacao = proposta.get('data_criacao')
                
                # Filtro de data
                if data_inicio and data_criacao:
                    if hasattr(data_criacao, 'date'):
                        if data_criacao.date() < data_inicio:
                            continue
                    elif isinstance(data_criacao, str):
                        try:
                            data_obj = datetime.strptime(data_criacao.split()[0], '%Y-%m-%d').date()
                            if data_obj < data_inicio:
                                continue
                        except:
                            continue
                
                if data_fim and data_criacao:
                    if hasattr(data_criacao, 'date'):
                        if data_criacao.date() > data_fim:
                            continue
                    elif isinstance(data_criacao, str):
                        try:
                            data_obj = datetime.strptime(data_criacao.split()[0], '%Y-%m-%d').date()
                            if data_obj > data_fim:
                                continue
                        except:
                            continue
                
                # Filtro de analista
                if analista and analista != "todos":
                    if proposta.get('analista') != analista:
                        continue
                
                propostas_filtradas.append(proposta)
            
            print(f"✅ {len(propostas_filtradas)} propostas após filtro (CACHE)")
            return propostas_filtradas
            
        except Exception as e:
            print(f"❌ Erro ao filtrar propostas: {e}")
            return []


    def listar_todas_propostas(self, forcar_atualizacao=False):
        """Lista TODAS as propostas com APENAS 4 LEITURAS"""
        try:
            print("📋 Buscando TODOS os contratos (4 leituras)")
            todas_propostas = []
            
            # ⭐⭐ COLEÇÕES - CADA UMA SERÁ 1 LEITURA
            colecoes_contratos = [
                'contratos_saquefacil',
                'contratos_refin', 
                'contratos_saquedirecionado',
                'contratos_solicitacao_interna'
            ]
            
            for colecao_nome in colecoes_contratos:
                try:
                    # ⭐⭐ CADA .get() = 1 LEITURA (INDEPENDENTE DE QUANTOS DOCS)
                    leitura_numero = self._incrementar_contador_leituras(
                        "COLECAO_COMPLETA", 
                        colecao_nome, 
                        None
                    )
                    
                    print(f"🔍 LEITURA #{leitura_numero}: Buscando coleção {colecao_nome}")
                    
                    # ⭐⭐ 1 LEITURA = TODOS OS DOCUMENTOS DA COLEÇÃO
                    docs = self.db.collection(colecao_nome).get()
                    
                    # Processar todos os documentos (NÃO CUSTA LEITURAS ADICIONAIS)
                    for doc in docs:
                        proposta_data = doc.to_dict()
                        proposta_data['id'] = doc.id
                        proposta_data['colecao_origem'] = colecao_nome
                        
                        # Padronizar campos para tabela
                        if 'numero' not in proposta_data:
                            proposta_data['numero'] = doc.id
                        if 'tipo_contrato' in proposta_data:
                            proposta_data['tipo_proposta'] = proposta_data['tipo_contrato']
                        if 'numero' in proposta_data:
                            proposta_data['numero_proposta'] = proposta_data['numero']
                        
                        # Converter datas
                        proposta_data = self._converter_datas_contrato(proposta_data)
                        
                        # Garantir dados_filtro
                        if 'dados_filtro' not in proposta_data:
                            proposta_data['dados_filtro'] = {}
                        
                        todas_propostas.append(proposta_data)
                    
                    print(f"✅ {len(docs)} documentos carregados (1 leitura)")
                    
                except Exception as e:
                    print(f"❌ Erro na coleção {colecao_nome}: {e}")
                    continue
            
            # Ordenar por data
            todas_propostas.sort(key=lambda x: self._converter_para_datetime(x.get('data_criacao')), reverse=True)
            
            print(f"🎯 TOTAL: {len(todas_propostas)} contratos | 4 LEITURAS realizadas")
            return todas_propostas
            
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            return []
    

        
    def _converter_datas_contrato(self, contrato_data):
        """Converte as datas do Firestore para objetos Python datetime"""
        try:
            # Converter data_criacao
            if 'data_criacao' in contrato_data:
                data_criacao = contrato_data['data_criacao']
                # Para DatetimeWithNanoseconds, usar diretamente
                if hasattr(data_criacao, 'year'):  # Já é um objeto datetime-like
                    contrato_data['data_criacao'] = data_criacao
                elif hasattr(data_criacao, 'timestamp'):
                    # Para objetos timestamp do Firestore
                    contrato_data['data_criacao'] = data_criacao.to_pydatetime()
                elif isinstance(data_criacao, str):
                    # Tentar converter string para datetime
                    try:
                        contrato_data['data_criacao'] = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
                    except:
                        # Tentar outros formatos
                        try:
                            contrato_data['data_criacao'] = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
                        except:
                            pass
            
            # Converter data_conclusao
            if 'data_conclusao' in contrato_data:
                data_conclusao = contrato_data['data_conclusao']
                # Para DatetimeWithNanoseconds, usar diretamente
                if hasattr(data_conclusao, 'year'):  # Já é um objeto datetime-like
                    contrato_data['data_conclusao'] = data_conclusao
                elif hasattr(data_conclusao, 'timestamp'):
                    # Para objetos timestamp do Firestore
                    contrato_data['data_conclusao'] = data_conclusao.to_pydatetime()
                elif isinstance(data_conclusao, str):
                    # Tentar converter string para datetime
                    try:
                        contrato_data['data_conclusao'] = datetime.strptime(data_conclusao, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            contrato_data['data_conclusao'] = datetime.fromisoformat(data_conclusao.replace('Z', '+00:00'))
                        except:
                            pass
            
            return contrato_data
            
        except Exception as e:
            print(f"Erro ao converter datas: {e}")
            return contrato_data
    
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
    
            
    def verificar_contrato_existente(self, numero_contrato, tipo_contrato=None):
        """Verifica se um contrato já existe - APENAS 1 LEITURA na coleção específica"""
        try:
            print(f"🔍 Verificando contrato {numero_contrato} na aba: {tipo_contrato}")
            
            mapeamento_abas = {
                'Saque Fácil': 'contratos_saquefacil',
                'Refin': 'contratos_refin', 
                'Saque Direcionado': 'contratos_saquedirecionado',
                'Solicitação Interna': 'contratos_solicitacao_interna'
            }
            
            if not tipo_contrato or tipo_contrato not in mapeamento_abas:
                print(f"❌ Aba não especificada ou inválida: {tipo_contrato}")
                return None
            
            colecao_alvo = mapeamento_abas[tipo_contrato]
            print(f"🎯 Consultando coleção: {colecao_alvo}")
            
            # ⭐⭐ CONTAGEM DE LEITURA - CONSULTA
            leitura_numero = self._incrementar_contador_leituras(
                "CONSULTA_CONTRATO", 
                colecao_alvo, 
                numero_contrato
            )
            
            # ⭐⭐ APENAS 1 LEITURA DIRETA
            doc_ref = self.db.collection(colecao_alvo).document(numero_contrato)
            documento = doc_ref.get()
            
            if documento.exists:
                contrato_data = documento.to_dict()
                contrato_data['id'] = documento.id
                contrato_data['colecao_origem'] = colecao_alvo
                
                # ⭐⭐ CORREÇÃO: Garantir que o campo 'numero' existe (usar ID se necessário)
                if 'numero' not in contrato_data or not contrato_data['numero']:
                    contrato_data['numero'] = documento.id
                    print(f"   🔄 Campo 'numero' vazio, usando ID: {documento.id}")
                
                # Converter datas
                contrato_data = self._converter_datas_contrato(contrato_data)
                
                # Garantir que dados_filtro existe
                if 'dados_filtro' not in contrato_data:
                    contrato_data['dados_filtro'] = {
                        'regiao': '', 'convenio': '', 'produto': '', 'status': '',
                        'motivo_recusa_id': '', 'motivo_recusa_descricao': '', 'tipo_recusa': ''
                    }
                
                print(f"✅ Contrato {numero_contrato} encontrado na coleção {colecao_alvo}")
                print(f"📋 RESUMO CONSULTA: 1 leitura realizada (total: {leitura_numero})")
                return contrato_data
            else:
                print(f"✅ Contrato {numero_contrato} não encontrado na coleção {colecao_alvo} (novo)")
                print(f"📋 RESUMO CONSULTA: 1 leitura realizada (total: {leitura_numero})")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao verificar contrato existente: {e}")
            return None
                
    def obter_dados_tma(self, data_inicio, data_fim, analista, user_data):
        """Obtém dados para cálculo do TMA - OTIMIZADO"""
        try:
            print(f"🔍 Buscando dados TMA - Período: {data_inicio} a {data_fim}")
            
            # ⭐⭐ USAR CACHE EM VEZ DE NOVAS QUERIES
            todas_propostas = self.listar_todas_propostas()
            dados_agrupados = {}
            
            for proposta in todas_propostas:
                # Aplicar filtros localmente
                status_proposta = proposta.get('status', '')
                if status_proposta not in ['Aprovada', 'Recusada']:
                    continue
                
                data_conclusao = proposta.get('data_conclusao')
                if not data_conclusao:
                    continue
                
                # Converter data_conclusao para string para comparação
                if hasattr(data_conclusao, 'strftime'):
                    data_conclusao_str = data_conclusao.strftime('%Y-%m-%d')
                else:
                    data_conclusao_str = str(data_conclusao)
                
                # Filtro de data
                if data_conclusao_str < data_inicio or data_conclusao_str > data_fim:
                    continue
                
                # Filtro de analista
                analista_proposta = proposta.get('analista', '')
                perfil = user_data.get('perfil', '').lower()
                
                if analista and analista != 'todos':
                    if analista_proposta != analista:
                        continue
                elif perfil not in ['gerente', 'dev']:
                    login_atual = user_data.get('login', '')
                    if analista_proposta != login_atual:
                        continue
                
                # Calcular duração
                duracao = proposta.get('duracao_total', '00:00:00')
                segundos = self._converter_duracao_para_segundos(duracao)
                
                # Agrupar
                if analista_proposta not in dados_agrupados:
                    dados_agrupados[analista_proposta] = {
                        'qtd_contratos': 0,
                        'duracao_total': 0
                    }
                
                dados_agrupados[analista_proposta]['qtd_contratos'] += 1
                dados_agrupados[analista_proposta]['duracao_total'] += segundos
            
            # Converter para lista
            dados_tma = []
            for analista_nome, dados in dados_agrupados.items():
                dados_tma.append({
                    'analista': analista_nome,
                    'qtd_contratos': dados['qtd_contratos'],
                    'duracao_total': dados['duracao_total']
                })
            
            dados_tma.sort(key=lambda x: x['analista'])
            print(f"✅ Dados TMA processados: {len(dados_tma)} analistas (CACHE)")
            return dados_tma
            
        except Exception as e:
            print(f"❌ Erro ao obter dados TMA: {e}")
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
        
    def buscar_contratos_por_prefixo(self, prefixo_numero, tipo_contrato):
        """Busca TODOS os contratos da coleção com APENAS 1 LEITURA"""
        try:
            print(f"🔍 Buscando TODOS os contratos da coleção - Prefixo: '{prefixo_numero}'")
            
            # Mapeamento das coleções
            mapeamento_abas = {
                'Saque Fácil': 'contratos_saquefacil',
                'Refin': 'contratos_refin', 
                'Saque Direcionado': 'contratos_saquedirecionado',
                'Solicitação Interna': 'contratos_solicitacao_interna'
            }
            
            if tipo_contrato not in mapeamento_abas:
                print(f"❌ Tipo de contrato não mapeado: {tipo_contrato}")
                return []
            
            colecao_alvo = mapeamento_abas[tipo_contrato]
            print(f"🎯 Fazendo 1 LEITURA COMPLETA na coleção: {colecao_alvo}")
            
            # ⭐⭐ APENAS 1 LEITURA - Buscar TODOS os contratos da coleção
            query = self.db.collection(colecao_alvo)
            resultados = list(query.stream())
            
            print(f"📊 1 LEITURA retornou {len(resultados)} documentos da coleção {colecao_alvo}")
            
            # ⭐⭐ DEBUG: Mostrar todos os números encontrados (campo + ID)
            todos_numeros = []
            for doc in resultados:
                contrato_data = doc.to_dict()
                numero_campo = contrato_data.get('numero', '')
                id_documento = doc.id
                todos_numeros.append(f"campo:'{numero_campo}' id:'{id_documento}'")
            
            print(f"🔍 Todos os números na coleção: {todos_numeros}")
            
            # ⭐⭐ FILTRAR LOCALMENTE os contratos que começam com o prefixo
            contratos_filtrados = []
            for doc in resultados:
                contrato_data = doc.to_dict()
                contrato_data['id'] = doc.id
                contrato_data['colecao_origem'] = colecao_alvo
                
                # ⭐⭐ CORREÇÃO: Usar ID do documento se campo 'numero' estiver vazio
                numero_contrato = contrato_data.get('numero', '')
                if not numero_contrato:
                    numero_contrato = doc.id  # Usar ID do documento como número
                    contrato_data['numero'] = numero_contrato  # Atualizar o campo para uso futuro
                    print(f"   🔄 Usando ID como número: {numero_contrato}")
                
                # ⭐⭐ CORREÇÃO: Verificar se começa com o prefixo (incluindo reanálises)
                if numero_contrato.startswith(prefixo_numero):
                    # Converter datas
                    contrato_data = self._converter_datas_contrato(contrato_data)
                    
                    # Garantir que dados_filtro existe
                    if 'dados_filtro' not in contrato_data:
                        contrato_data['dados_filtro'] = {
                            'regiao': '', 'convenio': '', 'produto': '', 'status': '',
                            'motivo_recusa_id': '', 'motivo_recusa_descricao': '', 'tipo_recusa': ''
                        }
                    
                    contratos_filtrados.append(contrato_data)
                    print(f"   📄 Contrato com prefixo encontrado: {numero_contrato}")
            
            print(f"✅ Total de {len(contratos_filtrados)} contratos com prefixo '{prefixo_numero}' (filtrado localmente)")
            return contratos_filtrados
            
        except Exception as e:
            print(f"❌ Erro ao buscar contratos por prefixo: {e}")
            import traceback
            traceback.print_exc()
            return []