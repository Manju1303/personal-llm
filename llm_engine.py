import os
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.groq import Groq

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self, provider="ollama", model_name="llama3", api_key=None):
        """
        Initialize the LLM Engine.
        """
        self.provider = provider
        self.model_name = model_name
        
        try:
            if provider == "gemini":
                if not api_key: raise ValueError("Gemini API Key missing.")
                # FIX: Removing 'models/' prefix as it often causes 404s in newer libs
                self.llm = Gemini(model="gemini-1.5-flash", api_key=api_key)
                self.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=api_key)
            
            elif provider == "groq":
                if not api_key: raise ValueError("Groq API Key missing.")
                self.llm = Groq(model=model_name, api_key=api_key)
                # Groq doesn't provide embeddings. We MUST use another provider.
                # Detailed logic: You can't run Ollama on Cloud.
                # So for Groq, we'll try to use Gemini Embeddings (requires Google Key!).
                # But to keep it simple, we will assume user has Google Key in env for embeddings?
                # Actually, worst case: No embeddings for Groq (Chat only).
                # Let's use Gemini Embeddings as default Cloud fallback.
                # NOTE: This implies users need a Google Key even for Groq RAG.
                self.embed_model = GeminiEmbedding(model_name="models/embedding-001") # Tries to find env key

            else: # Ollama
                self.llm = Ollama(model=model_name, request_timeout=360.0)
                self.embed_model = OllamaEmbedding(model_name=model_name)

            # Apply Settings
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            
        except Exception as e:
            logger.error(f"Failed to initialize {provider}: {e}")
            raise e

        self.index = None

    def create_index(self, input_files):
        """
        Creates a VectorStoreIndex from a list of input files.
        """
        try:
            if not input_files:
                return "No files provided."
            
            logger.info(f"Processing {len(input_files)} files...")
            self.index = VectorStoreIndex.from_documents(input_files)
            logger.info("Index created successfully.")
            return self.index
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise e

    def get_chat_engine(self):
        """
        Returns a chat engine with memory.
        """
        if not self.index:
            # If no files, return detailed chat engine (just LLM + Memory)
            # We need to create an empty index or just use the LLM directly with memory buffer.
            # LlamaIndex makes it easiest to just have an index.
            # Let's create an empty index if none exists.
            self.index = VectorStoreIndex.from_documents([])
        
        # Use "context" mode: capable of using the index + conversation history
        return self.index.as_chat_engine(
            chat_mode="context", 
            llm=self.llm,
            verbose=True
        )
