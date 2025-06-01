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
        data = request.get_json()
        print("📥 Recebido:", data)

        # Teste de verificação (NicoChat espera por um retorno simples)
        if not data:
            return jsonify({"status": "ok"})

        # Insere no Supabase
        response = supabase.table("nome_da_sua_tabela").insert(data).execute()
        print("✅ Dados inseridos no Supabase:", response)

        return jsonify({"status": "success", "message": "Dados recebidos e armazenados com sucesso."})
    except Exception as e:
        print("❌ Erro:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
