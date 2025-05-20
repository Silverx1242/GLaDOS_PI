import os
import json
import hashlib
import chromadb
import requests
from chromadb.config import Settings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
import time
from functools import lru_cache
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de directorios
DB_DIR = os.environ['DB_DIR', 'db']
DATA_DIR = os.environ['DATA_DIR', 'data']
INDEX_PATH = os.path.join(DB_DIR, "processed_files.json")
CACHE_SIZE = 1000  # Número de embeddings a cachear

# Crear directorios si no existen
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Configuración de LM Studio
LM_STUDIO_URL = os.environ['LM_STUDIO_URL']
EMBEDDING_MODEL = os.environ['EMBEDDING_MODEL']

if not LM_STUDIO_URL.startswith('http://'):
    LM_STUDIO_URL = f'http://{LM_STUDIO_URL}'

class NomicLlamaCppEmbeddings(Embeddings):
    def __init__(self):
        self.endpoint = f"{LM_STUDIO_URL}/v1/embeddings"
        self._cache = {}
        self._last_cleanup = time.time()
        self._cleanup_interval = 3600  # 1 hora

    def _cleanup_cache(self):
        if time.time() - self._last_cleanup > self._cleanup_interval:
            self._cache.clear()
            self._last_cleanup = time.time()

    @lru_cache(maxsize=CACHE_SIZE)
    def _embed(self, text):
        try:
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "model": EMBEDDING_MODEL,
                "input": text
            }
            response = requests.post(self.endpoint, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"[Embedding] Error al generar embedding: {e}")
            return [0.0] * 384  # fallback

    def embed_documents(self, texts):
        self._cleanup_cache()
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        self._cleanup_cache()
        return self._embed(text)

embedding_function = NomicLlamaCppEmbeddings()

# Nueva configuración de ChromaDB
client = chromadb.PersistentClient(path=DB_DIR)
vectorstore = None

def _file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_documents(directory):
    global vectorstore

    try:
        processed = {}
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, "r") as f:
                processed = json.load(f)

        documents = []
        for file in os.listdir(directory):
            if file.endswith(".txt"):
                full_path = os.path.join(directory, file)
                f_hash = _file_hash(full_path)

                if processed.get(file) == f_hash:
                    continue

                loader = TextLoader(full_path, encoding='utf-8')
                docs = loader.load()
                documents.extend(docs)
                processed[file] = f_hash

        if not documents:
            vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embedding_function)
            return

        # Reducir tamaño de chunks para mejor rendimiento
        splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
        chunks = splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(chunks, embedding_function, persist_directory=DB_DIR)
        vectorstore.persist()

        with open(INDEX_PATH, "w") as f:
            json.dump(processed, f)

    except Exception as e:
        print(f"[RAG] Error cargando documentos: {str(e)}")

def retrieve_relevant_docs(query, k=2):  # Reducido a 2 documentos para mejor rendimiento
    try:
        global vectorstore
        if not vectorstore:
            vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embedding_function)
        docs = vectorstore.similarity_search(query, k=k)
        return "\n".join([d.page_content for d in docs])
    except Exception as e:
        return f"[ERROR] No se pudo recuperar contexto: {str(e)}"
