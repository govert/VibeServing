# Getting Started

These instructions describe a minimal local setup. They do not require installing heavy dependencies, but assume you have Python 3 installed.

1. Clone this repository.
2. Install dependencies (placeholder):
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key so the example can contact the model:
   ```bash
   export OPENAI_API_KEY="<your-key>"
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

VibeStudio will provide a graphical view of prompts and traffic once the server is integrated.
