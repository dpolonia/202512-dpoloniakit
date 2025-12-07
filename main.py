import argparse
import datetime
import uuid
import sys
from dotenv import load_dotenv

# Importa módulos
from setup_google import init_vertex as google_ai
from setup_database import init_azure_cosmos, init_google_bigquery
from google.cloud import bigquery
from azure.cosmos import CosmosClient, PartitionKey
import os

load_dotenv()

# Configurações rápidas para conexão direta (pós-teste)
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
COSMOS_URL = os.getenv("AZURE_COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY")
DB_NAME = "SNSHADB"

def save_interaction(provider, prompt, response):
    """Salva a conversa no Cosmos DB"""
    try:
        client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
        database = client.get_database_client(DB_NAME)
        container = database.get_container_client("Interactions")
        
        item = {
            "id": str(uuid.uuid4()),
            "session_id": "session_dev_001",
            "timestamp": str(datetime.datetime.now()),
            "provider": provider,
            "prompt": prompt,
            "response": response
        }
        container.create_item(body=item)
        print(f"   💾 [Cosmos DB] Conversa salva com sucesso.")
    except Exception as e:
        print(f"   ⚠️ Falha ao salvar no Cosmos: {e}")

def log_event(message):
    """Salva log técnico no BigQuery"""
    try:
        client = bigquery.Client(project=GCP_PROJECT)
        table_id = f"{GCP_PROJECT}.{DB_NAME.lower()}.app_logs"
        
        rows_to_insert = [{
            "timestamp": str(datetime.datetime.now()),
            "provider": "SYSTEM",
            "message": message
        }]
        
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors == []:
            print(f"   📊 [BigQuery] Log registrado.")
        else:
            print(f"   ⚠️ Erros no BigQuery: {errors}")
    except Exception as e:
        print(f"   ⚠️ Falha no BigQuery: {e}")

def main():
    parser = argparse.ArgumentParser(description="SNSHADB - AI & Data Controller")
    parser.add_argument("--ask", type=str, help="Faça uma pergunta para a IA (ex: 'O que é Python?')")
    args = parser.parse_args()

    if not args.ask:
        print("ℹ️  Uso: python main.py --ask \"Sua pergunta aqui\"")
        # Se rodar sem argumentos, roda os testes de conexão antigos
        print("   Rodando verificação de saúde do sistema...")
        init_google_bigquery()
        init_azure_cosmos()
        return

    print(f"🚀 Processando pergunta: \"{args.ask}\"")
    log_event(f"Iniciando processamento: {args.ask}")

    # 1. Chama a IA (Usando Gemini como padrão hoje)
    # Nota: Estamos importando a função de teste, idealmente refatoraríamos para retornar texto limpo.
    # Por enquanto, vamos simular a chamada ou você pode editar o setup_google para retornar string.
    
    print("\n🤖 Consultando Google Gemini...")
    # Aqui, para simplificar neste passo final, vou instanciar o cliente direto para pegar o texto limpo
    try:
        from google import genai
        client = genai.Client(vertexai=True, project=GCP_PROJECT, location="us-central1")
        response = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=args.ask
        )
        ai_reply = response.text
        print(f"✅ Resposta:\n{ai_reply[:200]}... (truncado)")
        
        # 2. Salva nos Bancos de Dados
        save_interaction("Google Vertex AI", args.ask, ai_reply)
        log_event("Sucesso no processamento AI")
        
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        log_event(f"Erro: {str(e)}")

if __name__ == "__main__":
    main()
