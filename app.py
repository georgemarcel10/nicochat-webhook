import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from datetime import datetime

app = Flask(__name__)

# Variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_SECRET = os.getenv("API_SECRET")  # Pegamos a API_KEY criada no NicoChat
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return jsonify({
        "status": "✅ Webhook NicoChat + Supabase ATIVO!",
        "version": "3.0 - Captura TOTAL + Atualização Progressiva",
        "features": [
            "Captura TODOS os dados disponíveis",
            "Atualização progressiva do mesmo lead",
            "Histórico completo de mudanças"
        ]
    })

@app.route('/webhook/nicochat', methods=['POST'])
def webhook():
    auth_header = request.headers.get('Authorization')
    print(f"Header recebido: [{auth_header}]")
    print(f"Header esperado: [Bearer {API_SECRET}]")
    if auth_header != f"Bearer {API_SECRET}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    print("Webhook recebido:", data)

    # Salva os dados no Supabase (opcional)
    # supabase.table("webhooks").insert({"data": data, "timestamp": str(datetime.utcnow())}).execute()

    return jsonify({"message": "Webhook recebido com sucesso!"}), 200

if __name__ == '__main__':
    app.run()
