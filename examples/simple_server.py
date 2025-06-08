"""Minimal VibeServer example with an LLM echo.

The handler forwards each HTTP GET request to an LLM which returns
the path and query parameters. The result is streamed back as plain
text. The OpenAI API is used for the language model call if available.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import os

try:
    import openai
except ImportError:  # pragma: no cover - library may not be installed
    openai = None

PREVIOUS_RESPONSE_ID = None

class Handler(BaseHTTPRequestHandler):
    """Basic request handler that proxies to an LLM."""

    def call_llm(self, path: str) -> str:
        """Send a prompt to the LLM asking it to echo ``path``.

        If the ``openai`` package is not installed or no API key is
        configured, a RuntimeError is raised. Any API error results in a
        string describing the failure so the server can respond
        gracefully.
        """

        if openai is None:
            raise RuntimeError("openai package is required for LLM calls")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")

        openai.api_key = api_key
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        prompt = f"Echo the following HTTP path and query exactly:\n{path}"

        try:
            global PREVIOUS_RESPONSE_ID
            if hasattr(openai, "responses"):
                response = openai.responses.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    previous_response_id=PREVIOUS_RESPONSE_ID,
                )
                PREVIOUS_RESPONSE_ID = response.id
                text = response.choices[0].message.content.strip()
            elif hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
                response = openai.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = response.choices[0].message.content.strip()
            else:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = response.choices[0].message["content"].strip()
            return text
        except Exception as exc:  # pragma: no cover - depends on network
            return f"LLM call failed: {exc}"

    def do_GET(self):
        response_text = ""
        try:
            response_text = self.call_llm(self.path)
        except Exception as exc:
            response_text = f"Error: {exc}"

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(response_text.encode("utf-8"))

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), Handler)
    print("Serving on http://localhost:8000")
    server.serve_forever()
