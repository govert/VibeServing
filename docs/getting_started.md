# Getting Started

These instructions describe a minimal local setup. They do not require installing heavy dependencies, but assume you have Python 3 installed.

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key so the example can contact the model:
   ```bash
   export OPENAI_API_KEY="<your-key>"  # Linux/macOS
   $Env:OPENAI_API_KEY="<your-key>"   # PowerShell
   set OPENAI_API_KEY=<your-key>      # cmd.exe
   ```
4. Run the toy VibeServer:
   ```bash
   python examples/simple_server.py
   ```

The example server now forwards each request to an LLM. Run the automated test to verify the behavior without hitting the API:
```bash
python -m unittest examples.test_simple_server
```
See [example_service.md](example_service.md) for more details on the design and tests.

5. Launch VibeStudio in a second terminal:
   ```bash
   python -m vibestudio.studio
   ```
   Then open http://localhost:8500 in your browser. The dashboard lists the
   examples and shows how to run their tests.

VibeStudio currently surfaces example information only; later versions will also
display live traffic and prompts from a running VibeServer.
