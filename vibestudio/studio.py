import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.dirname(HERE)


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


class StudioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(HERE, "static"), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/examples":
            data = json.dumps(gather_examples()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()


def run(host="localhost", port=8500):
    server = HTTPServer((host, port), StudioHandler)
    print(f"VibeStudio running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
