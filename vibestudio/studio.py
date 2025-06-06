import json
import os
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.dirname(HERE)

PROMPT = "Echo the following HTTP path and query exactly:\n{path}"
LOGS = []
_SERVER_THREAD = None


def _start_example_server():
    """(Re)start the background example server."""
    global _SERVER_THREAD
    if _SERVER_THREAD is not None:
        _SERVER_THREAD.stop()
        _SERVER_THREAD.join()
    _SERVER_THREAD = _ExampleServerThread()
    _SERVER_THREAD.start()


def gather_examples():
    """Return a list of example run/test commands from the repo."""
    examples_dir = os.path.join(REPO_ROOT, "examples")
    items = []
    for filename in os.listdir(examples_dir):
        if filename.endswith(".py") and not filename.startswith("test_"):
            name = os.path.splitext(filename)[0]
            run_cmd = f"python examples/{filename}"
            test_file = os.path.join(examples_dir, f"test_{filename}")
            test_cmd = None
            if os.path.exists(test_file):
                test_mod = os.path.splitext(os.path.basename(test_file))[0]
                test_cmd = f"python -m unittest examples.{test_mod}"
            items.append({"name": name, "run": run_cmd, "test": test_cmd})
    return items


class ExampleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global PROMPT
        text = PROMPT.format(path=self.path)
        LOGS.append({"request": self.path, "response": text})
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))


class _ExampleServerThread(threading.Thread):
    def __init__(self, host="localhost", port=8000):
        super().__init__(daemon=True)
        self.server = HTTPServer((host, port), ExampleHandler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class StudioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(HERE, "static"), **kwargs)

    def _send_json(self, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/examples":
            self._send_json(gather_examples())
        elif parsed.path == "/api/prompt":
            self._send_json({"prompt": PROMPT})
        elif parsed.path == "/api/logs":
            self._send_json(LOGS)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/prompt":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            global PROMPT
            PROMPT = data.get("prompt", PROMPT)
            self._send_json({"status": "ok"})
        elif parsed.path == "/api/restart":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            global PROMPT, LOGS
            PROMPT = data.get("prompt", PROMPT)
            LOGS = []
            _start_example_server()
            self._send_json({"status": "restarted"})
        elif parsed.path == "/api/run_tests":
            result = subprocess.run([
                "python",
                "-m",
                "unittest",
                "examples.test_simple_server",
            ], capture_output=True, text=True)
            self._send_json({"output": result.stdout + result.stderr, "returncode": result.returncode})
        else:
            self.send_response(404)
            self.end_headers()


def run(host="localhost", port=8500):
    _start_example_server()
    server = HTTPServer((host, port), StudioHandler)
    print(f"VibeStudio running on http://{host}:{port}")
    try:
        server.serve_forever()
    finally:
        if _SERVER_THREAD is not None:
            _SERVER_THREAD.stop()


if __name__ == "__main__":
    run()

