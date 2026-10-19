# Nmap MCP Server

> **Disclaimer:** This is a personal project, and still a work in progress, and is not intended for production in real environments. Use at your own risk!

Dockerized Kali Linux container that exposes Nmap, curl, and WhatWeb as very small and lightweight [MCP (Model Context Protocol)](https://modelcontextprotocol.io) tools for AI agents.

## Architecture

```
AI Client (Claude, etc.)
    │  MCP protocol (stdio)
    ▼
Docker Container (kalilinux/kali-rolling)
    │
    ├── uv             (Python package manager)
    ├── src/server.py  (FastMCP server)
    │   ├── @mcp.tool()  →  local_ip()
    │   ├── @mcp.tool()  →  nmap_scan(target, flags, ports)
    │   ├── @mcp.tool()  →  ping_scan(target)
    │   ├── @mcp.tool()  →  ping6_scan(target)
    │   ├── @mcp.tool()  →  curl_request(flags, url)
    │   └── @mcp.tool()  →  whatweb_scan(flags, url)
    ├── nmap
    ├── curl
    └── whatweb
```

## Quick Start

> **Branch note:** `curl_request` and `whatweb_scan` are available on `develop` only. Check out `develop` before building the image to use them; `main` currently provides only the Nmap tools.

Build the new image, then edit your AI configuration file in order to use it with your agent. See below for configuration example.

### Prerequisites

- Docker

### Build the Docker image

```bash
# Build the image (prod stage is default)
docker build -t nmap-mcp-server .

# Run (stdio-based MCP server)
docker run --rm --network host -i nmap-mcp-server

# Dev — run tests
docker build --target dev -t nmap-mcp-server-dev .
docker run --rm nmap-mcp-server-dev
```

### Configure your Agent

Add to your MCP client config (e.g., `claude_desktop_config.json` or `opencode.json`):

```json
{
  "mcpServers": {
    "nmap-mcp-server": {
      "command": "docker",
      "args": ["run", "--rm", "--network", "host", "-i", "nmap-mcp-server"]
    }
  }
}
```

### 3. Optionally verify Connection

Test the server manually using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector docker run -i --rm nmap-mcp-server
```

## Usage examples

### 1. Quick Discovery (Ping Scan)

Find live hosts on a local subnet before performing a deeper scan.

- **Prompt to Agent:** "Scan the 192.168.1.0/24 subnet and tell me which devices are online."
- **Agent Action:** Calls `ping_scan(target="192.168.1.0/24")`.

### 2. Detailed Service Enumeration

Identify the specific versions of software running on open ports.

- **Prompt to Agent:** "Check what services are running on 10.0.0.50. I need to know the exact versions."
- **Agent Action:** Calls `nmap_scan(target="10.0.0.50", flags="-sV")`.

### 3. Security Audit (Port Range)

Perform a stealthy scan on a specific range of ports to identify vulnerabilities.

- **Prompt to Agent:** "Perform a stealth SYN scan on scanme.nmap.org for ports 1 to 1000."
- **Agent Action:** Calls `nmap_scan(target="scanme.nmap.org", flags="-sS", ports="1-1000")`.

### 4. Web Fingerprinting

Fingerprint a web target with WhatWeb or make a specific HTTP request with curl.

- **Prompt to Agent:** "Fingerprint https://example.com and show detected web technologies."
- **Agent Action:** Calls `whatweb_scan(flags=["--no-errors"], url="https://example.com")`.
- **Agent Action:** Calls `curl_request(flags=["-I"], url="https://example.com")` for HTTP headers.

### 5. Agentic Workflow: "The Recon Loop"

AI agents can chain these tools together in a single conversation:

1.  **Discover**: Use `ping_scan` to find a target.
2.  **Scan**: Use `nmap_scan` to find open ports.
3.  **Fingerprint**: Use `whatweb_scan` or `curl_request` for web targets.
4.  **Analyze**: The agent interprets the `stdout` and suggests next steps based on the `security-researcher` persona.

## Development

```bash
# Mount local source for hot-reload
./run_dev.sh
```

The project root is volume-mounted so code changes take effect without rebuilding.

Or run directly:

```bash
uv sync
uv run src/server.py
```

## Dependencies

- `mcp[cli]>=1.27.0`
- `pytest>=9.0.3` (dev)
