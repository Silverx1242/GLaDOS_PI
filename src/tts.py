import os
import requests
import tempfile
from dotenv import load_dotenv
from ui import show_status
import pygame
import time

# Cargar variables de entorno
load_dotenv()

class TTS:
    def __init__(self):
        self.api_key = os.environ['ELEVENLABS_API_KEY']
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
        # Inicializar pygame mixer con parámetros específicos
        try:
            pygame.mixer.quit()  # Asegurarse de que no hay instancias previas
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            show_status("Sistema de audio inicializado correctamente", "success")
        except Exception as e:
            show_status(f"Error al inicializar el sistema de audio: {str(e)}", "error")
        
        if not self.api_key:
            show_status("Error: No hay API key de ElevenLabs configurada", "error")
            show_status("Por favor, configura ELEVENLABS_API_KEY en tu archivo .env", "error")

    def generate_speech(self, text, voice_id):
        """Generar audio a partir de texto usando ElevenLabs"""
        try:
            if not self.api_key:
                show_status("Error: No hay API key de ElevenLabs configurada", "error")
                return None

            if not voice_id:
                show_status("Error: No hay Voice ID configurado para el personaje", "error")
                return None

            show_status(f"Usando Voice ID: {voice_id}", "info")
            show_status("Generando audio...", "loading")
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }

            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            show_status(f"Enviando solicitud a ElevenLabs...", "info")
            response = requests.post(
                f"{self.base_url}/{voice_id}",
                json=data,
                headers=headers
            )

            if response.status_code == 200:
                show_status("Audio generado correctamente", "success")
                # Guardar el audio en un archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_file.write(response.content)
                    show_status(f"Audio guardado en: {temp_file.name}", "info")
                    return temp_file.name
            else:
                show_status(f"Error en la API de ElevenLabs: {response.status_code}", "error")
                show_status(f"Respuesta: {response.text}", "error")
                return None

        except Exception as e:
            show_status(f"Error al generar audio: {str(e)}", "error")
            return None

    def play_audio(self, audio_file):
        """Reproducir un archivo de audio"""
        try:
            if not audio_file:
                return

            show_status("Reproduciendo audio...", "info")
            
            # Asegurarse de que el mixer esté limpio
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except:
                pass
            
            # Verificar que el archivo existe
            if not os.path.exists(audio_file):
                show_status(f"Error: El archivo de audio no existe: {audio_file}", "error")
                return
            
            # Verificar el tamaño del archivo
            file_size = os.path.getsize(audio_file)
            show_status(f"Tamaño del archivo de audio: {file_size} bytes", "info")
            
            if file_size == 0:
                show_status("Error: El archivo de audio está vacío", "error")
                return
            
            # Cargar y reproducir el audio
            try:
                show_status("Cargando archivo de audio...", "info")
                pygame.mixer.music.load(audio_file)
                show_status("Iniciando reproducción...", "info")
                pygame.mixer.music.play()
                
                # Esperar a que termine la reproducción
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    time.sleep(0.1)  # Pequeña pausa para no saturar la CPU
                
                # Asegurarse de que el mixer esté limpio
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                
                show_status("Audio reproducido", "success")
            except Exception as e:
                show_status(f"Error al reproducir audio: {str(e)}", "error")
            finally:
                # Limpiar el archivo temporal
                try:
                    os.unlink(audio_file)
                except:
                    pass

        except Exception as e:
            show_status(f"Error al reproducir audio: {str(e)}", "error")
            # Asegurarse de que el mixer esté limpio incluso en caso de error
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except:
                pass

    def speak(self, text, voice_id):
        """Generar y reproducir audio en un solo paso"""
        show_status(f"Preparando texto para TTS: {text[:50]}...", "info")
        audio_file = self.generate_speech(text, voice_id)
        if audio_file:
            self.play_audio(audio_file)

# Instancia global de TTS
tts_engine = TTS()

def speak(text, voice_id):
    """Función de conveniencia para usar el TTS"""
    tts_engine.speak(text, voice_id)
