# 202512-dpoloniakit

Projeto de integração Multi-Cloud AI (Google Vertex AI & Azure OpenAI) preparado para desenvolvimento escalável.

## 🚀 Tech Stack

* **Linguagem:** Python 3.11
* **Containerização:** Docker
* **Clouds:**
    * 🟢 **Google Cloud:** Vertex AI, Gemini Pro, BigQuery
    * 🔵 **Microsoft Azure:** Azure OpenAI, AI Search, CosmosDB
    * 🟣 **OpenAI:** API Padrão

## 🛠️ Configuração Inicial (Local)

### 1. Clonar e preparar ambiente
```bash
git clone https://github.com/dpolonia/202512-dpoloniakit.git
cd 202512-dpoloniakit

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Variáveis de Ambiente
Copie o exemplo e preencha com suas chaves de API:
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves (Google, Azure, OpenAI)
```

---

## ☁️ Autenticação Cloud

**Google Cloud (Vertex AI):**
Certifique-se de ter o [gcloud CLI](https://cloud.google.com/sdk/docs/install) instalado e autenticado:
```bash
gcloud auth application-default login
```

**Azure:**
As chaves são gerenciadas diretamente via variáveis de ambiente no arquivo `.env`.

---

## 🐳 Rodando com Docker

Para isolar a aplicação e rodar em container:

```bash
# 1. Construir a imagem
docker build -t snshadb-image .

# 2. Rodar o container (passando as variáveis de ambiente)
docker run --env-file .env snshadb-image
```

## 🧪 Scripts de Teste

O projeto inclui scripts para validar a conexão com as clouds:

* `python setup_google.py` -> Testa conexão com Vertex AI (Gemini).
* `python setup_azure.py` -> Testa conexão com Azure OpenAI.

