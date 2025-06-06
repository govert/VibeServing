"""Placeholder example for a minimal VibeServer.

This script is intentionally lightweight. It outlines how an HTTP request might be
forwarded to a language model and the response returned.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        # TODO: integrate LLM call here
        self.wfile.write(b"Hello from the VibeServer placeholder\n")

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), Handler)
    print("Serving on http://localhost:8000")
    server.serve_forever()
