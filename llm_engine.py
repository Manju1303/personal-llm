import os
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self, provider="ollama", model_name="llama3", api_key=None):
        """
        Initialize the LLM Engine with either Ollama (Local) or Gemini (Cloud).
        """
        self.provider = provider
        self.model_name = model_name
        
        try:
            if provider == "gemini":
                logger.info("Initializing Google Gemini...")
                if not api_key:
                    raise ValueError("API Key is required for Gemini.")
                
                # Setup Gemini LLM
                self.llm = Gemini(model="models/gemini-1.5-flash", api_key=api_key)
                
                # Setup Gemini Embeddings
                self.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=api_key)
                
            else: # Default to Ollama
                logger.info(f"Initializing Local Ollama: {model_name}")
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

    def get_query_engine(self):
        """
        Returns a query engine for the created index.
        """
        if not self.index:
            raise ValueError("Index not created. Upload and process files first.")
        
        return self.index.as_query_engine(streaming=True)
