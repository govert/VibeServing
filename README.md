# VibeServing

VibeServing explores services implemented directly by neural models. Instead of writing server code in the traditional sense, we prompt a model—the **VibeServer**—to handle HTTP requests and produce responses. A **VibeClient** can be any interface that communicates with the VibeServer, including a browser, scripts, or the planned **VibeStudio** dashboard.

The approach draws inspiration from "vibe coding" (leaning on large language models to generate code and handle changes) and "Software 2.0" (where the core logic is a trained model). Our goal is to build tooling and documentation that make it easy to experiment with model-driven services.

See the [docs](docs/) directory for the project overview, roadmap, policies, and research notes.
The [example service](docs/example_service.md) describes the first minimal VibeServer implementation.
See [docs/getting_started.md](docs/getting_started.md) for setup instructions to run the example service.
