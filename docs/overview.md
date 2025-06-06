# Overview

VibeServing is an approach to building services where a neural model acts as the server itself. The inputs are HTTP requests and the outputs are the responses, with optional side channels for monitoring and control. The idea draws on "vibe coding"—leaning heavily on large language models to generate and adapt code—and "Software 2.0," where the core of the application is a trained model rather than handcrafted logic.

A **VibeServer** is a neural network model (for example, a large language model or a distilled variant) that directly handles web requests. A **VibeClient** is any interface that communicates with the VibeServer, whether programmatically or through a testing dashboard. Together, these form the foundation of an end-to-end AI web.

This repository captures experiments, documentation, and tooling for exploring VibeServing.
