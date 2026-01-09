import os
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalLLMEngine:
    def __init__(self, model_name="llama3", embedding_model="llama3"):
        """
        Initialize the Local LLM Engine with Ollama for both Generation and Embeddings.
        """
        self.model_name = model_name
        
        # Setup LLM
        try:
            logger.info(f"Connecting to Ollama with model: {model_name}")
            self.llm = Ollama(model=model_name, request_timeout=360.0)
            Settings.llm = self.llm
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise e

        # Setup Embeddings (Ollama)
        try:
            logger.info(f"Connecting to Ollama for embeddings: {embedding_model}")
            # Note: Using the same model for embeddings is often fine for simple use cases,
            # or user can pull 'nomic-embed-text'
            self.embed_model = OllamaEmbedding(model_name=embedding_model)
            Settings.embed_model = self.embed_model
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
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
            
            # Save uploaded files temporarily to read them with SimpleDirectoryReader
            # NOTE: Streamlit UploadedFile objects are file-like, but SimpleDirectoryReader usually wants paths.
            # We will handle the conversion in file_handler.py or here.
            # To adhere to LlamaIndex standards, best to just load Documents directly if possible,
            # but SimpleDirectoryReader is easiest.
            # For this 'engine', let's assume we pass in a list of 'Document' objects from LlamaIndex.
            
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
