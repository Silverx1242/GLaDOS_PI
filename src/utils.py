import os
from datetime import datetime
import time

# Códigos de color ANSI
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

# Símbolos para estados
class Symbols:
    INFO = 'ℹ️'
    ERROR = '❌'
    SUCCESS = '✅'
    WARNING = '⚠️'
    MICROPHONE = '🎤'
    SPEAKER = '🔊'
    THINKING = '🤔'
    LOADING = '⏳'

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def show_message(role, text, tts_callback=None):
    timestamp = get_timestamp()
    
    # Seleccionar color y símbolo según el rol y estado
    if role.upper() == "INFO":
        color = Colors.BLUE
        symbol = Symbols.INFO
    elif role.upper() == "ERROR":
        color = Colors.RED
        symbol = Symbols.ERROR
    elif role.upper() == "FATAL":
        color = Colors.RED
        symbol = Symbols.ERROR
    elif role.upper() == "TARS":
        color = Colors.GREEN
        symbol = Symbols.SPEAKER
    elif role.upper() == "USUARIO":
        color = Colors.CYAN
        symbol = Symbols.MICROPHONE
    else:
        color = Colors.WHITE
        symbol = ""

    # Mostrar mensaje con formato
    print(f"{color}[{timestamp}] {symbol} {role.upper()}: {text}{Colors.RESET}\n")
    
    # Activar TTS solo para mensajes de TARS si hay callback
    if role.upper() == "TARS" and tts_callback:
        tts_callback(text)

def show_status(message, status="info"):
    """Mostrar mensajes de estado del sistema"""
    timestamp = get_timestamp()
    
    if status == "info":
        color = Colors.BLUE
        symbol = Symbols.INFO
    elif status == "error":
        color = Colors.RED
        symbol = Symbols.ERROR
    elif status == "success":
        color = Colors.GREEN
        symbol = Symbols.SUCCESS
    elif status == "warning":
        color = Colors.YELLOW
        symbol = Symbols.WARNING
    elif status == "thinking":
        color = Colors.PURPLE
        symbol = Symbols.THINKING
    elif status == "loading":
        color = Colors.YELLOW
        symbol = Symbols.LOADING
    else:
        color = Colors.WHITE
        symbol = ""

    print(f"{color}[{timestamp}] {symbol} {message}{Colors.RESET}")

def show_loading(message, duration=1):
    """Mostrar una animación de carga"""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for _ in range(duration * 10):
        for char in chars:
            print(f"\r{Colors.YELLOW}{char} {message}{Colors.RESET}", end="")
            time.sleep(0.1)
    print("\r" + " " * (len(message) + 2) + "\r", end="") 