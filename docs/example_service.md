# First Example Service

The initial service demonstrates how a VibeServer can forward requests to a language model. It runs locally using the `examples/simple_server.py` script.

## Behavior

1. Accepts HTTP GET requests at `/`.
2. For each request the server sends a short prompt to an LLM that echoes the path and query parameters.
3. The response from the LLM is returned as plain text.

This simple interaction exercises the wiring between the HTTP wrapper and the LLM API.

## Development needs

* Implement the LLM call within `examples/simple_server.py`. The call can use OpenAI's API (an API key is required) and should return the model's text output.
* Add error handling for network failures or invalid responses.

## Testing tooling

* Use Python's `unittest` module to send sample requests and verify the text returned by the server contains the echoed path.
* Include a small test script under `examples/` once the LLM integration is in place.
