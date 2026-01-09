# 🤖 Personal Multilingual LLM

A private, custom AI assistant that works **Offline** (Local PC) and **Online** (Cloud/Mobile).
Designed to be completely free, secure, and accessible anywhere.

## ✨ Features
*   **Hybrid Core**: Switch between **Local (Ollama)** for privacy and **Cloud (Gemini)** for 24/7 access.
*   **Multilingual**: Supports queries in any language (English, Hindi, Kannada, Spanish, etc.).
*   **Offline Mode**: Run completely offline on your PC without internet.
*   **File Analysis**: Upload PDF, DOCX, TXT, and CSV files to chat with them (RAG).
*   **Mobile Ready**: Access via Streamlit Cloud or Local Wi-Fi.

## 🚀 How to Run

### Option 1: Local PC (Privacy Focused)
1.  Install [Ollama](https://ollama.com/) and run `ollama pull llama3`.
2.  Double-click `install_and_run.bat`.
3.  Choose "1" for Local Wi-Fi access.

### Option 2: Cloud / Mobile (24/7 Access)
*Recommended for use when PC is off.*
1.  Get a free API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Deploy this repository to [Streamlit Cloud](https://share.streamlit.io/).
3.  Enter your API Key in the app sidebar.

## 🛠️ Tech Stack
*   **App**: Streamlit
*   **AI Engine**: LlamaIndex
*   **Local Model**: Ollama (Llama 3, Mistral)
*   **Cloud Model**: Google Gemini 1.5 Flash (Free Tier)
