# First Example Service

The initial service demonstrates how a VibeServer can forward requests to a language model. It runs locally using the `examples/simple_server.py` script.

## Behavior

1. Accepts HTTP GET requests at `/`.
2. For each request the server sends a short prompt to an LLM that echoes the path and query parameters.
3. The response from the LLM is returned as plain text.

This simple interaction exercises the wiring between the HTTP wrapper and the LLM API.

## Development notes
The `simple_server.py` example includes a `call_llm` helper that relies on the OpenAI package. Install dependencies from `requirements.txt` and set the `OPENAI_API_KEY` variable as shown in [getting_started.md](getting_started.md) before starting the server. Errors from the API are returned to the client so failures are visible during development.
## Testing tooling

* Python's `unittest` module drives a small integration test in `examples/test_simple_server.py`.
* The test patches out the actual LLM call so it runs quickly without network access.
