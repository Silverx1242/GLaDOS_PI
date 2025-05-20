from stt import listen
from llm import get_llm_response
from ui import show_message, show_status, show_loading, show_message_with_tts
from rag import load_documents, retrieve_relevant_docs
from characters import get_character, get_character_list
import traceback
import time
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Obtener valores desde .env, usar 3 como valor por defecto si no están definidos
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 3))

def check_llm_server():
    """Verificar si el servidor LLM está disponible"""
    try:
        response = requests.get("http://localhost:1234/v1/models")
        return response.status_code == 200
    except RequestException:
        return False

def wait_for_llm_server():
    """Esperar a que el servidor LLM esté disponible"""
    retries = 0
    while not check_llm_server() and retries < MAX_RETRIES:
        show_status(f"Esperando al servidor LLM... Intento {retries + 1}/{MAX_RETRIES}", "warning")
        time.sleep(RETRY_DELAY)
        retries += 1
    return check_llm_server()

def select_character():
    """Permitir al usuario seleccionar un personaje por número"""
    characters = get_character_list()
    character_names = list(characters.keys())
    
    show_status("Personajes disponibles:", "info")
    for idx, (name, desc) in enumerate(characters.items(), 1):
        show_message("INFO", f"{idx}. {name}: {desc}")
    
    while True:
        show_status("Ingresa el número del personaje que deseas usar:", "info")
        choice = input().strip().lower()
        
        # Verificar si es un número
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(character_names):
                character = get_character(character_names[idx])
                show_status(f"Personaje seleccionado: {character.name}", "success")
                return character_names[idx]
            else:
                show_status("Número de personaje no válido. Intenta de nuevo.", "error")
        else:
            show_status("Entrada no válida. Ingresa un número.", "error")

def get_user_input():
    """Obtener entrada del usuario por voz o texto, con voz como predeterminado"""
    try:
        # Intentar usar el micrófono primero
        show_status("Probando micrófono...", "info")
        show_status("Por favor, di algo para probar el micrófono...", "info")
        show_status("(Tienes 5 segundos para hablar)", "info")
        test_audio = listen()
        if test_audio is not None:
            show_status("Modo voz activado (predeterminado)", "success")
            return "voice"
    except Exception as e:
        show_status("No se pudo acceder al micrófono", "warning")
    
    # Si hay error con el micrófono, mostrar opciones
    show_status("¿Cómo deseas interactuar?", "info")
    show_message("INFO", "1. Voz (requiere micrófono)")
    show_message("INFO", "2. Texto (escribir)")
    show_status("Tienes 10 segundos para elegir...", "info")
    
    # Esperar la entrada del usuario con timeout
    import sys
    import select
    
    timeout = 10  # segundos
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            choice = input().strip()
            if choice == "1":
                try:
                    show_status("Por favor, di algo para probar el micrófono...", "info")
                    test_audio = listen()
                    if test_audio is not None:
                        show_status("Modo voz activado", "success")
                        return "voice"
                    else:
                        show_status("No se pudo acceder al micrófono. Por favor, selecciona otra opción.", "error")
                except Exception:
                    show_status("Error al acceder al micrófono. Por favor, selecciona otra opción.", "error")
            elif choice == "2":
                show_status("Modo texto activado", "success")
                return "text"
            else:
                show_status("Opción no válida. Ingresa 1 o 2.", "error")
    
    # Si no se eligió nada, usar texto por defecto
    show_status("Tiempo agotado. Activando modo texto por defecto.", "warning")
    return "text"

def get_text_input():
    """Obtener texto del usuario"""
    show_status("Escribe tu mensaje:", "info")
    return input().strip()

def main():
    try:
        show_status("Iniciando TARS...", "info")
        show_loading("Inicializando componentes", 2)
        
        # Verificar servidor LLM
        if not wait_for_llm_server():
            show_status("No se pudo conectar al servidor LLM. Asegúrate de que LM Studio esté corriendo.", "error")
            return

        show_status("TARS está listo", "success")
        show_status("Cargando documentos...", "loading")
        load_documents("data")  # Cargar documentos al inicio
        show_status("Documentos cargados", "success")

        # Seleccionar personaje
        current_character = select_character()
        character = get_character(current_character)
        show_status(f"Actuando como: {character.name}", "info")

        # Seleccionar modo de entrada
        input_mode = get_user_input()

        while True:
            try:
                # Obtener entrada del usuario según el modo seleccionado
                if input_mode == "voice":
                    show_status("Escuchando...", "info")
                    text = listen()
                else:
                    text = get_text_input()

                if not text:
                    continue

                show_message("Usuario", text)

                # Reintentos para recuperar contexto
                show_status("Buscando contexto relevante...", "thinking")
                context = None
                for attempt in range(MAX_RETRIES):
                    try:
                        context = retrieve_relevant_docs(text)
                        break
                    except Exception as e:
                        if attempt == MAX_RETRIES - 1:
                            show_status(f"No se pudo recuperar contexto después de {MAX_RETRIES} intentos", "error")
                            context = ""
                        time.sleep(RETRY_DELAY)

                # Reintentos para consulta LLM
                show_status("Procesando respuesta...", "thinking")
                response = None
                for attempt in range(MAX_RETRIES):
                    try:
                        response = get_llm_response(text, character, context)
                        break
                    except Exception as e:
                        if attempt == MAX_RETRIES - 1:
                            show_status(f"No se pudo obtener respuesta del LLM después de {MAX_RETRIES} intentos", "error")
                            response = "Lo siento, estoy teniendo problemas para procesar tu solicitud."
                        time.sleep(RETRY_DELAY)

                if response:
                    # Mostrar y reproducir la respuesta
                    show_message_with_tts(character.name, response, character)
                    
                    # Esperar más tiempo después de la respuesta antes de volver a escuchar
                    show_status("Esperando 1 segundo antes de escuchar...", "info")
                    time.sleep(1)

            except Exception as e:
                show_status(f"Fallo en loop principal: {str(e)}", "error")
                traceback.print_exc()
                time.sleep(RETRY_DELAY)  # Esperar antes de reintentar

    except KeyboardInterrupt:
        show_message("SISTEMA", "\n¡Hasta luego!")
    except Exception as e:
        show_status(f"No se pudo iniciar TARS: {str(e)}", "fatal")
        traceback.print_exc()

if __name__ == "__main__":
    main()
