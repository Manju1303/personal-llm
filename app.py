import streamlit as st
from llm_engine import LLMEngine
from file_handler import FileHandler
import os

st.set_page_config(page_title="Personal AI Assistant", page_icon="🤖", layout="wide")

# ---------------------------------------------------------
# Custom CSS for Premium UI
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Main App Background */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #ffffff !important;
    }
    h1 {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(45deg, #2196F3, #21CBF3);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(33, 203, 243, 0.4);
    }

    /* Chat Messages */
    .stChatMessage {
        background-color: #1f2937;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #374151;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar & Config
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Mode Selection with visual icons
    mode = st.radio(
        "Optimization Mode",
        ["☁️ Cloud (Gemini)", "🏠 Local (Ollama)"],
        index=0,
        help="Select Cloud for 24/7 Mobile access. Select Local for Privacy on PC."
    )
    
    st.divider()
    
    api_key = None
    provider_code = "ollama"
    model_name = "llama3"

    if "Cloud" in mode:
        st.info("🟢 **Status:** Online Mode")
        # Secrets/Env loading
        default_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        api_key = st.text_input("Google API Key", value=default_key, type="password")
        
        if not api_key:
            st.warning("⚠️ key required for Cloud functionality.")
        else:
            provider_code = "gemini"
            
    else: # Local
        st.info("🏠 **Status:** Local PC Mode")
        model_name = st.selectbox("Ollama Model", ["llama3", "mistral", "phi3", "gemma"])
        provider_code = "ollama"

    st.divider()
    
    # File Uploader
    st.markdown("### 📚 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Drop files here to chat with them", 
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'csv']
    )
    
    col1, col2 = st.columns(2)
    with col1:
        process_btn = st.button("🧠 Process", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# Main Logic
# ---------------------------------------------------------
st.title("🤖 Personal AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your private AI. Upload a document or just ask me anything."}]

if "engine" not in st.session_state:
    st.session_state.engine = None
if "query_engine" not in st.session_state:
    st.session_state.query_engine = None

# File Processing
if process_btn and uploaded_files:
    if provider_code == "gemini" and not api_key:
        st.error("❌ Please enter your Google API Key in the sidebar first.")
    else:
        with st.status("Processing documents...", expanded=True) as status:
            try:
                st.write("Initializing AI Engine...")
                # Init Engine
                st.session_state.engine = LLMEngine(
                    provider=provider_code,
                    model_name=model_name,
                    api_key=api_key
                )
                
                st.write("Reading files...")
                documents = FileHandler.process_uploaded_files(uploaded_files)
                
                st.write("Creating Vector Index...")
                st.session_state.engine.create_index(documents)
                st.session_state.query_engine = st.session_state.engine.get_query_engine()
                
                status.update(label="✅ Ready! You can now chat with your files.", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="❌ Error Occurred", state="error")
                st.error(f"Error: {str(e)}")
                if "404" in str(e):
                    st.warning("Tip: Check if your API Key is valid and has access to Gemini.")

# Chat Loop
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message..."):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Auto-init if needed
            if not st.session_state.engine:
                if provider_code == "gemini" and not api_key:
                     raise ValueError("Google API Key is missing. Check sidebar.")
                
                st.session_state.engine = LLMEngine(
                    provider=provider_code, 
                    model_name=model_name, 
                    api_key=api_key
                )

            # Generate
            if st.session_state.query_engine:
                response_iter = st.session_state.query_engine.query(prompt).response_gen
            else:
                response_iter = st.session_state.engine.llm.stream_complete(prompt)

            for part in response_iter:
                # Handle different library return types (LlamaIndex vs raw)
                text = part if isinstance(part, str) else getattr(part, 'delta', str(part))
                full_response += text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            err_msg = str(e)
            if "Connection" in err_msg:
                full_response = "❌ **Connection Error**: Could not reach the AI model.\n- If using **Local**, is `ollama serve` running?\n- If using **Cloud**, did you select Cloud Mode?"
            elif "404" in err_msg:
                 full_response = "❌ **Model Error**: Google Gemini model not found.\n- I switched the code to use `gemini-pro`. Please refresh."
            else:
                full_response = f"❌ Error: {err_msg}"
            
            message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
