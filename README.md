# VibeServing

VibeServing explores services implemented directly by neural models. Instead of writing server code in the traditional sense, we prompt a model—the **VibeServer**—to handle HTTP requests and produce responses. A **VibeClient** can be any interface that communicates with the VibeServer, including a browser, scripts, or the planned **VibeStudio** dashboard.

The approach draws inspiration from "vibe coding" (leaning on large language models to generate code and handle changes) and "Software 2.0" (where the core logic is a trained model). Our goal is to build tooling and documentation that make it easy to experiment with model-driven services.

See the [docs](docs/) directory for the project overview, roadmap, policies, and research notes.
See [docs/getting_started.md](docs/getting_started.md) for setup instructions to run the example service.
The [example service](docs/example_service.md) describes the first minimal VibeServer implementation.
The new [VibeStudio design overview](docs/vibestudio_design.md) explains the dashboard architecture and lists the steps toward a working release. An initial implementation lives under `vibestudio/` and can be started with `python -m vibestudio.studio`. The dashboard launches a small server that proxies HTTP traffic to the LLM using the active prompts. Pressing *Restart Server* in the UI starts a fresh conversation with the model using the edited prompts and issues an initial `GET /` request so the response appears in the Browser panel. The Browser panel itself is an `<iframe>` pointing at the example server, so any HTML body returned with a `Content-Type: text/html` header is rendered just like a normal webpage. The dashboard separates the user-supplied **Service Prompt** from a persistent **Meta Prompt** stored in `vibestudio/meta_prompt.txt`. Both prompts are editable in dedicated panels. Meta instructions and responses are wrapped in triple braces on their own lines. Only HTTP is handled today, but other protocols could be added later.

See [docs/testing_strategy.md](docs/testing_strategy.md) for details on automated tests and recommended manual checks.

For a walk-through of how the frontend, backend, and LLM interact, see [docs/vibestudio_interactions.md](docs/vibestudio_interactions.md).

