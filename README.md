# VibeServing

VibeServing explores services implemented directly by neural models. Instead of writing server code in the traditional sense, we prompt a model—the **VibeServer**—to handle HTTP requests and produce responses. A **VibeClient** can be any interface that communicates with the VibeServer, including a browser, scripts, or the planned **VibeStudio** dashboard.

The approach draws inspiration from "vibe coding" (leaning on large language models to generate code and handle changes) and "Software 2.0" (where the core logic is a trained model). Our goal is to build tooling and documentation that make it easy to experiment with model-driven services.

See the [docs](docs/) directory for the project overview, roadmap, policies, and research notes.
See [docs/getting_started.md](docs/getting_started.md) for setup instructions to run the example service.
The [example service](docs/example_service.md) describes the first minimal VibeServer implementation.
The new [VibeStudio design overview](docs/vibestudio_design.md) explains the dashboard architecture and lists the steps toward a working release. An initial implementation lives under `vibestudio/` and can be started with `python -m vibestudio.studio`. VibeStudio proxies HTTP traffic to a running VibeServer—pressing *Restart Server* in the UI starts a fresh conversation with the LLM using the edited prompt and sends a `GET /` request so the first response appears in the Browser panel. Meta instructions and responses are wrapped in triple braces on their own lines. Only HTTP is handled today, but other protocols could be added later.
