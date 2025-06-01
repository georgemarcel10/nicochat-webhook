from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
import json
from datetime import datetime

app = Flask(__name__)

# Variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return jsonify({
        "status": "✅ Webhook NicoChat ULTRA + Supabase ATIVO!",
        "version": "3.0 - Captura TOTAL + Atualização Progressiva",
        "features": [
            "📥 Captura TODOS os dados disponíveis",
            "🔄 Atualização progressiva do mesmo lead",
            "📝 Histórico completo de mudanças"
        ]
    })

@app.route('/webhook/nicochat', methods=['POST'])
def webhook():
    try:
        # Captura o header Authorization (se vier)
        auth_header = request.headers.get('Authorization', None)
        print("🔑 Header recebido:", auth_header)

        # (Opcional) Valide se o header começa com 'Bearer'
        if auth_header and not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Header Authorization inválido."}), 400

        # Processa o JSON recebido
        data = request.get_json()
        print("📥 Dados recebidos:", json.dumps(data, indent=2))

        if not data:
            return jsonify({"status": "ok", "message": "Nenhum dado recebido."})

        # Insere no Supabase
        response = supabase.table("nome_da_sua_tabela").insert(data).execute()
        print("✅ Dados inseridos no Supabase:", response)

        return jsonify({"status": "success", "message": "Dados armazenados com sucesso."})

    except Exception as e:
        print("❌ Erro:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
