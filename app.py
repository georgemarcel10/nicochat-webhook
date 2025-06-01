import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from datetime import datetime

app = Flask(__name__)

# Variáveis de ambiente (Render)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return jsonify({
        "status": "✅ Webhook NicoChat ULTRA + Supabase ATIVO!",
        "version": "3.0 - Captura TOTAL + Atualização Progressiva",
        "features": [
            "Captura TODOS os dados disponíveis",
            "Atualização progressiva do mesmo lead",
            "Histórico completo de mudanças"
        ]
    })

@app.route('/webhook/nicochat', methods=['POST'])
def webhook():
    try:
        # Apenas para log: mostra o header, mas não processa
        auth_header = request.headers.get('Authorization')
        print("🔑 Header Authorization recebido:", auth_header)

        # Captura os dados JSON
        data = request.get_json()
        print("📥 Dados recebidos:", data)

        # Se for apenas um teste de verificação (sem dados), responde OK
        if not data:
            return jsonify({"status": "ok"})

        # Salva no Supabase
        response = supabase.table("nome_da_sua_tabela").insert(data).execute()
        print("✅ Dados armazenados no Supabase:", response)

        return jsonify({"status": "success", "message": "Dados processados e armazenados."})
    except Exception as e:
        print("❌ Erro:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
