FROM python:3.11-slim

# Instalar dependencias necesarias para compilar/usar ODBC y librerías del sistema requeridas por el driver de MS SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

# Agregar el repositorio de Microsoft como origen de confianza directa (evita error de firma SHA1 de MS en Debian Trixie 2026)
RUN echo "deb [arch=amd64,arm64,armhf trusted=yes] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Instalar el driver MS ODBC 18
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
