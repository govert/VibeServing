import json
import os
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

try:
    import openai
except ImportError:  # pragma: no cover - optional for tests
    openai = None

HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.dirname(HERE)

PROMPT_FILE = os.path.join(HERE, "prompt.txt")
META_PROMPT_FILE = os.path.join(HERE, "meta_prompt.txt")

DEFAULT_PROMPT = "Echo the following HTTP path and query exactly:\n{path}"

def _load_file(path: str, default: str) -> str:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(default)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

PROMPT = _load_file(PROMPT_FILE, DEFAULT_PROMPT)
META_PROMPT = _load_file(
    META_PROMPT_FILE,
    (
        "You are a VibeServer controller. Each incoming message contains an HTTP "
        "request. Combine this meta prompt with the service prompt to determine "
        "the correct response. Always return a full HTTP reply: status line, "
        "headers, a blank line, then the body. Begin the reply with this meta "
        "prompt wrapped in triple braces on its own line."
    ),
)
LOGS = []
META_LOGS = []
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
            prompt_file = os.path.join(examples_dir, f"{name}_prompt.txt")
            test_cmd = None
            prompt = None
            if os.path.exists(test_file):
                test_mod = os.path.splitext(os.path.basename(test_file))[0]
                test_cmd = f"python -m unittest examples.{test_mod}"
            if os.path.exists(prompt_file):
                with open(prompt_file, "r", encoding="utf-8") as fh:
                    prompt = fh.read()
            items.append({"name": name, "run": run_cmd, "test": test_cmd, "prompt": prompt})
    return items


class ExampleHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler used by the dashboard."""

    def call_llm(self, prompt_text: str) -> str:
        """Send ``prompt_text`` to the LLM and return the result."""
        if openai is None:
            raise RuntimeError("openai package is required for LLM calls")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")

        openai.api_key = api_key
        try:  # pragma: no cover - network dependent
            if hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt_text}],
                )
                return response.choices[0].message.content.strip()
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt_text}],
                )
                return response.choices[0].message["content"].strip()
        except Exception as exc:
            return f"LLM call failed: {exc}"

    def do_GET(self):
        global PROMPT, META_PROMPT, LOGS, META_LOGS
        prompt_text = f"{META_PROMPT}\n{PROMPT.format(path=self.path)}"
        META_LOGS.append({"direction": "out", "text": META_PROMPT})
        status = 200
        try:
            response_text = self.call_llm(prompt_text)
        except Exception as exc:  # pragma: no cover - dependent on environment
            status = 500
            response_text = f"LLM error: {exc}"
        lines = response_text.splitlines()
        meta_lines = []
        while lines and lines[0].startswith("{{{") and lines[0].endswith("}}}"):
            meta_lines.append(lines.pop(0)[3:-3].strip())
        for m in meta_lines:
            META_LOGS.append({"direction": "in", "text": m})

        headers = {}
        if lines and lines[0].startswith("HTTP/"):
            status_line = lines.pop(0)
            parts = status_line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status = int(parts[1])
            while lines:
                line = lines.pop(0)
                if not line.strip():
                    break
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip()] = v.strip()

        body_text = "\n".join(lines)
        LOGS.append({"request": self.path, "status": status, "response": body_text, "error": status >= 400})

        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        if "Content-Type" not in headers:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body_text.encode("utf-8"))


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
        elif parsed.path == "/api/meta_prompt":
            self._send_json({"meta_prompt": META_PROMPT})
        elif parsed.path == "/api/logs":
            self._send_json(LOGS)
        elif parsed.path == "/api/meta_logs":
            self._send_json(META_LOGS)
        else:
            super().do_GET()

    def do_POST(self):
        global PROMPT, META_PROMPT, LOGS, META_LOGS
        parsed = urlparse(self.path)
        if parsed.path == "/api/prompt":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            PROMPT = data.get("prompt", PROMPT)
            with open(PROMPT_FILE, "w", encoding="utf-8") as fh:
                fh.write(PROMPT)
            self._send_json({"status": "ok"})
        elif parsed.path == "/api/meta_prompt":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            META_PROMPT = data.get("meta_prompt", META_PROMPT)
            with open(META_PROMPT_FILE, "w", encoding="utf-8") as fh:
                fh.write(META_PROMPT)
            self._send_json({"status": "ok"})
        elif parsed.path == "/api/restart":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            PROMPT = data.get("prompt", PROMPT)
            META_PROMPT = data.get("meta_prompt", META_PROMPT)
            LOGS = []
            META_LOGS = []
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

