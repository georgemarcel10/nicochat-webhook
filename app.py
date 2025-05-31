# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import json
import os

# --- WEBHOOK AUTOMÁTICO PARA RAILWAY --- #

app = Flask(__name__)

# Credenciais (em produção use variáveis de ambiente)
SUPABASE_URL = "https://tnibpkxgsxvuzkxnevab.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRuaWJwa3hnc3h2dXpreG5ldmFiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODY5NzA4NCwiZXhwIjoyMDY0MjczMDg0fQ.yudJ3AgnPT-iMDX8uIpsNrFqMYPuN6f7X1EEQvkn_4g"

# Inicializa Supabase
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Supabase conectado!")
except Exception as e:
    print(f"❌ Erro Supabase: {e}")

@app.route('/')
def home():
    """Página inicial do webhook"""
    return jsonify({
        "status": "🚀 Webhook NicoChat → Supabase ATIVO!",
        "timestamp": datetime.now().isoformat(),
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
        
        # Processa o lead
        success = process_new_lead(webhook_data)
        
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

def process_new_lead(webhook_data):
    """Processa um novo lead recebido via webhook"""
    try:
        # Extrai dados do lead
        lead_data = webhook_data.get('subscriber', webhook_data)
        
        subscriber_id = lead_data.get("user_ns") or lead_data.get("id") or f"webhook_{datetime.now().timestamp()}"
        
        # Mapeia os dados essenciais
        mapped_data = {
            "nicochat_subscriber_id": str(subscriber_id),
            "name": lead_data.get("name") or f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip() or "Novo Lead",
            "phone": lead_data.get("phone"),
            "email": lead_data.get("email") if lead_data.get("email") else None,
            "source": "NicoChat Webhook",
            "synced_at": datetime.now().isoformat(),
            "webhook_data": json.dumps(webhook_data)  # Salva dados completos
        }

        # Remove valores vazios
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None and v != ""}

        # Insert/Update no Supabase
        result = supabase.table("leads").upsert(mapped_data, on_conflict="nicochat_subscriber_id").execute()
        
        print(f"✅ Lead {subscriber_id} processado via webhook!")
        print(f"📊 Nome: {mapped_data.get('name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar lead: {e}")
        return False

@app.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """Endpoint para testar webhook"""
    return jsonify({
        "status": "✅ Webhook funcionando!",
        "method": request.method,
        "timestamp": datetime.now().isoformat(),
        "message": "Pronto para receber leads do NicoChat! 🎯"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    try:
        # Testa Supabase
        supabase.table("leads").select("count", count="exact").limit(1).execute()
        return jsonify({
            "status": "🟢 Healthy",
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
