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

    # Files (Removed from Sidebar to use Floating +)
    # kept empty or minimal
    pass

    # -------------------------------------------------------------------------
    # Floating Widgets (Defined in SIDEBAR but CSS moves them to Main Screen)
    # -------------------------------------------------------------------------
    # We put these at the very end of sidebar to target them easily with CSS
    
    st.markdown("---") # Separator to ensure distinct container
    
    # 1. Model Selector (Will be floated Right)
    if provider_code == "ollama":
        st.selectbox("M", ["llama3", "mistral", "gemma", "phi3", "custom"], label_visibility="collapsed", key="float_model")
    elif provider_code == "groq":
        st.selectbox("M", ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"], label_visibility="collapsed", key="float_model")
    else:
        st.caption("Gemini Flash") # Placeholder for Gemini

    # 2. Upload Button (Will be floated Left)
    with st.popover("➕", help="Add Files"):
        st.markdown("### 📂 Upload")
        uploaded_files_sidebar = st.file_uploader("Drop files", accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files_sidebar:
            st.session_state.uploaded_files = uploaded_files_sidebar # Store in session state
            if st.button("Process Files", type="primary"):
                st.session_state.processing_trigger = True
                st.toast("Processing...")
        else:
            st.session_state.uploaded_files = [] # Clear if no files selected

# ---------------------------------------------------------
# CSS: Teleport Sidebar Widgets to Main Screen Bottom
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 
       Targeting the LAST elements in the sidebar.
       NOTE: This relies on the precise order of elements in the sidebar above.
       We target the last two 'div.stElementContainer' in the sidebar.
    */
    
    /* Upload Button (The very last item) -> Bottom Left */
    section[data-testid="stSidebar"] > div > div:last-child {
        position: fixed !important;
        bottom: 25px !important;
        left: 20px !important;
        width: auto !important;
        z-index: 99999 !important;
    }
    
    /* Model Selector (The second to last item) -> Bottom Right */
    section[data-testid="stSidebar"] > div > div:nth-last-child(2) {
        position: fixed !important;
        bottom: 25px !important;
        right: 80px !important;
        width: 160px !important;
        z-index: 99999 !important;
    }
    
    /* Styling for the selector to look like a pill */
    section[data-testid="stSidebar"] > div > div:nth-last-child(2) div[data-baseweb="select"] > div {
        background-color: #2F2F2F !important;
        border-radius: 20px !important;
        border: 1px solid #444 !important;
        height: 35px !important;
        min-height: 35px !important;
    }

    /* Styling for the Plus Button */
    section[data-testid="stSidebar"] > div > div:last-child button {
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        background-color: #2F2F2F !important;
        border: 1px solid #444 !important;
        color: #ddd !important;
    }
</style>
""", unsafe_allow_html=True)

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

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# Init Engine Logic (Graceful)
if provider_code == "groq" and not api_key:
    # Don't crash, just wait
    pass 
elif provider_code == "gemini" and not api_key:
    pass

# File Processing
if st.session_state.processing_trigger and st.session_state.uploaded_files:
    st.session_state.processing_trigger = False # Reset
    if provider_code == "gemini" and not api_key:
        st.error("Please provide an API Key.")
    else:
        with st.status("Analyzing documents...", expanded=True) as status:
            try:
                # Init Engine
                st.session_state.engine = LLMEngine(
                    provider=provider_code,
                    model_name=st.session_state.get("float_model", "llama3"), # Get from float widget
                    api_key=api_key
                )
                
                documents = FileHandler.process_uploaded_files(st.session_state.uploaded_files)
                st.session_state.engine.create_index(documents)
                st.session_state.chat_engine = st.session_state.engine.get_chat_engine()
                
                status.update(label="Context Ready", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="Error", state="error")
                st.error(str(e))

# Welcome Message if empty
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; margin-top: 10vh;">
        <h1 style="color: #ECECF1; font-size: 2.5rem;">Personal AI</h1>
        <p style="color: #888;">Secure • Private • Smart</p>
    </div>
    """, unsafe_allow_html=True)

# Chat Loop
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Message..."):
    # Guard Checks
    if provider_code == "groq" and not api_key:
        st.warning("⚠️ Please enter Groq API Key in Settings (Sidebar).")
    elif provider_code == "gemini" and not api_key:
        st.warning("⚠️ Please enter Gemini API Key in Settings (Sidebar).")
    else:
        # Proceed
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
                    st.session_state.engine = LLMEngine(
                        provider=provider_code, 
                        model_name=st.session_state.get("float_model", "llama3"), # Get from float widget
                        api_key=api_key
                    )
                
                # Ensure Chat Engine
                if not st.session_state.chat_engine:
                     st.session_state.chat_engine = st.session_state.engine.get_chat_engine()

                # Generate
                response_iter = st.session_state.chat_engine.stream_chat(prompt)

                for part in response_iter.response_gen:
                    full_response += part
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
