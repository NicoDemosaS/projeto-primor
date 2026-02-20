# Usa uma imagem oficial do Python levinha
FROM python:3.11-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código do seu projeto
COPY . .

# Expõe a porta que o Gunicorn vai rodar internamente (ex: 5000)
EXPOSE 5000

# Comando para rodar a aplicação com Gunicorn 
# (ajuste 'app:app' para o nome do seu arquivo principal e a instância do Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]