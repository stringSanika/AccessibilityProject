"""
serve.py — Local dev server with cache disabled.
Every response gets Cache-Control: no-cache so the browser
always loads the latest file from disk.

Usage:  python serve.py        (default port 8000)
        python serve.py 8080   (custom port)
"""
import http.server
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma",        "no-cache")
        self.send_header("Expires",       "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass   # suppress request logs for cleaner output

print(f"[SERVER] Serving on http://localhost:{PORT}  (cache disabled)")
print(f"[SERVER] Press Ctrl+C to stop")

with http.server.HTTPServer(("", PORT), NoCacheHandler) as httpd:
    httpd.serve_forever()