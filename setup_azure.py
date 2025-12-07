import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")

def init_azure():
    print(f"🚀 Iniciando configuração Azure AI Foundry...")
    print(f"   ☁️  Endpoint: {ENDPOINT}")
    print(f"   🤖 Deployment: {DEPLOYMENT}")

    try:
        client = AzureOpenAI(
            azure_endpoint=ENDPOINT,
            api_key=API_KEY,
            api_version=API_VERSION
        )

        print(f"\n👉 Enviando prompt de teste...")
        
        # Adicionamos stream=False explicitamente
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "user", "content": "Hello! Just say 'Azure Connected'."}
            ],
            max_tokens=50
        )
        
        # --- DIAGNÓSTICO DE RESPOSTA VAZIA ---
        choice = response.choices[0]
        content = choice.message.content
        finish_reason = choice.finish_reason
        
        print(f"   🔍 Finish Reason: {finish_reason}")
        
        if content:
            print("✅ SUCESSO! O Azure respondeu:")
            print("-" * 40)
            print(content)
            print("-" * 40)
        else:
            print("⚠️  ALERTA: Conteúdo vazio (None).")
            print("   Motivo provável: Filtro de conteúdo ou modelo não gerou texto.")
            print(f"   Dump completo da resposta: {response.model_dump()}")

    except Exception as e:
        print(f"\n❌ Falha na conexão Azure: {e}")

if __name__ == "__main__":
    init_azure()
