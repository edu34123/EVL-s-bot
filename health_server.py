from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'✅ Bot is alive!')
    
    def log_message(self, format, *args):
        pass  # Disabilita log

def start_health_server():
    # Usa la porta da Render o default 10000
    port = int(os.getenv('PORT', 10000))
    print(f"🌐 Avvio server health check sulla porta {port}...")
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"✅ Server health check avviato sulla porta {port}!")
    server.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_health_server, daemon=True)
    server_thread.start()
    
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Server fermato")
