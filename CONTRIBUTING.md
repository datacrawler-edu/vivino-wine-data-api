# Contributing

Contributions should improve the integration examples, documentation, or data-format clarity. Do not add Actor runtime source, credentials, proxy settings, private endpoints, local paths, logs, or unsupported product claims.

Before opening a pull request:

- Keep Actor inputs and output fields aligned with the current public schemas.
- Keep sample wine, merchant, and rating data fictional or sanitized.
- Run the local Python API-fixture tests with the pinned client: install requirements-dev.txt and run python -m pytest -q tests/test_public_examples.py.
- Check the JavaScript example with node --check examples/javascript/request.mjs.
- Review git status and the complete diff; never commit an API token.
