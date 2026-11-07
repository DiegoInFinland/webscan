#!/bin/sh
# Run the webscan MCP server in a Docker container, mounting the project root to /app.
# Since the volume mount hides the image's .venv, we run uv sync at startup.
# It should be used for development purposes only.
docker run --rm -it \
  --network host \
  -v $(pwd):/app \
  --entrypoint sh \
  webscan \
  -c "uv sync --no-dev && exec /app/.venv/bin/python src/server.py"
