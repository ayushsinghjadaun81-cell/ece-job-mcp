# ECE Job MCP Server

Our first MCP experiment: give Claude one external capability, `search_jobs`.

## What this version does

It exposes two tools:

- `search_jobs(keywords, location)` — searches a tiny demo dataset.
- `server_status()` — confirms that the MCP server is reachable.

**Important:** this is intentionally NOT a real job scraper yet. The first goal is to prove the complete MCP connection:

Claude → remote MCP → our Python server → tool result → Claude.

Once that works, we can replace the demo dataset with a real, legally/technically appropriate job-data source.

## Requirements

Python 3.10+.

## Run locally

Create a virtual environment, then:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
python server.py
```

The MCP endpoint is:

```text
http://localhost:8000/mcp
```

## Important: Claude Web cannot reach localhost

Claude's web custom connector connects to the MCP server from Anthropic's cloud infrastructure. Therefore, for Claude Web, the server must eventually be deployed at a public HTTPS URL.

Do NOT expose a server publicly without authentication/security once it has real tools or private data.

## Next stages

1. Prove the server works locally.
2. Deploy a minimal public HTTPS version.
3. Add it to Claude: Settings → Connectors → Add → Add custom connector.
4. Test `server_status`.
5. Test `search_jobs`.
6. Only then add real job retrieval.
7. Add separate tools for job details and saving jobs.
8. Keep job scoring in Claude/Skill at first rather than hiding all logic inside the MCP server.
