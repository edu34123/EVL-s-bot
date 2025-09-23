import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, *args):
        pass

port = int(os.environ.get('PORT', 10000))
print(f"Starting server on port {port}")
HTTPServer(('0.0.0.0', port), Handler).serve_forever()
