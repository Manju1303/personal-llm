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
# ---------------------------------------------------------
# ChatGPT "Midnight" Theme
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main App - Deep Dark */
    .stApp {
        background-color: #212121; /* Deep Black/Grey */
        color: #ECECF1;
    }
    
    /* Sidebar - Black */
    section[data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2F2F2F;
    }
    
    /* Buttons (New Chat) */
    .stButton button {
        background-color: transparent;
        color: #ECECF1;
        border: 1px solid #424242;
        border-radius: 4px;
        transition: all 0.2s;
        text-align: left;
    }
    .stButton button:hover {
        background-color: #2F2F2F;
    }
    
    /* Input Area - Floats at bottom */
    .stChatInput {
        background-color: #212121;
        padding-bottom: 30px;
    }
    .stChatInput textarea {
        background-color: #2F2F2F; /* Input Box Grey */
        color: white;
        border: 1px solid #424242;
        border-radius: 12px;
    }
    
    /* Messages */
    div[data-testid="stChatMessage"] {
        background-color: transparent;
        border: none;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) {
        /* User */
        background-color: transparent; 
    }
    div[data-testid="stChatMessage"]:nth-child(even) {
        /* Assistant */
        background-color: transparent;
    }

    /* Avatars */
    .stChatMessage .stChatMessageAvatar {
        background-color: #19c37d; /* OpenAI Green */
        color: white;
        width: 30px;
        height: 30px;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Layout (ChatGPT Style)
# ---------------------------------------------------------
# ---------------------------------------------------------
# Sidebar: Minimalist (New Chat, History, Settings)
# ---------------------------------------------------------
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("### History")
    st.caption("Today")
    st.button("📝 Previous Chat 1", use_container_width=True)
    st.button("📝 Previous Chat 2", use_container_width=True)
    
    st.markdown("---")
    
    # Settings (Hidden by default)
    with st.expander("⚙️ Settings"):
        st.write("**System Configuration**")
        mode = st.radio("Mode", ["Cloud", "Local"], label_visibility="collapsed")
        
        # Config Logic (Hidden in Settings)
        api_key = None
        provider_code = "ollama"
        model_name = "llama3"

        if "Cloud" in mode:
            cloud_provider = st.selectbox("Cloud", ["Groq", "Google Gemini"])
            if "Gemini" in cloud_provider:
                provider_code = "gemini"
                env_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if env_key:
                    api_key = env_key
                    st.success("Connected")
                else:
                    api_key = st.text_input("Key", type="password")
            else:
                provider_code = "groq"
                st.info("Using Groq")
                env_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
                if env_key: 
                    api_key = env_key 
                    st.success("Connected")
                else: 
                     api_key = st.text_input("Groq Key", type="password")
        else:
            provider_code = "ollama"
            st.info("Local Mode")

    # Knowledge Base (Moved specific file handling to main area or settings? 
    # User said sidebar only NewChat/Settings/History. 
    # But we need file upload. Let's put it in Settings for minimal look or a small icon)
    with st.expander("📂 Files"):
        uploaded_files = st.file_uploader("Upload", accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            if st.button("Process", use_container_width=True):
                 st.session_state.processing_trigger = True

# ---------------------------------------------------------
# Main Area: Top Bar (Model Selector)
# ---------------------------------------------------------
# ChatGPT puts model selector at top left.
col_model, col_spacer, col_mic = st.columns([2, 4, 1])

with col_model:
    # Model Selector (Visual like ChatGPT Header)
    if provider_code == "ollama":
        model_name = st.selectbox(
            "Model", 
            ["llama3", "mistral", "gemma", "phi3", "Custom..."], 
            label_visibility="collapsed"
        )
        if model_name == "Custom...":
            model_name = st.text_input("Model Name", value="gemma2:latest")
    elif provider_code == "groq":
        model_name = st.selectbox(
            "Model", 
            ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"], 
            label_visibility="collapsed"
        )
    else:
        st.markdown(f"**🤖 Gemini 1.5 Flash**")

with col_mic:
    # Mic Dummy Button (Visual)
    st.button("🎙️", type="secondary")

st.divider()

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
