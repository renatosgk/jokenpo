FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg2 \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc \
       -o /usr/share/keyrings/microsoft.asc \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.asc] \
       https://packages.microsoft.com/debian/12/prod bookworm main" \
       > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY jokenpo.py .

RUN pip install --no-cache-dir flask pyodbc

EXPOSE 80

CMD ["python", "jokenpo.py"]
