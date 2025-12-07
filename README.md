# dpoloniakit

Kit de ferramentas pessoal e laboratório de experiências.

## 🚀 Instalação Local (Python)

1. **Configurar ambiente:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Segurança:**
   - Cria um ficheiro `.env` baseado no `.env.example`.
   - Adiciona as tuas chaves (Azure, OpenAI, etc) no `.env`.

---

## 🐳 Rodando com Docker

Para isolar a aplicação e rodar num container sem instalar nada no PC:

1. **Construir a imagem:**
   ```bash
   docker build -t dpoloniakit .
   ```

2. **Rodar o container:**
   ```bash
   # -p 8501:8501 : Abre a porta do Streamlit no browser
   # --env-file .env : Passa as chaves de segurança para o container
   docker run -p 8501:8501 --env-file .env dpoloniakit
   ```
