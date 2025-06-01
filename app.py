import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from datetime import datetime

# Inicializa o Flask
app = Flask(__name__)

# Variáveis de ambiente (configure no Render)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rota de status (para teste rápido)
@app.route('/')
def index():
    return jsonify({
        "status": "✅ Webhook NicoChat ULTRA → Supabase ATIVO!",
        "version": "3.0 - Captura TOTAL + Atualização Progressiva",
        "features": [
            "Captura TODOS os dados disponíveis",
            "Atualização progressiva do mesmo lead",
            "Histórico completo de mudanças"
        ]
    })

# Rota para receber o webhook do NicoChat
@app.route('/webhook/nicochat', methods=['POST'])
def webhook():
    try:
        # Recebe os dados JSON enviados pelo NicoChat
        data = request.json
        print("Webhook recebido:", data)

        # Data e hora atual para controle
        now = datetime.now().isoformat()

        # Mapeamento de campos recebidos
        lead_data = {
            "user_ns": data.get("user_ns"),
            "user_id": data.get("user_id"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "name": data.get("name"),
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
            "platform": data.get("platform"),
            "browser": data.get("browser"),
            "device": data.get("device"),
            "device_type": data.get("device_type"),
            "referrer": data.get("referrer"),
            "landing_page": data.get("landing_page"),
            "lead_source": data.get("lead_source"),
            "lead_status": data.get("lead_status"),
            "department": data.get("department"),
            "interest": data.get("interest"),
            "market": data.get("market"),
            "agent_id": data.get("agent_id"),
            "agent_name": data.get("agent_name"),
            "pergunta_user": data.get("pergunta_user"),
            "resposta_gpt": data.get("resposta_gpt"),
            "synced_at": now
        }

        # Envia para o Supabase via upsert
        response = supabase.table("leads").upsert(lead_data).execute()
        print("Resposta do Supabase:", response)

        return jsonify({"status": "✅ OK", "mensagem": "Lead salvo no Supabase!"})

    except Exception as e:
        print("Erro ao processar webhook:", str(e))
        return jsonify({"status": "❌ Erro", "mensagem": str(e)}), 500

# Executa o Flask (opcional para testes locais)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
