# CUQU (找搭子) MCP Server

Open-source MCP server giving AI agents live access to **[CUQU (找搭子)](https://cuqu.net)** — a local offline social activities platform in China (Shenzhen-based, 10+ cities incl. Hong Kong, China). Users discover and book offline interest-based group activities (board games, frisbee, hiking, badminton, fishing, anime and 100+ more categories); organizers publish and run events.

**Live demo endpoint (hosted):** `https://agent.cuqu.net/mcp` (Streamable HTTP, per-user `cq-sk-` keys — see [llms.txt](https://cuqu.net/llms.txt))
**Agent Card:** https://cuqu.net/.well-known/agent.json

## What this repository contains

| Path | What it is |
|---|---|
| `server.py` | **The MCP server implementation** — zero-dependency Python, JSON-RPC 2.0 over stdio. Read tools call CUQU's public live activity API; write tools forward to the hosted gateway with a user key. |
| `Dockerfile` | One-command container build for the server (glama.ai / docker / any MCP host). |
| `glama.json` | glama.ai directory metadata & maintainership. |
| `scripts/check-mcp.py` | Connectivity check for the hosted gateway. |
| `skills/`, `docs/` | Agent skill manifests and platform integration docs (Qwen/Dify/Yuanqi). |

## Tools (8)

| Tool | Type | Description |
|---|---|---|
| `query_activities` | read (no key) | Search live activities by type / city / date — 100+ categories, real-time public data |
| `get_activity_card` | read (no key) | Full detail card for one activity (time, venue, price, booking progress, organizer, cover) |
| `query_venues` | read (no key) | Curated partner venue directory (capacity, per-head price) |
| `generate_urllink` | read (no key) | Share link + WeChat mini-program path for an activity |
| `create_activity` | write (key) | Organizer publishes a new event |
| `register_event` | write (key) | Book a user into an activity |
| `create_payment` | write (key) | Create WeChat Pay for a booking order |
| `check_in` | write (key) | On-site check-in / redemption |

Write tools are executed by the hosted gateway and require `CUQU_API_KEY` (`cq-sk-...`, issued via scan-to-issue flow documented in [llms.txt](https://cuqu.net/llms.txt)).

## Quick start

```bash
# stdio, zero dependencies, Python 3.9+
python -u server.py

# or via Docker
docker build -t cuqu-mcp .
docker run -i cuqu-mcp
```

Claude Desktop / any stdio MCP client:

```json
{
  "mcpServers": {
    "cuqu": {
      "command": "python",
      "args": ["-u", "/path/to/server.py"],
      "env": { "CUQU_API_KEY": "cq-sk-...(optional, enables write tools)" }
    }
  }
}
```

## License

MIT — © 2026 光天科技（深圳）有限公司 (Guangtian Technology (Shenzhen) Co., Ltd.)
