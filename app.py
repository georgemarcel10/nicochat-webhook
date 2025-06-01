import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from datetime import datetime

app = Flask(__name__)

# Variáveis de ambiente (Render)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_SECRET = os.getenv("API_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return jsonify({
        "status": "🚀 Webhook NicoChat ULTRA ~ Supabase ATIVO!",
        "version": "3.0 - Captura TOTAL + Validação de Autorização",
        "features": [
            "Validação de Authorization Header",
            "Captura e armazenamento no Supabase",
            "Atualização progressiva do mesmo lead",
            "Histórico completo de mudanças"
        ]
    })

@app.route('/webhook/nicochat', methods=['POST'])
def webhook():
    # Valida o Authorization Header
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {API_SECRET}":
        return jsonify({"error": "Unauthorized. Invalid or missing API_SECRET."}), 401

    # Processa o payload recebido
    data = request.json
    print(f"Webhook recebido: {json.dumps(data)}")

    # Aqui você pode ajustar como salvar no Supabase, exemplo simples:
    try:
        response = supabase.table("leads").insert(data).execute()
        return jsonify({"status": "success", "data": response.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
