# Install CUQU找搭子 MCP Server

Zero-dependency Python MCP server (JSON-RPC 2.0 over stdio) plus a hosted remote endpoint.

## Option A — hosted remote endpoint (no install required)

```json
{
  "mcpServers": {
    "cuqu": {
      "type": "streamable-http",
      "url": "https://agent.cuqu.net/mcp"
    }
  }
}
```

## Option B — local stdio (PyPI package `cuqu-mcp`)

```json
{
  "mcpServers": {
    "cuqu": {
      "command": "uvx",
      "args": ["cuqu-mcp"]
    }
  }
}
```

or

```bash
pip install cuqu-mcp
cuqu-mcp
```

## Option C — from source

```bash
git clone https://github.com/cuqu-net/cuqu-skill
cd cuqu-skill
python -u server.py
```

## API key

Read tools need no key: `query_activities`, `get_activity_card`, `query_venues`, `generate_urllink`.

Write tools (`create_activity`, `register_event`, `create_payment`, `check_in`) need a user-scoped key:

```json
"env": { "CUQU_API_KEY": "cq-sk-..." }
```

Issue a key via the scan-to-issue flow documented at https://cuqu.net/llms.txt

## Verify

```bash
python scripts/check-mcp.py
```
