#!/bin/bash

# Actualizar y preparar el sistema
echo "Actualizando el sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias generales necesarias
echo "Instalando dependencias generales..."
sudo apt install -y python3 python3-pip python3-venv build-essential libsndfile1 ffmpeg libatlas-base-dev

# Instalación de dependencias para Faster Whisper (puede ser necesario compilar)
echo "Instalando dependencias para Faster Whisper..."
sudo apt install -y cmake libsndfile-dev

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
python3 -m venv tars_env
source tars_env/bin/activate
pip install --upgrade pip

# Instalar las dependencias del proyecto
pip install -r requirements.txt

# Instalar Faster Whisper desde el código fuente
echo "Instalando Faster Whisper..."
git clone https://github.com/guillaumelaurell/faster-whisper.git
cd faster-whisper
git checkout main
pip install .

# Instalar Langchain y Chromadb (si no están en requirements.txt)
pip install langchain chromadb

# Configuración adicional para Eleven Labs TTS (necesitas la API key de Eleven Labs)
echo "Por favor, asegúrate de tener tu API Key y Voice ID de Eleven Labs listos para configurar el TTS."

# Descargar Whisper en el directorio adecuado (puede requerir GPU o CPU optimizada)
echo "Descargando y configurando Whisper..."
pip install faster-whisper

# Verificación final
echo "Instalación completada. Activa el entorno con 'source tars_env/bin/activate' y luego ejecuta 'python main.py' para iniciar TARS."
