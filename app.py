# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime, date, time
import json
import re
import os

# --- WEBHOOK ULTRA COMPLETO PARA CAPTURAR TODOS OS DADOS NICOCHAT --- #

app = Flask(__name__)

# Credenciais Supabase
SUPABASE_URL = "https://tnibpkxgsxvuzkxnevab.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRuaWJwa3hnc3h2dXpreG5ldmFiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODY5NzA4NCwiZXhwIjoyMDY0MjczMDg0fQ.yudJ3AgnPT-iMDX8uIpsNrFqMYPuN6f7X1EEQvkn_4g"

# Inicializa Supabase
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Supabase conectado!")
except Exception as e:
    print(f"❌ Erro Supabase: {e}")

def extrair_todos_dados_nicochat(webhook_data):
    """Extrai TODOS os dados possíveis do NicoChat"""
    try:
        dados = {}
        
        # Função recursiva para buscar em qualquer nível
        def buscar_recursivo(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Salva o valor se não for dict/list
                    if not isinstance(value, (dict, list)):
                        dados[current_path] = value
                    
                    # Busca recursivamente
                    if isinstance(value, (dict, list)):
                        buscar_recursivo(value, current_path)
                        
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    buscar_recursivo(item, current_path)
        
        # Extrai todos os dados recursivamente
        buscar_recursivo(webhook_data)
        
        # Mapeamento específico para campos conhecidos
        mapeamento = {
            # IDs únicos
            'user_ns': ['meta.user_ns', 'user_ns', 'subscriber_id'],
            'agent_id': ['meta.agent_id', 'agent_id'],
            'flow_ns': ['meta.flow_ns', 'flow_ns'],
            'team_id': ['meta.team_id', 'team_id'],
            
            # Dados pessoais
            'nome_completo': ['Nome_Completo', 'nome_completo', 'name', 'full_name'],
            'primeiro_nome': ['primeiro_nome', 'first_name', 'nome'],
            'ultimo_nome': ['ultimo_nome', 'last_name', 'sobrenome'],
            'telefone': ['phone', 'telefone', 'celular', 'mobile'],
            'email': ['email', 'e-mail', 'email_address'],
            'documento_cliente': ['Documento_Cliente', 'documento', 'cpf', 'document'],
            
            # Localização
            'endereco': ['Endereco', 'endereco', 'address', 'endereço'],
            'cidade': ['cidade', 'city'],
            'estado': ['Estado', 'estado', 'state', 'uf'],
            'cep': ['cep', 'postal_code', 'zip'],
            'pais': ['pais', 'country'],
            
            # Origem e datas
            'canal_origem': ['canal_origem', 'channel', 'source_channel'],
            'data_entrada_nicochat': ['Data_Entrada', 'data_entrada', 'entry_date'],
            'hora_entrada': ['Hora_Entrada', 'hora_entrada', 'entry_time'],
            'ano_entrada': ['Ano_Entrada', 'ano_entrada', 'year'],
            
            # IDs externos
            'id_leads_zoho': ['id_leads_ZOHO', 'id_leads_zoho', 'zoho_id'],
            'id_negociacao_zoho': ['id_negociacao_ZOHO', 'id_negociacao_zoho'],
            'id_leads_2000': ['id_leads_2000'],
            
            # Produto e serviços
            'produto': ['Produto', 'produto', 'product', 'service'],
            'area_direito': ['area_direito', 'legal_area'],
            'situacao_cliente': ['Situacao_Cliente', 'situacao', 'status'],
            'problema_busca': ['problema_busca', 'search_problem'],
            
            # Mensagens
            'last_message': ['Last_Message', 'last_message', 'message.content'],
            'last_message_type': ['message.type', 'msg_type'],
            
            # URLs
            'url_origem': ['url_origem', 'origin_url'],
            'url_thumbnail': ['url_thumbnail', 'thumbnail_url'],
        }
        
        # Aplica mapeamento
        dados_mapeados = {}
        for campo_final, possibilidades in mapeamento.items():
            for possibilidade in possibilidades:
                if possibilidade in dados:
                    dados_mapeados[campo_final] = dados[possibilidade]
                    break
        
        # Adiciona dados brutos para campos não mapeados
        dados_mapeados['dados_extras'] = {k: v for k, v in dados.items() 
                                         if not any(k in poss for poss in mapeamento.values())}
        
        return dados_mapeados
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        return {}

def identificar_lead_existente(dados):
    """Identifica se é um lead existente para atualizar"""
    try:
        # Critérios de identificação (em ordem de prioridade)
        criterios = [
            ('user_ns', dados.get('user_ns')),
            ('telefone', dados.get('telefone')),
            ('id_leads_zoho', dados.get('id_leads_zoho')),
            ('email', dados.get('email'))
        ]
        
        for campo, valor in criterios:
            if valor and valor.strip():
                result = supabase.table("leads").select("*").eq(campo, valor).execute()
                if result.data:
                    return result.data[0]  # Retorna o primeiro encontrado
        
        return None
        
    except Exception as e:
        print(f"❌ Erro ao identificar lead: {e}")
        return None

@app.route('/')
def home():
    """Página inicial do webhook"""
    return jsonify({
        "status": "🚀 Webhook NicoChat ULTRA → Supabase ATIVO!",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0 - Captura TOTAL + Atualização Progressiva",
        "features": [
            "Captura TODOS os dados disponíveis",
            "Atualização progressiva do mesmo lead",
            "Histórico completo de mudanças",
            "Mapeamento inteligente de campos"
        ],
        "endpoints": {
            "webhook": "/webhook/nicochat",
            "test": "/webhook/test",
            "health": "/health"
        }
    })

@app.route('/webhook/nicochat', methods=['POST'])
def nicochat_webhook():
    """Webhook ULTRA que captura e atualiza TODOS os dados"""
    try:
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({"error": "No data received"}), 400
        
        print(f"📨 Webhook ULTRA recebido: {json.dumps(webhook_data, indent=2)}")
        
        # Processa com captura total
        success = process_lead_ultra_completo(webhook_data)
        
        if success:
            return jsonify({
                "status": "✅ Lead processado com TODOS os dados!",
                "timestamp": datetime.now().isoformat(),
                "version": "3.0"
            }), 200
        else:
            return jsonify({
                "status": "❌ Erro ao processar lead"
            }), 500
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def process_lead_ultra_completo(webhook_data):
    """Processa lead com captura TOTAL e atualização progressiva"""
    try:
        # Extrai TODOS os dados possíveis
        dados_extraidos = extrair_todos_dados_nicochat(webhook_data)
        
        print(f"🔍 Dados extraídos: {json.dumps(dados_extraidos, indent=2, default=str)}")
        
        # Verifica se é lead existente
        lead_existente = identificar_lead_existente(dados_extraidos)
        
        agora = datetime.now().isoformat()
        
        if lead_existente:
            # ATUALIZAÇÃO de lead existente
            print(f"🔄 Atualizando lead existente: {lead_existente['id']}")
            
            # Mescla dados novos com existentes
            dados_atualizados = {
                # Atualiza campos básicos
                "name": dados_extraidos.get('nome_completo') or lead_existente.get('name'),
                "phone": dados_extraidos.get('telefone') or lead_existente.get('phone'),
                "email": dados_extraidos.get('email') or lead_existente.get('email'),
                
                # Todos os novos campos
                "user_ns": dados_extraidos.get('user_ns') or lead_existente.get('user_ns'),
                "nome_completo": dados_extraidos.get('nome_completo') or lead_existente.get('nome_completo'),
                "telefone": dados_extraidos.get('telefone') or lead_existente.get('telefone'),
                "endereco": dados_extraidos.get('endereco') or lead_existente.get('endereco'),
                "estado": dados_extraidos.get('estado') or lead_existente.get('estado'),
                "canal_origem": dados_extraidos.get('canal_origem') or lead_existente.get('canal_origem'),
                "produto": dados_extraidos.get('produto') or lead_existente.get('produto'),
                "id_leads_zoho": dados_extraidos.get('id_leads_zoho') or lead_existente.get('id_leads_zoho'),
                "last_message": dados_extraidos.get('last_message') or lead_existente.get('last_message'),
                
                # Controle de atualizações
                "ultima_atualizacao": agora,
                "numero_atualizacoes": (lead_existente.get('numero_atualizacoes') or 0) + 1,
                
                # Dados brutos atualizados
                "dados_brutos_nicochat": dados_extraidos,
                "webhook_raw_data": webhook_data,
                "campos_extras": dados_extraidos.get('dados_extras', {}),
                
                # Histórico de mudanças
                "historico_atualizacoes": (lead_existente.get('historico_atualizacoes') or []) + [{
                    "timestamp": agora,
                    "dados_novos": dados_extraidos,
                    "webhook_completo": webhook_data
                }]
            }
            
            # Remove valores None/vazios
            dados_atualizados = {k: v for k, v in dados_atualizados.items() 
                               if v is not None and v != ""}
            
            # Atualiza no Supabase
            result = supabase.table("leads").update(dados_atualizados).eq("id", lead_existente['id']).execute()
            
            print(f"✅ Lead {lead_existente['id']} ATUALIZADO com sucesso!")
            
        else:
            # CRIAÇÃO de novo lead
            print(f"🆕 Criando novo lead")
            
            subscriber_id = (
                dados_extraidos.get('user_ns') or 
                dados_extraidos.get('id_leads_zoho') or 
                f"webhook_{datetime.now().timestamp()}"
            )
            
            dados_novo_lead = {
                "nicochat_subscriber_id": str(subscriber_id),
                "name": dados_extraidos.get('nome_completo') or "Lead Automático",
                "phone": dados_extraidos.get('telefone'),
                "email": dados_extraidos.get('email'),
                
                # TODOS os campos mapeados
                "user_ns": dados_extraidos.get('user_ns'),
                "nome_completo": dados_extraidos.get('nome_completo'),
                "telefone": dados_extraidos.get('telefone'),
                "endereco": dados_extraidos.get('endereco'),
                "estado": dados_extraidos.get('estado'),
                "canal_origem": dados_extraidos.get('canal_origem'),
                "produto": dados_extraidos.get('produto'),
                "id_leads_zoho": dados_extraidos.get('id_leads_zoho'),
                "last_message": dados_extraidos.get('last_message'),
                
                # Controle
                "source": "NicoChat Webhook v3.0",
                "synced_at": agora,
                "primeira_captura": agora,
                "ultima_atualizacao": agora,
                "numero_atualizacoes": 1,
                
                # Dados completos
                "dados_brutos_nicochat": dados_extraidos,
                "webhook_raw_data": webhook_data,
                "campos_extras": dados_extraidos.get('dados_extras', {}),
                "historico_atualizacoes": [{
                    "timestamp": agora,
                    "acao": "criacao",
                    "dados": dados_extraidos
                }]
            }
            
            # Remove valores None/vazios
            dados_novo_lead = {k: v for k, v in dados_novo_lead.items() 
                             if v is not None and v != ""}
            
            # Insere no Supabase
            result = supabase.table("leads").insert(dados_novo_lead).execute()
            
            print(f"✅ Novo lead {subscriber_id} criado com sucesso!")
        
        # Log detalhado
        print(f"📊 Dados capturados:")
        for campo, valor in dados_extraidos.items():
            if valor and campo != 'dados_extras':
                print(f"   {campo}: {valor}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar lead ultra completo: {e}")
        return False

@app.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """Endpoint para testar webhook"""
    return jsonify({
        "status": "✅ Webhook v3.0 ULTRA funcionando!",
        "method": request.method,
        "timestamp": datetime.now().isoformat(),
        "message": "Pronto para capturar TODOS os dados do NicoChat! 🎯",
        "features": "Captura total + Atualização progressiva"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    try:
        supabase.table("leads").select("count", count="exact").limit(1).execute()
        return jsonify({
            "status": "🟢 Healthy v3.0 ULTRA",
            "supabase": "✅ Connected",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "🔴 Unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
