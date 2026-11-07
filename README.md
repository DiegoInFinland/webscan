# Webscan MCP Server

> **Disclaimer:** This is a personal project, and still a work in progress, and is not intended for production in real environments. Use at your own risk!

Dockerized Kali Linux container that exposes Nmap, curl, and WhatWeb as lightweight [MCP (Model Context Protocol)](https://modelcontextprotocol.io) tools for AI agents. Only scan targets you are authorized to assess.

## Architecture

```
AI Client (MCP-compatible)
    │  MCP protocol (stdio)
    ▼
Docker Container (kalilinux/kali-rolling)
    │
    ├── uv             (Python package manager)
    ├── src/server.py  (FastMCP server)
    │   ├── @mcp.tool()  →  local_ip()
    │   ├── @mcp.tool()  →  nmap_scan(target, flags, ports)
    │   ├── @mcp.tool()  →  ping_scan(target, disable_arp_ping=False)
    │   ├── @mcp.tool()  →  ping6_scan(target)
    │   ├── @mcp.tool()  →  curl_request(flags, url)
    │   └── @mcp.tool()  →  whatweb_scan(flags, url)
    ├── nmap
    ├── curl
    └── whatweb
```

## Quick Start

Run these commands from the `webscan` project root. Build the image, then configure your MCP client to launch it.

### Prerequisites

- Docker
- `uv` (only for local development)

### Build the Docker image

```bash
# Build the image (prod stage is default)
docker build -t webscan .

# Run (stdio-based MCP server)
docker run --rm --network host -i webscan

# Dev — run tests
docker build --target dev -t webscan-dev .
docker run --rm webscan-dev
```

### Configure your Agent

For a client that uses the `mcpServers` format (for example, Claude Desktop), add:

```json
{
  "mcpServers": {
    "webscan": {
      "command": "docker",
      "args": ["run", "--rm", "--network", "host", "-i", "webscan"]
    }
  }
}
```

On macOS and Windows, Docker runs in a VM: `--network host` does not necessarily expose the host's LAN interface to the container. Check `local_ip` and supply the intended subnet explicitly before discovery scans.

### Optionally verify the connection

Test the server manually using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector docker run --rm --network host -i webscan
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

Scan a specific port range on an authorized target.

- **Prompt to Agent:** "Scan ports 1 to 1000 on my authorized test host."
- **Agent Action:** Calls `nmap_scan(target="test.example.com", ports="1-1000")`.

### 4. Web Fingerprinting

Fingerprint a web target with WhatWeb or make a specific HTTP request with curl.

- **Prompt to Agent:** "Fingerprint https://example.com and show detected web technologies."
- **Agent Action:** Calls `whatweb_scan(flags=["--no-errors"], url="https://example.com")`.
- **Agent Action:** Calls `curl_request(flags=["-I"], url="https://example.com")` for HTTP headers.

### 5. Agentic Workflow: "The Recon Loop"

AI agents can chain these tools together in a single conversation:

1. **Discover**: Use `ping_scan` to find hosts in an authorized range.
2. **Select**: Confirm which hosts may be scanned further.
3. **Scan**: Use `nmap_scan` to find open ports.
4. **Fingerprint**: Use `whatweb_scan` or `curl_request` for web targets.
5. **Analyze**: Interpret the `stdout`, `stderr`, and `returncode` returned by each tool.

## Development

```bash
# Mount local source and run the MCP server in Docker
./run_dev.sh
```

The project root is volume-mounted so code changes take effect on the next run without rebuilding. Build the `webscan` image first.

Or run directly:

```bash
uv sync
uv run src/server.py
```
