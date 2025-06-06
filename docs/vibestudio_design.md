# VibeStudio Design Overview

VibeStudio is the planned development dashboard for working with a
VibeServer. The goal is to provide a single page interface where a
developer can inspect prompts, view live traffic, run tests, and
interact with the service as a user. This document expands on the
[vibestudio_spec.md](vibestudio_spec.md) by outlining the overall design
and providing a step‑by‑step roadmap to a working implementation.

## Architecture

* **Server** – a lightweight Python or JavaScript backend serves static
  assets and exposes endpoints for log data, prompt updates, and test
  commands. Early versions can reuse the example Flask server from this
  repository.
* **Frontend** – a small single‑page application (HTML/JS) renders the
  panels described in the spec. Communication with the backend happens
  via simple JSON APIs.
* **Integration** – the dashboard communicates with a running
  VibeServer instance. Initial prototypes can mock responses so the UI
  works without an active model.

## Roadmap

1. **Static prototype**
   - Create a basic Flask (or Node) server that serves a static page with
     placeholder panels.
   - Mock data for requests, responses, and tests so the layout can be
     exercised.
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
