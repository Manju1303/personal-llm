import streamlit as st
from llm_engine import LLMEngine
from file_handler import FileHandler
import os

st.set_page_config(page_title="Personal AI", page_icon="🤖", layout="wide")

# ---------------------------------------------------------
# ChatGPT Style CSS
# ---------------------------------------------------------
# ---------------------------------------------------------
# ChatGPT Style CSS with Animations
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Source Sans Pro', sans-serif;
    }

    /* ANIMATIONS */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatMessage {
        animation: slideIn 0.3s ease-out forwards;
    }

    /* Main Background */
    .stApp {
        background-color: #343541; /* ChatGPT Dark */
        color: #d1d5db;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #202123;
        border-right: 1px solid #4d4d4f;
    }
    
    /* Chat Bubbles */
    div[data-testid="stChatMessage"] {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        transition: background-color 0.3s;
    }
    
    /* User Bubble - Dark Transparent */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(52, 53, 65, 0.9);
        border: 1px solid #565869;
    }
    
    /* Assistant Bubble - SLightly Lighter */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #444654;
        border: 1px solid #444654;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Avatars */
    .stChatMessage .stChatMessageAvatar {
        background: linear-gradient(135deg, #10a37f, #0d8c6d); /* OpenAI Green Gradient */
        color: white;
        border-radius: 4px;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) .stChatMessageAvatar {
        background: linear-gradient(135deg, #8e2de2, #4a00e0); /* User Purple Gradient */
    }

    /* Headers & Text */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #40414f !important;
        color: white !important;
        border: 1px solid #565869 !important;
        border-radius: 6px;
    }
    
    /* Custom Buttons */
    .stButton button {
        background-color: #40414f;
        color: white;
        border-radius: 6px;
        border: 1px solid #565869;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #202123;
        border-color: #10a37f;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar & Config
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🤖 **Assistant**")
    
    # Mode Toggle
    mode = st.radio("Access Mode", ["☁️ Cloud (Gemini)", "🏠 Local (Ollama)"], label_visibility="collapsed")
    
    api_key = None
    provider_code = "ollama"
    model_name = "llama3"

    # -------------------------------------------
    # Cloud (Gemini)
    # -------------------------------------------
    if "Cloud" in mode:
        # Try to load from Secrets/Env silently
        env_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if env_key:
            api_key = env_key
            st.success("✨ Online: Gemini 1.5 Flash")
            provider_code = "gemini"
        else:
            api_key = st.text_input("💎 API Key", type="password", placeholder="Paste Google Key here...")
            if not api_key:
                 st.warning("Key required for Cloud.")
            else:
                 provider_code = "gemini"
            
    else: # Local
        st.info("🏠 Offline Mode: Private")
        provider_code = "ollama"
        # Expanded Free Model List
        with st.expander("🛠️ Model Settings", expanded=True):
            model_name = st.selectbox(
                "Select Model", 
                [
                    "llama3", "mistral", "gemma", "phi3",  # Top Tier
                    "neural-chat", "starling-lm", "codellama", # Specialty
                    "llama2", "vicuna", "orca-mini" # Legacy/Lightweight
                ],
                help="Make sure you have run 'ollama pull <model>' for these to work!"
            )

    st.divider()
    
    # File Uploader (Cleaner)
    with st.expander("📚 Knowledge Base", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload files", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt', 'csv'],
            label_visibility="collapsed"
        )
        if uploaded_files:
            if st.button("Update Context", type="primary", use_container_width=True):
                 st.session_state.processing_trigger = True
    
    # Bottom Actions
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# Main Logic
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "engine" not in st.session_state:
    st.session_state.engine = None
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None

if "processing_trigger" not in st.session_state:
    st.session_state.processing_trigger = False

# File Processing
if st.session_state.processing_trigger and uploaded_files:
    st.session_state.processing_trigger = False # Reset
    if provider_code == "gemini" and not api_key:
        st.error("Please provide an API Key.")
    else:
        with st.status("Analyzing documents...", expanded=True) as status:
            try:
                # Init Engine
                st.session_state.engine = LLMEngine(
                    provider=provider_code,
                    model_name=model_name,
                    api_key=api_key
                )
                
                documents = FileHandler.process_uploaded_files(uploaded_files)
                st.session_state.engine.create_index(documents)
                st.session_state.chat_engine = st.session_state.engine.get_chat_engine()
                
                status.update(label="Context Ready", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="Error", state="error")
                st.error(str(e))

# Welcome Message if empty
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h1 style="color: #ECECF1;">Personal AI</h1>
        <p style="color: #C5C5D2;">Secure, Private, and Multilingual.</p>
    </div>
    """, unsafe_allow_html=True)

# Chat Loop
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Send a message..."):
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
                     full_response = "Please enter your Google API Key in the sidebar."
                     message_placeholder.markdown(full_response)
                     raise ValueError("Missing Key")
                
                # Init basic engine
                st.session_state.engine = LLMEngine(
                    provider=provider_code, 
                    model_name=model_name, 
                    api_key=api_key
                )
            
            # Ensure Chat Engine exists
            if not st.session_state.chat_engine:
                 st.session_state.chat_engine = st.session_state.engine.get_chat_engine()

            # Generate with History!
            response_iter = st.session_state.chat_engine.stream_chat(prompt)

            for part in response_iter.response_gen:
                full_response += part
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            if not full_response:
                full_response = f"Error: {str(e)}"
                message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
