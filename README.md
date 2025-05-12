# GLaDOS/TARS_Pi - Advanced Conversational AI Assistant

GLaDOS/TARS_Pi is an advanced conversational AI assistant that combines speech recognition, natural language processing, and text-to-speech capabilities to create an interactive and engaging experience. It features multiple character personalities and can maintain context-aware conversations.

## Features

- **Speech Recognition**: Real-time voice input using Faster Whisper
- **Text-to-Speech**: High-quality voice synthesis using ElevenLabs API
- **Multiple Personalities**: Choose between different AI characters (TARS, GLaDOS, etc.)
- **Context Awareness**: Maintains conversation history and context
- **RAG Integration**: Retrieves relevant information from documents
- **LM Studio Integration**: Uses local LLM for responses
- **Bilingual Support**: Works with both English and Spanish

## Hardware Requirements
For the PC used as Server
- **CPU**: Any modern processor (Intel/AMD)
- **GPU**: Any Nvidia Graphic Card with with CUDA support 
- **RAM**: Minimum 8GB recommended
- **VRAM**: Minimum 4GB recommended 
- **Internet**: Required for ElevenLabs API and LM Studio
  
For Running the code
- **Raspberry Pi 4 or Higher**  
- **OS**: Rasberry OS
- **RAM**: 4GB recommended
- **Storage**: at least 3GB
## Software Requirements

- Python 3.8 or higher
- LM Studio running locally
- FFmpeg
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Silverx1242/GLaDOS_PI.git
cd GLaDOS_PI
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Create a `.env` file in the project root with the following variables:
```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
LM_STUDIO_URL=localhost:1234
LM_STUDIO_MODEL=your_model_name
EMBEDDING_MODEL=your_embedding_model
WHISPER_MODEL_SIZE=tiny
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=float32
DB_DIR=db
DATA_DIR=data
MAX_RETRIES=3
RETRY_DELAY=3
```

## Project Structure

```
TARS/
├── src/
│   ├── main.py          # Main application entry point
│   ├── stt.py           # Speech-to-text functionality
│   ├── tts.py           # Text-to-speech functionality
│   ├── llm.py           # Language model integration
│   ├── rag.py           # Retrieval Augmented Generation
│   ├── characters.py    # Character definitions
│   └── ui.py           # User interface utilities
├── data/                # Directory for knowledge base documents
├── db/                  # Vector database storage
├── requirements.txt     # Python dependencies
└── install.sh          # Installation script
```

## Code Overview

### Main Components

1. **Speech Recognition (stt.py)**
   - Uses Faster Whisper for real-time speech-to-text
   - Implements silence detection for natural conversation flow
   - Supports multiple languages

2. **Text-to-Speech (tts.py)**
   - Integrates with ElevenLabs API for high-quality voice synthesis
   - Supports multiple voice IDs for different characters
   - Handles audio playback using Pygame

3. **Language Model (llm.py)**
   - Connects to local LM Studio instance
   - Maintains conversation memory
   - Handles context and character-specific responses

4. **RAG System (rag.py)**
   - Implements document retrieval using ChromaDB
   - Supports document embedding and similarity search
   - Maintains a vector database for quick information retrieval

5. **Character System (characters.py)**
   - Defines different AI personalities
   - Manages character-specific prompts and voice IDs
   - Allows for easy addition of new characters

## Usage

1. Start LM Studio and load your preferred model
2. Run the main application:
```bash
python src/main.py
```

3. Select your preferred character when prompted
4. Choose between voice or text input
5. Start conversing with TARS!

## Adding New Characters

To add a new character, modify `characters.py`:

```python
CHARACTERS = {
    "new_character": Character(
        name="Character Name",
        description="Character description",
        system_prompt="""Character's personality and behavior""",
        voice_id="elevenlabs_voice_id"
    )
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ElevenLabs for the TTS API
- LM Studio for the local LLM capabilities
- Faster Whisper for speech recognition
- ChromaDB for vector storage 
