import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "snshadb")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

def init_vertex():
    print(f"🚀 Iniciando configuração Gemini 2.5 Pro (Versão Estável)...")
    print(f"   📂 Projeto: {PROJECT_ID}")
    print(f"   🌎 Região: {LOCATION}")

    try:
        # Inicializa cliente no modo Vertex AI
        client = genai.Client(
            vertexai=True, 
            project=PROJECT_ID, 
            location=LOCATION
        )

        # ID do modelo conforme sua documentação (GA)
        model_id = "gemini-2.5-pro"

        print(f"\n🧠 Conectando ao modelo: {model_id}...")
        
        # Configuração padrão (Temperature 1.0 é o default do 2.5)
        generate_config = types.GenerateContentConfig(
            temperature=1.0,
            candidate_count=1
        )

        print(f"   👉 Enviando prompt de teste...")
        
        response = client.models.generate_content(
            model=model_id,
            contents="Explique resumidamente o impacto da IA na medicina diagnóstica.",
            config=generate_config
        )

        print("✅ SUCESSO! Conexão estabelecida.")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        print(f"🎉 Modelo oficial '{model_id}' validado.")

    except Exception as e:
        print(f"\n❌ Erro na conexão: {e}")
        if "404" in str(e):
            print("⚠️ Erro 404 persistente? Tente mudar a região no .env para 'us-central1' ou 'europe-west1'.")

if __name__ == "__main__":
    init_vertex()
