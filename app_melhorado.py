# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import json
import os

# --- WEBHOOK MELHORADO PARA CAPTURAR DADOS COMPLETOS --- #

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

def extrair_dados_nicochat(webhook_data):
    """Extrai dados específicos do NicoChat baseado na estrutura real"""
    try:
        dados = {}
        
        # Buscar dados em diferentes níveis da estrutura
        # Meta dados básicos
        meta = webhook_data.get('meta', {})
        dados['user_ns'] = meta.get('user_ns', '')
        dados['agent_id'] = meta.get('agent_id', 0)
        dados['team_id'] = meta.get('team_id', 0)
        
        # Procurar por campos específicos em qualquer lugar do JSON
        def buscar_campo_recursivo(obj, campo):
            """Busca um campo em qualquer nível do JSON"""
            if isinstance(obj, dict):
                # Busca direta
                if campo in obj:
                    return obj[campo]
                # Busca em subcampos
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        resultado = buscar_campo_recursivo(value, campo)
                        if resultado:
                            return resultado
            elif isinstance(obj, list):
                for item in obj:
                    resultado = buscar_campo_recursivo(item, campo)
                    if resultado:
                        return resultado
            return None
        
        # Extrair campos específicos
        campos_busca = [
            'Nome_Completo', 'nome_completo', 'name',
            'Endereco', 'endereco', 'address',
            'canal_origem', 'channel',
            'Data_Entrada', 'data_entrada',
            'id_leads_ZOHO', 'id_leads_zoho', 'lead_id',
            'Produto', 'produto', 'product',
            'Last_Message', 'last_message',
            'Estado', 'estado', 'state',
            'phone', 'telefone', 'celular',
            'email', 'e-mail'
        ]
        
        for campo in campos_busca:
            valor = buscar_campo_recursivo(webhook_data, campo)
            if valor:
                dados[campo.lower()] = valor
        
        return dados
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        return {}

@app.route('/')
def home():
    """Página inicial do webhook"""
    return jsonify({
        "status": "🚀 Webhook NicoChat → Supabase ATIVO!",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0 - Captura Completa",
        "endpoints": {
            "webhook": "/webhook/nicochat",
            "test": "/webhook/test",
            "health": "/health"
        }
    })

@app.route('/webhook/nicochat', methods=['POST'])
def nicochat_webhook():
    """Webhook que recebe novos leads do NicoChat"""
    try:
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({"error": "No data received"}), 400
        
        print(f"📨 Webhook recebido: {webhook_data}")
        
        # Processa o lead com mapeamento melhorado
        success = process_new_lead_enhanced(webhook_data)
        
        if success:
            return jsonify({
                "status": "✅ Lead processado com sucesso!",
                "timestamp": datetime.now().isoformat()
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

def process_new_lead_enhanced(webhook_data):
    """Processa um novo lead com mapeamento completo dos dados"""
    try:
        # Extrai dados do lead usando função melhorada
        dados_extraidos = extrair_dados_nicochat(webhook_data)
        
        # ID único do subscriber
        subscriber_id = (
            dados_extraidos.get('user_ns') or 
            dados_extraidos.get('id_leads_zoho') or 
            f"webhook_{datetime.now().timestamp()}"
        )
        
        # Mapeia os dados para o Supabase
        mapped_data = {
            "nicochat_subscriber_id": str(subscriber_id),
            "name": dados_extraidos.get('nome_completo') or dados_extraidos.get('name') or "Lead Automático",
            "phone": dados_extraidos.get('phone') or dados_extraidos.get('telefone'),
            "email": dados_extraidos.get('email'),
            
            # Novos campos específicos
            "nome_completo": dados_extraidos.get('nome_completo'),
            "endereco": dados_extraidos.get('endereco'),
            "canal_origem": dados_extraidos.get('canal_origem'),
            "id_leads_zoho": dados_extraidos.get('id_leads_zoho'),
            "produto": dados_extraidos.get('produto'),
            "last_message": dados_extraidos.get('last_message'),
            
            # Campos de controle
            "source": "NicoChat Webhook v2.0",
            "synced_at": datetime.now().isoformat(),
            "webhook_data": json.dumps(webhook_data),  # Dados originais completos
            "json_dados_completos": webhook_data  # Para consultas JSONB
        }

        # Remove valores vazios
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None and v != ""}

        # Insert/Update no Supabase
        result = supabase.table("leads").upsert(mapped_data, on_conflict="nicochat_subscriber_id").execute()
        
        print(f"✅ Lead {subscriber_id} processado via webhook!")
        print(f"📊 Nome: {mapped_data.get('name')}")
        if mapped_data.get('endereco'):
            print(f"📍 Endereço: {mapped_data.get('endereco')}")
        if mapped_data.get('produto'):
            print(f"🎯 Produto: {mapped_data.get('produto')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar lead: {e}")
        return False

@app.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """Endpoint para testar webhook"""
    return jsonify({
        "status": "✅ Webhook v2.0 funcionando!",
        "method": request.method,
        "timestamp": datetime.now().isoformat(),
        "message": "Pronto para capturar dados completos do NicoChat! 🎯"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    try:
        # Testa Supabase
        supabase.table("leads").select("count", count="exact").limit(1).execute()
        return jsonify({
            "status": "🟢 Healthy v2.0",
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
