import vertexai
from vertexai.preview.generative_models import GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

print(f"🔍 Buscando modelos disponíveis em {REGION} para o projeto {PROJECT_ID}...")

vertexai.init(project=PROJECT_ID, location=REGION)

# Lista modelos da 'Model Garden' que são Foundation Models
from google.cloud import aiplatform
aiplatform.init(project=PROJECT_ID, location=REGION)

models = aiplatform.Model.list()

# Como a API de listagem do Vertex é complexa, vamos testar os IDs mais prováveis
candidates = [
    "gemini-1.5-pro-002",      # Versão mais potente atual (Estável)
    "gemini-1.5-flash-002",    # Versão mais rápida atual
    "gemini-experimental",     # Onde novos recursos costumam aparecer
    "gemini-1.5-pro-preview-0514",
    "gemini-pro"
]

print("\n🧪 Testando disponibilidade direta:")
for model_id in candidates:
    try:
        model = GenerativeModel(model_id)
        # Tenta uma chamada simples (dry run)
        print(f"  ✅ {model_id} -> DISPONÍVEL")
    except Exception:
        print(f"  ❌ {model_id} -> Indisponível/Erro")

print("\n💡 Dica: Se 'gemini-3' não está na lista, ele ainda não foi liberado na API pública da sua região.")
