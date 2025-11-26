# Usar imagen oficial de Python 3.7
FROM python:3.7-slim

# Instalar herramientas necesarias y git
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias
COPY requirements-docker.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copiar todo el proyecto al contenedor
COPY . .

# Exponer puerto 8000
EXPOSE 8000

# Comando para ejecutar Django en producción
CMD ["gunicorn", "blog.wsgi:application", "--bind", "0.0.0.0:8000"]
