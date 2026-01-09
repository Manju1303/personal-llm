import streamlit as st
from llm_engine import LLMEngine
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

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Provider Selection
    provider = st.radio(
        "Select Mode",
        ["Local (Ollama)", "Cloud (Google Gemini)"],
        index=0,
        help="Use 'Local' for privacy/offline. Use 'Cloud' for mobile access when PC is off."
    )
    
    api_key = None
    model_name = "llama3"
    
    if "Cloud" in provider:
        st.info("☁️ Cloud Mode: Works anywhere! Requires API Key.")
        
        # Try to load from Secrets/Env
        default_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        
        api_key = st.text_input("Google AI Studio Key", value=default_key, type="password", help="Get free key at aistudio.google.com")
        provider_code = "gemini"
        if not api_key:
            st.warning("⚠️ Please enter API Key to proceed.")
    else:
        st.success("🏠 Local Mode: Runs on your PC. Private & Free.")
        model_name = st.selectbox(
            "Select Local Model",
            ["llama3", "mistral", "gemma", "phi3"],
            index=0
        )
        provider_code = "ollama"
    
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
    if provider_code == "gemini" and not api_key:
        st.error("Please enter a Google API Key first!")
    else:
        with st.spinner(f"Processing files using {provider}..."):
            try:
                # Initialize Engine
                # Re-initialize if provider changed or first run
                st.session_state.engine = LLMEngine(
                    provider=provider_code, 
                    model_name=model_name, 
                    api_key=api_key
                )

                # Process Files
                documents = FileHandler.process_uploaded_files(uploaded_files)
                
                # Create Index
                st.session_state.engine.create_index(documents)
                st.session_state.query_engine = st.session_state.engine.get_query_engine()
                
                st.success(f"Successfully processed {len(uploaded_files)} files!")
            except Exception as e:
                msg = str(e)
                if "Connection refused" in msg or "Max retries exceeded" in msg:
                    st.error("❌ **Could not connect to Ollama.**")
                    st.warning("""
                    **Are you running this on the Cloud (Streamlit Share)?**
                    If yes, **Local (Ollama)** will NOT work because it cannot see your computer.
                    👉 **Please switch to 'Cloud (Google Gemini)' in the Sidebar.**
                    
                    **Are you running this locally?**
                    👉 Make sure Ollama is running! Open a terminal and type `ollama serve`.
                    """)
                else:
                    st.error(f"An error occurred: {msg}")

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
            # Check for Engine Initialization
            if not st.session_state.engine:
                 if provider_code == "gemini" and not api_key:
                     full_response = "⚠️ Please enter API Key in sidebar."
                     message_placeholder.markdown(full_response)
                     raise ValueError("Missing API Key")
                 
                 st.session_state.engine = LLMEngine(
                    provider=provider_code, 
                    model_name=model_name,
                    api_key=api_key
                 )
            
            if st.session_state.query_engine:
                # RAG Mode
                streaming_response = st.session_state.query_engine.query(prompt)
                
                # Stream the response
                for token in streaming_response.response_gen:
                    full_response += token
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            else:
                # Chat Mode (No RAG)
                resp = st.session_state.engine.llm.stream_complete(prompt)
                for part in resp:
                    full_response += part.delta
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)

        except Exception as e:
            if not full_response: # Don't overwrite if we already set a specific error message
                st.error(f"Error: {e}")
                full_response = f"Error: {e}"
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
