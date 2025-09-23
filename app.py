from flask import Flask
import threading
import os
import subprocess
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot running"

@app.route('/health')
def health():
    return "OK"

def run_bot():
    time.sleep(5)
    subprocess.run(["python", "main.py"])

if __name__ == '__main__':
    # Avvia il bot in un thread separato
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Avvia Flask (processo principale)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
