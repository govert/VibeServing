# VibeStudio Message Flow

This document expands on the existing design notes by walking through how a developer interacts with a VibeServer via VibeStudio. It combines a text-based UI mockup with message trace diagrams showing the flow between the browser, the local VibeStudio backend, and the remote LLM acting as the VibeServer.

## Components

* **VibeStudio Frontend** – Runs in the developer's browser and displays the dashboard panels.
* **VibeStudio Backend** – A lightweight Python server (`vibestudio/studio.py`) that serves the frontend assets, stores prompts, proxies HTTP traffic, and exposes helper APIs.
* **VibeServer (LLM)** – The language model that interprets HTTP requests and returns HTTP responses. The current implementation uses the OpenAI API.

## Initial creation

1. The developer starts the dashboard with `python -m vibestudio.studio`.
2. The backend loads `prompt.txt` and `meta_prompt.txt`, then launches an example HTTP server on port 8000.
3. The browser loads `http://localhost:8500/` and renders the panels.
4. When *Restart Server* is pressed, the backend combines the Service and Meta prompts and sends an initial `GET /` request to the LLM. The response populates the Browser panel.

Sequence diagram for the restart flow:

```
Browser -> Backend: POST /api/restart (prompts)
Backend -> LLM: meta + service prompt + "GET /" request
LLM -> Backend: HTTP response
Backend -> Browser: update traffic log
Browser -> Browser: iframe loads http://localhost:8000/
```

## Subsequent interactions

After the server is restarted, the Browser panel acts as a regular client. Each navigation or form submission is proxied through the backend to the LLM. Traffic logs show the requests and responses in real time.

```
Browser -> Backend: HTTP request via iframe
Backend -> LLM: same request prefixed with meta prompt
LLM -> Backend: HTTP response
Backend -> Browser: relay response and append log entry
```

Because the meta prompt instructs the model to act as a VibeServer, the LLM returns full HTTP replies beginning with the meta block wrapped in triple braces:

```
{{{ meta }}}
HTTP/1.1 200 OK
Content-Type: text/html

<html>...</html>
```

## Logging and out‑of‑band messages

The backend keeps an in‑memory list `LOGS` containing dictionaries with `request` and `response` fields. The Traffic panel polls `/api/logs` every few seconds to display these entries. Any additional metadata returned by the LLM could be surfaced in a similar way—for example, diagnostics wrapped in triple braces.

Future versions may allow the LLM to send notifications separate from the HTTP response stream. These would travel through the backend before reaching the UI.

## UI mockup

A simplified text representation of the dashboard:

```
+---------------- Service Prompt ----------------+
| [textarea]                                      |
| [Save]                                          |
+------------------------------------------------+

+----------------- Meta Prompt ------------------+
| [textarea]                                      |
| [Save] [Restart Server]                         |
+------------------------------------------------+

+------------------ Traffic ---------------------+
| GET / -> {{{ meta }}} HTTP/1.1 200 OK ...       |
| /form -> {{{ meta }}} HTTP/1.1 200 OK ...       |
+------------------------------------------------+

+------------------ Browser ---------------------+
| [ iframe showing http://localhost:8000/ ]       |
+------------------------------------------------+

+------------------- Tester ---------------------+
| [Run Tests]                                     |
| test output                                     |
+------------------------------------------------+
```

## Summary

VibeStudio orchestrates a short feedback loop between prompt editing, server restart, and live interaction. The backend threads together the service prompt, meta prompt, and user HTTP requests before calling the LLM. Responses are logged and displayed so the developer can iterate quickly on the behaviour of the VibeServer.

