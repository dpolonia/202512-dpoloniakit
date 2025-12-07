import os
from dotenv import load_dotenv

# Google Libs
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Azure Libs
from azure.cosmos import CosmosClient, PartitionKey, exceptions

load_dotenv()

# Configs
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "snshadb")
# Remove espaços em branco ou aspas acidentais das variáveis
COSMOS_URL = os.getenv("AZURE_COSMOS_ENDPOINT", "").strip()
COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY", "").strip().strip("'").strip('"')
DB_NAME = "SNSHADB"

def init_google_bigquery():
    print(f"\n[GOOGLE] 🐘 Conectando ao BigQuery ({GCP_PROJECT})...")
    try:
        client = bigquery.Client(project=GCP_PROJECT)
        dataset_id = f"{GCP_PROJECT}.{DB_NAME.lower()}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        
        try:
            client.get_dataset(dataset_id)
            print(f"   ✅ Dataset '{dataset_id}' encontrado.")
        except NotFound:
            client.create_dataset(dataset, timeout=30)
            print(f"   ✨ Dataset criado.")
            
        # Verifica tabela
        table_id = f"{dataset_id}.app_logs"
        try:
            client.get_table(table_id)
            print(f"   ✅ Tabela 'app_logs' verificada.")
        except NotFound:
            print(f"   ✨ Tabela 'app_logs' criada (lazy).")

    except Exception as e:
        print(f"   ❌ Erro no BigQuery: {e}")

def init_azure_cosmos():
    print(f"\n[AZURE] 🪐 Conectando ao Cosmos DB...")
    
    if not COSMOS_URL or len(COSMOS_KEY) < 10:
        print("   ⚠️ Pulei: Credenciais inválidas no .env")
        return

    # Debug de segurança (mostra apenas o início da chave para conferência)
    print(f"   🔑 Usando chave (início): {COSMOS_KEY[:5]}...")

    try:
        client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
        
        # Cria o Banco de Dados
        database = client.create_database_if_not_exists(id=DB_NAME)
        print(f"   ✅ Database '{database.id}' conectado!")
        
        # Cria um Container
        container = database.create_container_if_not_exists(
            id="Interactions", 
            partition_key=PartitionKey(path="/session_id"),
            offer_throughput=400
        )
        print(f"   ✅ Container '{container.id}' pronto.")
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"   ❌ Erro de Autorização Azure: Verifique se o firewall do Cosmos DB permite acesso público ou seu IP.")
        print(f"   Detalhe: {e.status_code} - {e.message}")
    except Exception as e:
        print(f"   ❌ Erro genérico Cosmos: {e}")

def init_databases():
    print("🚀 Inicializando Camada de Dados Multi-Cloud...")
    init_google_bigquery()
    init_azure_cosmos()

if __name__ == "__main__":
    init_databases()
