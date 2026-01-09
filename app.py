import streamlit as st
from llm_engine import LLMEngine
from file_handler import FileHandler
import os

st.set_page_config(page_title="Personal AI", page_icon="🤖", layout="wide")

# ---------------------------------------------------------
# ChatGPT Style CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Global Reset & Font */
    @import url('https://fonts.googleapis.com/css2?family=Söhne&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Main Background - Dark Grey */
    .stApp {
        background-color: #343541;
        color: #ECECF1;
    }
    
    /* Sidebar Background - Darker Grey */
    section[data-testid="stSidebar"] {
        background-color: #202123;
    }
    
    /* Input Container */
    .stChatInput {
        background-color: #343541;
        padding-bottom: 2rem;
    }
    
    /* User Message Bubble */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #343541; /* Matches bg */
        border: none;
    }
    
    /* Assistant Message Bubble - Slightly Lighter */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #444654;
        border: none;
        width: 100%;
        padding: 1.5rem;
    }

    /* Message Content */
    .stMarkdown {
        color: #ECECF1;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Avatar Styling */
    .stChatMessage .stChatMessageAvatar {
        background-color: #19c37d; /* OpenAI Green */
        color: white;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) .stChatMessageAvatar {
        background-color: #5436DA; /* User Purple */
    }

    /* Headers */
    h1, h2, h3 {
        color: #ECECF1 !important;
        font-weight: 600;
    }
    
    /* Buttons in Sidebar */
    .stButton button {
        background-color: #343541;
        color: #ECECF1;
        border: 1px solid #565869;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #2A2B32;
        border-color: #ECECF1;
    }
    
    /* Primary Action Button */
    button[kind="primary"] {
        background-color: #19c37d !important;
        border: none !important;
        color: white !important;
    }
    button[kind="primary"]:hover {
        background-color: #1a885d !important;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar & Config
# ---------------------------------------------------------
with st.sidebar:
    st.title("🤖 Chat")
    
    # Mode Toggle (Subtle)
    mode = st.radio("System Mode", ["☁️ Cloud", "🏠 Local"], label_visibility="collapsed")
    
    api_key = None
    provider_code = "ollama"
    model_name = "llama3"

    # -------------------------------------------
    # Cloud Config (Auto-Hide Key)
    # -------------------------------------------
    if "Cloud" in mode:
        # Try to load from Secrets/Env silently
        env_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if env_key:
            # Key found in backend - Hide input for "ChatGPT" feel
            api_key = env_key
            st.success("🟢 Connected to Cloud")
            provider_code = "gemini"
        else:
            # Key missing - Show Password Field
            api_key = st.text_input("Enter API Key", type="password", placeholder="sk-...")
            if not api_key:
                 st.warning("Key required for Cloud.")
            else:
                 provider_code = "gemini"
            
    else: # Local
        st.info("🏠 Local Mode Active")
        provider_code = "ollama"
        # Hide model selector in an expander to keep sidebar clean
        with st.expander("Model Settings"):
            model_name = st.selectbox("Model", ["llama3", "mistral", "phi3", "gemma"])

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
