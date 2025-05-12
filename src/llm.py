import os
import requests
import json
from dotenv import load_dotenv
from characters import get_character
from utils import show_status
from collections import deque

# Cargar variables de entorno
load_dotenv()

# Configuración de LM Studio
LM_STUDIO_URL = os.environ['LM_STUDIO_URL']
LM_STUDIO_MODEL = os.environ['LM_STUDIO_MODEL']

if not LM_STUDIO_URL.startswith('http://'):
    LM_STUDIO_URL = f'http://{LM_STUDIO_URL}'

# Memoria de conversación
conversation_memory = deque(maxlen=10)  # Mantener las últimas 10 interacciones

def get_llm_response(prompt, character=None, context=None):
    """Obtener respuesta del modelo de lenguaje"""
    try:
        show_status("Procesando respuesta...", "thinking")
        
        # Construir el prompt completo
        system_prompt = """Eres un asistente conversacional. Sigue estas reglas:
1. Sé conciso y directo en tus respuestas
2. No inventes información que no esté en el contexto
3. Si no sabes algo, admítelo honestamente
4. Mantén un tono conversacional y amigable
5. No uses formato markdown ni listas numeradas
6. Responde como si estuvieras en una conversación real
7. Mantén coherencia con las respuestas anteriores"""

        full_prompt = system_prompt + "\n\n"
        
        if character:
            full_prompt += f"Actúa como {character.name}. {character.description}\n\n"
        
        # Agregar historial de conversación
        if conversation_memory:
            full_prompt += "Historial de conversación:\n"
            for user_msg, assistant_msg in conversation_memory:
                full_prompt += f"Usuario: {user_msg}\nAsistente: {assistant_msg}\n\n"
        
        if context:
            full_prompt += f"Contexto relevante:\n{context}\n\n"
        
        full_prompt += f"Usuario: {prompt}\n\nAsistente:"

        # Preparar la solicitud
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": LM_STUDIO_MODEL,
            "prompt": full_prompt,
            "max_tokens": 200,  # Reducido para respuestas más concisas
            "temperature": 0.7,
            "stop": ["Usuario:", "Contexto:", "\n\n"]
        }

        # Realizar la solicitud
        response = requests.post(
            f"{LM_STUDIO_URL}/v1/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            assistant_response = result['choices'][0]['text'].strip()
            
            # Guardar la interacción en la memoria
            conversation_memory.append((prompt, assistant_response))
            
            return assistant_response
        else:
            show_status(f"Error en la API de LM Studio: {response.status_code}", "error")
            return f"[ERROR] Fallo al consultar LM Studio: {response.text}"

    except requests.exceptions.RequestException as e:
        show_status(f"Error de conexión con LM Studio: {str(e)}", "error")
        return f"[ERROR] Fallo al consultar LM Studio: {str(e)}"
    except Exception as e:
        show_status(f"Error inesperado: {str(e)}", "error")
        return f"[ERROR] Error inesperado: {str(e)}"
