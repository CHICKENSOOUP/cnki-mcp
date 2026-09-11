# CNKI Scholar for ChatGPT / Codex

**Language:** [English](README.en.md) | [简体中文](README.md)

CNKI Scholar is a small service that lets ChatGPT, Codex, and other tools search CNKI (China National Knowledge Infrastructure) metadata. It searches bibliographic records, reads abstracts and keywords, and retrieves paper details and reference lists. Results can be returned as JSON or citation text.

It only reads literature metadata. It does not download paywalled full text, collect CNKI usernames, passwords, or cookies, or try to bypass CAPTCHAs and access restrictions.

## What it does

| Tool | Purpose |
|---|---|
| `search_cnki` | Search by topic, keyword, title, author, abstract, full text, or DOI; filter by year and document type; choose a sort order |
| `get_cnki_paper_detail` | Read title, authors, institutions, abstract, keywords, DOI, source, funding, and citation/download counts |
| `get_cnki_references` | Read the references for one paper |

Supported document types include journals, master's theses, doctoral dissertations, conferences, newspapers, and yearbooks. Tool names and arguments stay stable for MCP clients.

## Two ways to use it

### Option 1: Local Docker

Use this when you want the complete CNKI tools. Install Docker Desktop and run `scripts/start.ps1`; it starts the local MCP service. See “One-click start” below.

### Option 2: Prompt only

Use this when you do not have Docker or a public server. Open [`CHATGPT_PROMPT.md`](CHATGPT_PROMPT.md), copy it into your own GPT instructions or the beginning of a chat, or upload the file directly.

This teaches a GPT the search workflow but does not run the local `cnki` command from this repository. Results depend on whether the current chat can use web search and whether CNKI pages are reachable.

## One-click start (Windows)

Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/), then run this from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

The script will:

1. check that Docker is available;
2. build the image;
3. start the service in the background;
4. wait for `http://127.0.0.1:8000/health` to succeed.

After startup:

- Homepage: <http://127.0.0.1:8000/>
- Health check: <http://127.0.0.1:8000/health>
- MCP endpoint: <http://127.0.0.1:8000/mcp>

Stop the service:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1 -Stop
```

Follow logs:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1 -Logs
```

The script never overwrites an existing `.env` file or prints its contents.

## Without the script

If Docker is already installed, run:

```bash
docker compose up --build -d
curl http://127.0.0.1:8000/health
docker compose down
```

## Use it from an MCP client

The development configuration is in the repository root `mcp.json` and points to:

```text
http://127.0.0.1:8000/mcp
```

After starting the service, add this URL to a Remote MCP client and ask, for example:

```text
Search CNKI for papers about large language models, limit results to 2020 and later, and sort by citations.
```

You can also ask for paper details or references. Detail and reference URLs must come from `https://kns.cnki.net/...`.

## Use the upstream `cnki` command directly

The Docker image builds and installs the upstream [`ExquisiteCore/CNKI-search`](https://github.com/ExquisiteCore/CNKI-search) `cnki` command. It can also be used on its own:

```bash
cnki search "deep learning" --size=10
cnki search "large language models" --from=2020 --to=2025 --sort=cited --size=30
cnki search "knowledge graph" --size=20 --format=citation
cnki detail "https://kns.cnki.net/kcms2/article/abstract?v=..." --with-refs --format=markdown
cnki refs "https://kns.cnki.net/kcms2/article/abstract?v=..."
```

The upstream command supports JSON, table, citation, and Markdown output. See [ExquisiteCore/CNKI-search](https://github.com/ExquisiteCore/CNKI-search) for all options.

## Configuration

Normal local use needs no configuration. To customize it, copy the example file:

```powershell
Copy-Item .env.example .env
```

Common variables:

| Variable | Default | Purpose |
|---|---|---|
| `CNKI_TIMEOUT_SECONDS` | `90` | Maximum wait time per request |
| `CNKI_MAX_RESULTS` | `100` | Maximum results per request |
| `CNKI_MAX_CONCURRENCY` | `2` | Concurrent requests to CNKI |
| `PORT` | `8000` | Local service port |
| `PUBLISHER_NAME` | `CNKI Scholar contributors` | Name shown on public pages |
| `SUPPORT_EMAIL` | Empty | Support address |

Keep `.env` on the local machine or server and never commit it. The example file contains no real credentials.

## Public deployment

If you only use the service on your own computer, stop here. To let other people access it:

1. prepare a publicly reachable HTTPS domain;
2. reverse-proxy that domain to the container's port 8000;
3. set `PUBLIC_BASE_URL`, `MCP_ALLOWED_HOSTS`, `PUBLISHER_NAME`, and `SUPPORT_EMAIL`;
4. run `python scripts/configure_plugin.py --base-url https://your-domain.example --publisher "Your name"` to generate plugin configuration.

See [`deploy/Caddyfile.example`](deploy/Caddyfile.example) for a reverse-proxy example. The `submission/` directory contains the OpenAI submission materials.

## Safety notes

- Paper detail URLs must be `https://kns.cnki.net/...`;
- PDF/CAJ downloads, paywall bypasses, and CAPTCHA bypasses are not provided;
- CNKI accounts, campus passwords, and institutional cookies are not required;
- the service does not write search results to a database;
- for a public deployment, avoid detailed request logs and set a retention period.

## Tests

The adapter tests do not need a CNKI connection:

```bash
python -m unittest discover -s tests -v
```

There are currently 11 tests. Real CNKI searches require a deployment that can reach `kns.cnki.net`.

## Project files

```text
cnki-mcp/
├── cnki_chatgpt/              # MCP service code
├── skills/                    # Literature-search skill
├── CHATGPT_PROMPT.md          # Prompt for direct use in a GPT
├── scripts/start.ps1          # Windows one-click start/stop script
├── scripts/configure_plugin.py  # Generate production plugin configuration
├── submission/                # Release materials
├── Dockerfile
├── docker-compose.yml
├── mcp.json
└── plugin.json
```

## License

This project is released under the MIT License. Copyright (c) 2026 Chengxu Xie. The upstream `ExquisiteCore/CNKI-search` project is also MIT-licensed; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).