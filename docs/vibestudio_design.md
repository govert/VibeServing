# VibeStudio Design Overview

VibeStudio is the planned development dashboard for working with a
VibeServer. The goal is to provide a single page interface where a
developer can inspect prompts, view live traffic, run tests, and
interact with the service as a user. This document expands on the
[vibestudio_spec.md](vibestudio_spec.md) by outlining the overall design
and providing a step‑by‑step roadmap to a working implementation.

## Architecture

* **Server** – a lightweight Python or JavaScript backend serves static
  assets and exposes endpoints for log data, prompt updates, meta prompt
  storage, and test commands. Early versions can reuse the example Flask server from this
  repository.
* **Frontend** – a small single‑page application (HTML/JS) renders the
  panels described in the spec. Communication with the backend happens
  via simple JSON APIs.
* **Integration** – the dashboard communicates with a running
  VibeServer instance. Initial prototypes can mock responses so the UI
  works without an active model.

## Interaction flow

Restarting the server from the Prompt panels begins a fresh conversation
with the LLM. The **Service Prompt** and **Meta Prompt** (loaded from
`vibestudio/meta_prompt.txt`) are sent once at the start of that
conversation, each wrapped in triple braces on its own line such as
`{{{ meta prompt }}}`. After this initial handshake the proxy only forwards
HTTP requests or meta chat comments, appending each one to the same
conversation so context accumulates over time. VibeStudio issues an HTTP
`GET /` request immediately after the prompts so the first page loads
automatically. The model's reply is logged and rendered in the Browser
panel. Navigation works like a normal browser—the request text is sent as
a new message and the HTTP response from the model is shown. Meta messages
are captured separately so they appear in a **Meta Chat** panel as well as
in the Traffic log. To mirror the real VibeServer behaviour, the proxy
echoes the meta prompt at the top of each response wrapped in triple
braces (`{{{ meta }}}`). Future versions may forward additional protocols
or out‑of‑band notifications, but today only HTTP is supported.


## Roadmap

1. **Static prototype**
   - Create a small Python server that serves a static page with placeholder
     panels. The implementation lives in `vibestudio/studio.py`.
   - Mock data for requests, responses, and tests so the layout can be
     exercised. The server also exposes `/api/examples` which lists runnable
     examples from the repository.
2. **Live traffic and prompt editing**
   - Connect to the toy VibeServer from `examples/` and display incoming
     requests and outgoing responses in real time.
   - Allow the prompt panel to send updates to the server.
3. **Tester integration**
   - Run the existing unit tests from the dashboard and surface the
     results in the Tester panel.
   - Provide simple controls to trigger test runs on demand.
4. **Polish and deployment**
   - Refine styling and panel layouts.
   - Add minimal authentication if exposing the dashboard remotely.
   - Document setup steps in `getting_started.md`.

This staged approach keeps the initial implementation small while making
it easy to expand VibeStudio alongside the rest of the project.

## Current status

The implementation in this repository now covers stages 1–3. Running
`python -m vibestudio.studio` starts the dashboard along with a small
server that proxies HTTP requests to the LLM using the active prompts.
You can edit prompts, watch traffic, and execute the unit tests from the


Tester panel. A dropdown next to the Service Prompt lets you quickly load
example prompts from the repository. The `examples/simple_server.py` script remains as a minimal
standalone demonstration of the same behaviour.
See [testing_strategy.md](testing_strategy.md) for more on the automated tests
and suggested manual checks.

