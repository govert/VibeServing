import json
import os
import threading
import subprocess
import logging
from http.server import (
    BaseHTTPRequestHandler,
    SimpleHTTPRequestHandler,
    ThreadingHTTPServer,
    HTTPServer,
)
from urllib.parse import urlparse

try:
    import openai
except ImportError:  # pragma: no cover - optional for tests
    openai = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger(__name__)

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
MODEL_FILE = os.path.join(HERE, "model.txt")
MODEL = _load_file(MODEL_FILE, os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")).strip()
TEMPERATURE = ""
THINKING_TIME = ""
LOGS = []
META_LOGS = []
_SERVER_THREAD = None


def _start_proxy_server():
    """(Re)start the background proxy server."""
    global _SERVER_THREAD
    if _SERVER_THREAD is not None:
        _SERVER_THREAD.stop()
        _SERVER_THREAD.join()
    LOGGER.info("Starting proxy server thread")
    _SERVER_THREAD = _ProxyServerThread()
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


class ProxyHandler(BaseHTTPRequestHandler):
    """HTTP handler that proxies requests to the LLM."""

    def call_llm(self, prompt_text: str) -> str:
        """Send ``prompt_text`` to the LLM and return the result."""
        if openai is None:
            raise RuntimeError("openai package is required for LLM calls")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")

        openai.api_key = api_key
        model = MODEL or "gpt-3.5-turbo"
        LOGGER.info("Calling OpenAI model %s", model)
        LOGGER.debug("Prompt text: %s", prompt_text)
        try:  # pragma: no cover - network dependent
            if hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
                response = openai.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt_text}],
                )
                text = response.choices[0].message.content.strip()
            else:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt_text}],
                )
                text = response.choices[0].message["content"].strip()
            LOGGER.info("OpenAI response received (%d chars)", len(text))
            return text
        except Exception as exc:
            LOGGER.exception("OpenAI call failed")
            return f"LLM call failed: {exc}"

    def _handle_request(self, send_body: bool = True) -> None:
        """Forward the HTTP request to the LLM and relay the reply."""

        global PROMPT, META_PROMPT, LOGS, META_LOGS, MODEL, TEMPERATURE, THINKING_TIME

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        LOGGER.info("Handling %s %s", self.command, self.path)
        LOGGER.info("Current log size: %d entries", len(LOGS))
        request_lines = [f"{self.command} {self.path} HTTP/1.1"]
        for k, v in self.headers.items():
            request_lines.append(f"{k}: {v}")
        request_lines.append("")
        if body:
            request_lines.append(body.decode("utf-8", "replace"))
        request_text = "\n".join(request_lines)

        prompt_body = PROMPT.format(path=self.path, request=request_text)
        prompt_text = f"{META_PROMPT}\n{prompt_body}\n{request_text}"

        # Log outgoing meta and service prompts
        META_LOGS.append({"direction": "out", "text": META_PROMPT})
        LOGS.append({"type": "meta_out", "text": META_PROMPT})

        META_LOGS.append({"direction": "out", "text": prompt_body})
        LOGS.append({"type": "meta_out", "text": prompt_body})
        status = 200
        try:
            response_text = self.call_llm(prompt_text)
        except Exception as exc:  # pragma: no cover - dependent on environment
            LOGGER.error("LLM invocation failed: %s", exc)
            status = 500
            response_text = f"LLM error: {exc}"
        lines = response_text.splitlines()
        # Trim leading blank lines so slightly malformed responses still parse
        while lines and not lines[0].strip():
            lines.pop(0)

        meta_lines = []
        suffix_meta_lines = []
        while (
            lines
            and lines[0].lstrip().startswith("{{{")
            and lines[0].rstrip().endswith("}}}")
        ):
            meta_lines.append(lines.pop(0).strip()[3:-3].strip())
        while lines and not lines[0].strip():
            lines.pop(0)

        headers = {}
        if lines and lines[0].lstrip().startswith("HTTP/"):
            status_line = lines.pop(0).strip()
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

        # Extract trailing meta lines if present
        while (
            lines
            and lines[-1].lstrip().startswith("{{{")
            and lines[-1].rstrip().endswith("}}}")
        ):
            suffix_meta_lines.insert(0, lines.pop().strip()[3:-3].strip())
            while lines and not lines[-1].strip():
                lines.pop()

        body_text = "\n".join(lines)

        for m in meta_lines:
            META_LOGS.append({"direction": "in", "text": m})
            LOGS.append({"type": "meta_in", "text": m})

        LOGS.append({"type": "http", "request": self.path, "status": status, "response": body_text, "error": status >= 400})

        for m in suffix_meta_lines:
            META_LOGS.append({"direction": "in", "text": m})
            LOGS.append({"type": "meta_in", "text": m})

        self.send_response(status)
        LOGGER.info("Responding with status %s", status)
        for k, v in headers.items():
            self.send_header(k, v)
        if "Content-Type" not in headers:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()
        if send_body:
            self.wfile.write(body_text.encode("utf-8"))
        LOGGER.info("Body snippet: %s", body_text[:60].replace("\n", " "))

    # Basic HTTP verbs
    def do_GET(self):  # noqa: D401 - method docs inherited
        self._handle_request()

    def do_POST(self):  # noqa: D401 - method docs inherited
        self._handle_request()

    def do_PUT(self):  # noqa: D401 - method docs inherited
        self._handle_request()

    def do_DELETE(self):  # noqa: D401 - method docs inherited
        self._handle_request()

    def do_PATCH(self):  # noqa: D401 - method docs inherited
        self._handle_request()

    def do_OPTIONS(self):  # noqa: D401 - method docs inherited
        self._handle_request()

    def do_HEAD(self):  # noqa: D401 - method docs inherited
        self._handle_request(send_body=False)


class _ProxyServerThread(threading.Thread):
    def __init__(self, host="localhost", port=8000):
        super().__init__(daemon=True)
        # Use ThreadingHTTPServer so long LLM calls do not block other requests
        self.server = ThreadingHTTPServer((host, port), ProxyHandler)

    def run(self):
        LOGGER.info("Proxy server started on http://%s:%s", *self.server.server_address)
        try:
            self.server.serve_forever()
        except Exception:
            LOGGER.exception("Proxy server crashed")

    def stop(self):
        LOGGER.info("Stopping proxy server")
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
        LOGGER.info("Studio GET %s", parsed.path)
        if parsed.path == "/api/examples":
            self._send_json(gather_examples())
        elif parsed.path == "/api/prompt":
            self._send_json({"prompt": PROMPT})
        elif parsed.path == "/api/meta_prompt":
            self._send_json({"meta_prompt": META_PROMPT})
        elif parsed.path == "/api/settings":
            self._send_json({"model": MODEL, "temperature": TEMPERATURE, "thinking_time": THINKING_TIME})
        elif parsed.path == "/api/logs":
            self._send_json(LOGS)
        elif parsed.path == "/api/meta_logs":
            self._send_json(META_LOGS)
        else:
            super().do_GET()

    def do_POST(self):
        global PROMPT, META_PROMPT, LOGS, META_LOGS
        parsed = urlparse(self.path)
        LOGGER.info("Studio POST %s", parsed.path)
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
        elif parsed.path == "/api/settings":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            global MODEL, TEMPERATURE, THINKING_TIME
            MODEL = data.get("model", MODEL)
            TEMPERATURE = data.get("temperature", TEMPERATURE)
            THINKING_TIME = data.get("thinking_time", THINKING_TIME)
            with open(MODEL_FILE, "w", encoding="utf-8") as fh:
                fh.write(MODEL)
            self._send_json({"status": "ok"})
        elif parsed.path == "/api/restart":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            PROMPT = data.get("prompt", PROMPT)
            META_PROMPT = data.get("meta_prompt", META_PROMPT)
            LOGS = []
            META_LOGS = []
            _start_proxy_server()
            self._send_json({"status": "restarted"})
        elif parsed.path == "/api/meta_chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body or b"{}")
            text = data.get("text", "")
            META_LOGS.append({"direction": "out", "text": text})
            response = ProxyHandler.call_llm(ProxyHandler, text)
            META_LOGS.append({"direction": "in", "text": response})
            self._send_json({"response": response})
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
    _start_proxy_server()
    # ThreadingHTTPServer allows the dashboard to remain responsive while
    # the proxy server handles slower LLM requests.
    server = ThreadingHTTPServer((host, port), StudioHandler)
    print(f"VibeStudio running on http://{host}:{port}")
    LOGGER.info("Server starting on http://%s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping VibeStudio...")
        server.shutdown()
    finally:
        server.server_close()
        LOGGER.info("Server stopped")
        if _SERVER_THREAD is not None:
            _SERVER_THREAD.stop()
            _SERVER_THREAD.join()


if __name__ == "__main__":
    run()

