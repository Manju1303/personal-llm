import os
import sys
from pyngrok import ngrok
import subprocess
import time

def run_with_tunnel():
    print("==========================================")
    print("   🚀 Launching Public Mobile Access")
    print("==========================================")
    
    # Check if Ollama is likely running
    print("\n[!] IMPORTANT: Ensure 'ollama serve' is running in another window!")
    print("[!] This script creates a Public URL for your local app.")
    
    # Start Streamlit in the background
    print("\n[1/2] Starting Streamlit App...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Give it a second to start
    time.sleep(3)
    
    # Open Tunnel
    print("[2/2] Opening Public Tunnel (ngrok)...")
    try:
        # Open a HTTP tunnel on the default port 8501
        public_url = ngrok.connect(8501).public_url
        print(f"\n✅ YOUR PUBLIC URL: {public_url}")
        print(f"👉 Copy this link to your MOBILE phone to chat anywhere!")
        print("\n(Press Ctrl+C to stop)")
        
        # Keep alive
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        streamlit_process.terminate()
        ngrok.kill()

if __name__ == "__main__":
    run_with_tunnel()
