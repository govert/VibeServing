# VibeStudio / Mission Control Specification

VibeStudio provides a unified interface for interacting with a VibeServer during development.

## Key features

1. **Service Prompt panel** – displays the request-handling prompt and allows edits.
2. **Meta Prompt panel** – shows persistent instructions stored in `vibestudio/meta_prompt.txt`.
3. **Traffic panel** – shows incoming requests and outgoing responses in real time.
4. **Browser panel** – embedded view to interact with the VibeServer as a user would.
5. **Tester panel** – run automated tests against the VibeServer and display results.

## Implementation notes

* VibeStudio should run locally with minimal setup—ideally a simple Python or JavaScript server.
* Panels can be arranged using a lightweight web framework (for example, a single-page app served by Flask or Node/Express).
* Initial versions may rely on mock data; integration with the actual VibeServer and VibeTester will come later.
* Restarting the server with a new prompt should create a fresh conversation
  with the LLM. VibeStudio injects extra context instructing the model to act
  as a VibeServer. After restart the dashboard issues an HTTP `GET /` request
  and logs both the request and the model's HTTP response. The response body is
  rendered in the Browser panel and further interactions continue through the
  same proxy channel. The simple example server bundled with the dashboard also
  echoes the meta prompt at the top of each response to mimic this behaviour.
* These hidden instructions are delimited with triple braces on their own
  lines (e.g. `{{{ meta }}}`) so the server can return meta responses in the
  same form.
* Only HTTP traffic is currently proxied, though future versions may support
  additional protocols such as WebSocket.
