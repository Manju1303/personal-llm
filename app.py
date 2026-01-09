import streamlit as st
from llm_engine import LocalLLMEngine
from file_handler import FileHandler
import time

st.set_page_config(page_title="Personal Multilingual LLM", page_icon="🤖", layout="wide")

# Custom CSS for "Premium" look
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stChatInput {
        border-radius: 20px;
    }
    .stMarkdown {
        font-family: 'Inter', sans-serif;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Personal Multilingual LLM")
st.markdown("### Your Offline, Secure Data Assistant")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    model_name = st.selectbox(
        "Select Local Model",
        ["llama3", "mistral", "gemma", "phi3"],
        index=0,
        help="Make sure you have this model installed via `ollama pull <model>`"
    )
    
    st.divider()
    
    st.header("📂 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload Documents (PDF, DOCX, TXT)", 
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'csv']
    )
    
    process_btn = st.button("🚀 Process Files", type="primary")
    
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "engine" not in st.session_state:
    st.session_state.engine = None

if "query_engine" not in st.session_state:
    st.session_state.query_engine = None

# Logic for Processing Files
if process_btn and uploaded_files:
    with st.spinner("Processing files... This runs locally and might take a moment."):
        try:
            # Initialize Engine
            if not st.session_state.engine:
                st.session_state.engine = LocalLLMEngine(model_name=model_name, embedding_model=model_name)
            
            # Update Model if changed
            if st.session_state.engine.model_name != model_name:
                 st.session_state.engine = LocalLLMEngine(model_name=model_name, embedding_model=model_name)

            # Process Files
            documents = FileHandler.process_uploaded_files(uploaded_files)
            
            # Create Index
            st.session_state.engine.create_index(documents)
            st.session_state.query_engine = st.session_state.engine.get_query_engine()
            
            st.success(f"Successfully processed {len(uploaded_files)} files!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Ensure Ollama is running (`ollama serve`) and the model is pulled.")

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask something about your documents..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            if st.session_state.query_engine:
                # RAG Mode
                streaming_response = st.session_state.query_engine.query(prompt)
                
                # Stream the response
                for token in streaming_response.response_gen:
                    full_response += token
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            else:
                # Chat Mode (No RAG) - Fallback to just Ollama chat if no files
                # Quick hack: use the engine's llm directly if initialized, else init it
                if not st.session_state.engine:
                     st.session_state.engine = LocalLLMEngine(model_name=model_name)
                
                resp = st.session_state.engine.llm.stream_complete(prompt)
                for part in resp:
                    full_response += part.delta
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error generating response: {e}")
            full_response = "Error: Could not generate response. Is Ollama running?"
            message_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
