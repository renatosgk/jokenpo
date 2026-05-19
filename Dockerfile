# Use a imagem base do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo do jogo para o contêiner
COPY jokenpo.py .

# Instala o Flask
RUN pip install --no-cache-dir flask pyodbc

# Expõe a porta 80
EXPOSE 80

# Define o comando para rodar o aplicativo
CMD ["python", "jokenpo.py"]
