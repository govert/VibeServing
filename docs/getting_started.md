# Getting Started

These instructions describe a minimal local setup. They do not require installing heavy dependencies, but assume you have Python 3 installed.

1. Clone this repository.
2. Install dependencies (placeholder):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the toy VibeServer:
   ```bash
   python examples/simple_server.py
   ```

The example server simply echoes requests using an LLM call (not yet implemented). See [example_service.md](example_service.md) for details on the planned behavior and test tooling.

VibeStudio will provide a graphical view of prompts and traffic once the server is integrated.
