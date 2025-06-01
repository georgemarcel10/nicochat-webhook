import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from datetime import datetime

app = Flask(__name__)

# Variáveis de ambiente (configure no Render)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_SECRET = os.getenv("API_SECRET")  # Vamos criar essa variável para validar o token

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return jsonify({
        "status": "✅ Webhook NicoChat ULTRA ~ Supabase ATIVO!",
        "version": "3.0 - Captura TOTAL + Atualização Progressiva",
        "features": [
            "📌 Captura TODOS os dados disponíveis",
            "📌 Atualização progressiva do mesmo lead",
            "📌 Histórico completo de mudanças"
        ]
    })

@app.route('/webhook/nicochat', methods=['POST'])
def webhook():
    # 1️⃣ Verificar o cabeçalho Authorization
    auth_header = request.headers.get('Authorization', '')
    expected_token = f"Bearer {API_SECRET}"

    if auth_header != expected_token:
        return jsonify({"error": "Unauthorized"}), 401

    # 2️⃣ Receber e processar o webhook
    data = request.json
    print("Webhook recebido:", data)

    # Aqui você pode salvar no Supabase, processar, etc.
    # Por exemplo, salvar a data da requisição
    supabase.table("webhook_logs").insert({
        "timestamp": datetime.utcnow().isoformat(),
        "data": json.dumps(data)
    }).execute()

    return jsonify({"status": "sucesso", "mensagem": "Webhook recebido e processado!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
