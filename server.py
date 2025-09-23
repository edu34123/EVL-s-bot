from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # Disabilita i log

def start_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    print("✅ Server health check avviato sulla porta 10000")
    server.serve_forever()

# Avvia il server immediatamente
if __name__ == "__main__":
    start_server()
