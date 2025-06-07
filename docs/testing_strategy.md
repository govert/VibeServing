# Testing Strategy

This document explains how automated and manual tests ensure VibeStudio and the example server behave predictably.

## Unit tests

- **Request handling and logging** – `vibestudio/tests/test_example_handler.py` spins up the example HTTP server in a background thread. It issues a request and asserts that the response contains the expected text and that the request/response pair was recorded in `studio.LOGS`.
- **Example server** – `examples/test_simple_server.py` exercises the standalone server in `examples/simple_server.py`.
- Both test suites patch `call_llm` so no real network calls occur. This ensures deterministic results and allows the tests to run without API keys.

Run all tests from the repository root:

```bash
python -m pytest
```

## Tester panel

The dashboard provides a Tester panel that triggers the same CLI tests. When the *Run Tests* button is pressed, the UI sends a request to `/api/run_tests`. The server handler defined in `vibestudio/studio.py` executes `python -m unittest examples.test_simple_server` in a subprocess and returns the output.

## Manual checks

While unit tests cover basic behaviour, confirm the following manually after significant changes:

- Editing the Service or Meta prompts causes the server to restart and new requests appear in the Traffic panel.
- Request and response logs update live in the dashboard.
- The Tester panel reports pass/fail status for the CLI tests.
- Browser panel interactions match the responses shown in the logs.
