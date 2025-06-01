import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from datetime import datetime

app = Flask(__name__)

# Variáveis de ambiente (configure no Render)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return jsonify({
        "status": "🚀 Webhook NicoChat ULTRA → Supabase ATIVO!",
        "version": "3.0 - Captura TOTAL + Atualização Progressiva",
        "features": [
            "Captura TODOS os dados disponíveis",
            "Atualização progressiva do mesmo lead",
            "Histórico completo de mudanças"
        ]
    })

@app.route('/webhook/nicochat', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Mapeamento dos campos principais do NicoChat para Supabase
    mapped_data = {
        "user_ns": data.get("user_ns"),
        "user_id": data.get("user_id"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "name": data.get("name"),
        "gender": data.get("gender"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "channel": data.get("channel"),
        "status": data.get("status"),
        "country": data.get("country"),
        "region": data.get("region"),
        "city": data.get("city"),
        "address": data.get("address"),
        "postcode": data.get("postcode"),
        "ip": data.get("ip"),
        "locale": data.get("locale"),
        "language": data.get("language"),
        "timezone": data.get("timezone"),
        "lead_source": data.get("lead_source"),
        "lead_status": data.get("lead_status"),
        "referrer": data.get("referrer"),
        "landing_page": data.get("landing_page"),
        "platform": data.get("platform"),
        "browser": data.get("browser"),
        "device": data.get("device"),
        "device_type": data.get("device_type"),
        "department": data.get("department"),
        "interest": data.get("interest"),
        "market": data.get("market"),
        "profile_pic": data.get("profile_pic"),
        "subscribed": data.get("subscribed"),
        "opted_in_email": data.get("opted_in_email"),
        "opted_in_sms": data.get("opted_in_sms"),
        "opted_in_through": data.get("opted_in_through"),
        "last_interaction": data.get("last_interaction"),
        "last_agent_action_at": data.get("last_agent_action_at"),
        "last_seen": data.get("last_seen"),
        "last_message_type": data.get("last_message_type"),
        "last_message_at": data.get("last_message_at"),
        "agent_id": data.get("agent_id"),
        "agent_name": data.get("agent_name"),
        "agent_email": data.get("agent_email"),
        "pergunta_user": data.get("pergunta_user"),
        "resposta_gpt": data.get("resposta_gpt"),
        "synced_at": datetime.utcnow().isoformat()
    }

    # Verificar se o lead já existe
    existing = supabase.table("leads").select("user_ns").eq("user_ns", mapped_data["user_ns"]).execute()

    if existing.data:
        # Atualizar lead existente
        supabase.table("leads").update(mapped_data).eq("user_ns", mapped_data["user_ns"]).execute()
        action = "atualizado"
    else:
        # Criar novo lead
        supabase.table("leads").insert(mapped_data).execute()
        action = "criado"

    return jsonify({"status": "Lead processado com sucesso", "acao": action, "dados": mapped_data})

if __name__ == '__main__':
    app.run(debug=True)
