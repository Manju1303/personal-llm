import os
import tempfile
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, Document

class FileHandler:
    @staticmethod
    def process_uploaded_files(uploaded_files):
        """
        Takes Streamlit UploadedFile objects, saves them temporarily, 
        and uses LlamaIndex Reader to load them as Documents.
        """
        documents = []
        temp_dir = tempfile.mkdtemp()
        
        file_paths = []
        
        try:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
            
            # Use SimpleDirectoryReader to load the files
            # It handles PDF, DOCX, TXT, etc. automatically if libs are installed.
            reader = SimpleDirectoryReader(input_dir=temp_dir)
            documents = reader.load_data()
            
            return documents
        except Exception as e:
            raise e
        finally:
            # Cleanup optionally? For now, temp dir persists until OS cleanup 
            # or we could delete it, but LlamaIndex might lazy load?
            # Usually strict cleanup is good, but for now let's just leave it 
            # as safe within the run duration.
            pass

    @staticmethod
    def read_text_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
