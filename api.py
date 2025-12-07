from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import os
import uuid
import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Importa os módulos de conexão existentes
from google import genai
from azure.cosmos import CosmosClient
from google.cloud import bigquery

# Carrega ambiente
load_dotenv()

# Configuração da Aplicação
app = FastAPI(
    title="SNSHADB Core API",
    description="API Central para orquestração de IAs (Google/Azure) e Dados (Cosmos/BigQuery)",
    version="1.0.0"
)

# --- Configurações de Nuvem ---
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
COSMOS_URL = os.getenv("AZURE_COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY")
DB_NAME = "SNSHADB"

# --- Modelos de Dados (Contrato da API) ---
class ChatRequest(BaseModel):
    prompt: str = Field(..., description="A pergunta ou comando para a IA")
    user_id: str = Field("default_user", description="ID do usuário que está chamando")
    provider: str = Field("google", description="Qual IA usar: 'google' ou 'azure'")

class ChatResponse(BaseModel):
    response: str
    session_id: str
    provider: str
    timestamp: str

# --- Funções de Infra (Background) ---
# Usamos BackgroundTasks para não travar a resposta da API enquanto salva no banco

def save_to_cosmos(user_id: str, session_id: str, prompt: str, response: str, provider: str):
    """Salva a interação no Azure Cosmos DB"""
    try:
        client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
        # O cliente do DB e Container deveria ser cacheado em prod, mas aqui instanciamos por segurança
        db = client.get_database_client(DB_NAME)
        container = db.get_container_client("Interactions")
        
        item = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": str(datetime.datetime.now()),
            "provider": provider,
            "prompt": prompt,
            "response": response
        }
        container.create_item(body=item)
        print(f"✅ [Cosmos DB] Item salvo: {session_id}")
    except Exception as e:
        print(f"❌ [Cosmos DB] Erro: {e}")

def log_to_bigquery(event_type: str, message: str):
    """Registra log técnico no Google BigQuery"""
    try:
        client = bigquery.Client(project=GCP_PROJECT)
        table_id = f"{GCP_PROJECT}.{DB_NAME.lower()}.app_logs"
        
        rows = [{
            "timestamp": str(datetime.datetime.now()),
            "provider": event_type,
            "message": str(message)[:1000] # Trunca mensagens muito longas
        }]
        
        errors = client.insert_rows_json(table_id, rows)
        if errors:
            print(f"❌ [BigQuery] Erros: {errors}")
        else:
            print(f"✅ [BigQuery] Log inserido.")
            
    except Exception as e:
        print(f"❌ [BigQuery] Falha: {e}")

# --- Rotas da API ---

@app.get("/")
def root():
    """Health check simples"""
    return {
        "status": "online",
        "system": "SNSHADB Controller",
        "docs_url": "/docs"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Recebe um prompt, processa na IA escolhida e salva histórico em background.
    """
    session_id = str(uuid.uuid4())
    ai_reply = ""
    
    # 1. Roteamento de IA
    try:
        if request.provider == "google":
            # Conecta no Vertex AI (Gemini)
            # Nota: Em produção, o cliente deve ser inicializado fora da rota (startup event)
            client = genai.Client(vertexai=True, project=GCP_PROJECT, location="us-central1")
            resp = client.models.generate_content(
                model="gemini-2.5-pro", 
                contents=request.prompt
            )
            ai_reply = resp.text
            
        elif request.provider == "azure":
            # Lógica para Azure (pode ser expandida depois importando setup_azure)
            ai_reply = "Suporte a Azure API via endpoint HTTP será reativado em breve."
            
        else:
            raise HTTPException(status_code=400, detail="Provider desconhecido. Use 'google' ou 'azure'.")

    except Exception as e:
        # Loga o erro antes de quebrar
        background_tasks.add_task(log_to_bigquery, "API_ERROR", str(e))
        raise HTTPException(status_code=500, detail=f"Erro no processamento da IA: {str(e)}")

    # 2. Agendar salvamento de dados (não bloqueia o retorno para o usuário)
    background_tasks.add_task(
        save_to_cosmos, 
        request.user_id, 
        session_id, 
        request.prompt, 
        ai_reply, 
        request.provider
    )
    
    background_tasks.add_task(
        log_to_bigquery, 
        "API_SUCCESS", 
        f"Session: {session_id} | User: {request.user_id}"
    )

    # 3. Retorno rápido
    return {
        "response": ai_reply,
        "session_id": session_id,
        "provider": request.provider,
        "timestamp": str(datetime.datetime.now())
    }

if __name__ == "__main__":
    import uvicorn
    # Permite rodar como script python normal também
    uvicorn.run(app, host="0.0.0.0", port=8000)
