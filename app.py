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
# Sidebar: Minimalist
# ---------------------------------------------------------
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("### History")
    st.button("📝 Chat 1", use_container_width=True)
    st.button("📝 Chat 2", use_container_width=True)
    
    st.markdown("---")
    
    # Settings (Hidden Details)
    with st.expander("⚙️ Settings"):
        mode = st.radio("Mode", ["Cloud", "Local"], label_visibility="collapsed")
        
        # Config Logic
        api_key = None
        provider_code = "ollama"
        # We define defaults here, but selector is floating below
        
        if "Cloud" in mode:
            cloud_provider = st.selectbox("Cloud", ["Groq", "Google Gemini"])
            if "Gemini" in cloud_provider:
                provider_code = "gemini"
                env_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
                api_key = env_key if env_key else st.text_input("Key", type="password")
            else:
                provider_code = "groq"
                env_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
                api_key = env_key if env_key else st.text_input("Key", type="password")
        else:
            provider_code = "ollama"

    # Files
    with st.expander("📂 Files"):
        uploaded_files = st.file_uploader("Upload", accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files and st.button("Process"):
             st.session_state.processing_trigger = True

# ---------------------------------------------------------
# Floating Model Selector (The "Hack")
# ---------------------------------------------------------
# We place this physically in the layout, but CSS moves it to the bottom bar
st.markdown("""
<style>
    /* Position the container 'fixed' at bottom right */
    div.floating-selector {
        position: fixed;
        bottom: 25px; /* Aligns with Chat Input */
        right: 80px;  /* Left of Send Button */
        z-index: 1000;
        width: 150px;
    }
    
    /* Style the selectbox inside to look like a Pill */
    div.floating-selector div[data-baseweb="select"] > div {
        background-color: #2F2F2F !important;
        border-radius: 20px !important;
        border: 1px solid #424242 !important;
        font-size: 0.8rem !important;
        min-height: 30px !important;
        height: 30px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    div.floating-selector div[data-baseweb="select"] span {
        line-height: 30px !important;
    }
</style>
""", unsafe_allow_html=True)

# Container for the floating widget
with st.container():
    st.markdown('<div class="floating-selector">', unsafe_allow_html=True)
    
    if provider_code == "ollama":
        model_name = st.selectbox(
            "M", 
            ["llama3", "mistral", "gemma", "phi3", "custom"], 
            label_visibility="collapsed",
            key="float_model_select"
        )
        if model_name == "custom":
            # If custom, we might need a separate input? 
            # For UI compactness, let's just default to a popular one if they pick custom or show toast
            st.toast("Edit custom model in Settings")
            model_name = "llama3" 
    elif provider_code == "groq":
        model_name = st.selectbox(
            "M", 
            ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"], 
            label_visibility="collapsed",
            key="float_model_select"
        )
    else:
        st.markdown('<div style="color:gray; font-size:0.8rem; padding:5px;">Gemini Flash</div>', unsafe_allow_html=True)
        model_name = "gemini-1.5-flash"
        
    st.markdown('</div>', unsafe_allow_html=True)

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
