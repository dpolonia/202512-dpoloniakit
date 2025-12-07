# Usar uma imagem oficial leve do Python
FROM python:3.11-slim

# Variáveis para otimização do Python no Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Comando padrão: Executa o controlador principal testando tudo
CMD ["python", "main.py", "--provider", "all"]
