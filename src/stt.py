import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import tempfile
import wave
import os
from dotenv import load_dotenv
from utils import show_status, show_loading

# Cargar variables de entorno
load_dotenv()

# Configuración de Whisper desde variables de entorno
model_size = os.getenv('WHISPER_MODEL_SIZE', 'tiny')
device = os.getenv('WHISPER_DEVICE', 'cpu')
compute_type = os.getenv('WHISPER_COMPUTE_TYPE', 'float32')

# Cargar el modelo de Whisper
show_status("Cargando modelo de Whisper...", "loading")
model = WhisperModel(model_size, device=device, compute_type=compute_type)
show_status("Modelo de Whisper cargado", "success")

def detect_silence(audio_data, threshold=0.02, min_silence_duration=2.0, sample_rate=16000):
    """Detectar silencio en el audio"""
    # Calcular la energía del audio
    energy = np.mean(np.abs(audio_data))
    # Convertir duración de silencio a muestras
    min_silence_samples = int(min_silence_duration * sample_rate)
    # Detectar si la energía está por debajo del umbral
    is_silent = energy < threshold
    return is_silent

def record_audio(sample_rate=16000, silence_threshold=0.02, silence_duration=2.0, max_duration=60):
    """Grabar audio del micrófono hasta detectar silencio"""
    show_status("Grabando audio...", "info")
    
    # Buffer para almacenar el audio
    audio_buffer = []
    silence_counter = 0
    silence_samples = int(silence_duration * sample_rate)
    total_samples = 0
    max_samples = int(max_duration * sample_rate)
    
    def callback(indata, frames, time, status):
        if status:
            show_status(f"Error en grabación: {status}", "error")
        audio_buffer.append(indata.copy())
        
        # Detectar silencio
        if detect_silence(indata, threshold=silence_threshold):
            nonlocal silence_counter
            silence_counter += frames
        else:
            silence_counter = 0
        
        # Actualizar contador total de muestras
        nonlocal total_samples
        total_samples += frames
    
    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32', callback=callback):
            show_status("Habla ahora... (esperando silencio para terminar)", "info")
            while silence_counter < silence_samples and total_samples < max_samples:
                sd.sleep(100)  # Esperar 100ms entre verificaciones
            
        # Concatenar todos los fragmentos de audio
        if audio_buffer:
            return np.concatenate(audio_buffer)
        return None
    except Exception as e:
        show_status(f"Error al grabar audio: {str(e)}", "error")
        return None

def save_audio(audio_data, sample_rate=16000):
    """Guardar audio en un archivo temporal"""
    show_status("Procesando audio...", "loading")
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        return temp_file.name

def listen(timeout=30, phrase_time_limit=30):
    try:
        # Grabar audio hasta detectar silencio
        audio_data = record_audio()
        
        if audio_data is None or len(audio_data) == 0:
            show_status("No se detectó audio", "warning")
            return None
        
        # Guardar en archivo temporal
        temp_file = save_audio(audio_data)
        
        # Transcribir
        show_status("Transcribiendo audio...", "thinking")
        segments, _ = model.transcribe(temp_file, language="es")
        text = " ".join([segment.text for segment in segments])
        
        # Limpiar archivo temporal
        os.unlink(temp_file)
        
        if text.strip():
            show_status("Audio transcrito correctamente", "success")
        else:
            show_status("No se detectó habla", "warning")
        
        return text if text.strip() else None
    except Exception as e:
        show_status(f"Error en reconocimiento de voz: {e}", "error")
        return None
