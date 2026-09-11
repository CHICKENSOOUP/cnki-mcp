# Production deployment notes

1. Deploy the container on a host that can reach `https://kns.cnki.net`.
2. Put it behind a public HTTPS origin. The MCP URL should be `https://YOUR_HOST/mcp`.
3. Set at least:

```env
PUBLIC_BASE_URL=https://YOUR_HOST
MCP_ALLOWED_HOSTS=YOUR_HOST,YOUR_HOST:*
PUBLISHER_NAME=YOUR VERIFIED OPENAI DEVELOPER OR BUSINESS NAME
SUPPORT_EMAIL=YOUR SUPPORT ADDRESS
```

4. If OpenAI asks for domain verification, set `OPENAI_APPS_CHALLENGE` to the exact token shown in the submission portal and redeploy. The server exposes it at `/.well-known/openai-apps-challenge`.
5. Keep infrastructure logs minimal. Avoid logging request bodies/search terms. Configure finite retention and redact personal data.
6. Do not add institutional CNKI cookies, passwords, or shared credentials to environment variables or tool responses.
7. Keep the upstream request rate conservative. The adapter already caps concurrency and result count; add platform-level abuse/rate protections if the endpoint is public.

Build the production portable plugin metadata after the HTTPS origin is live:

```bash
python scripts/configure_plugin.py \
  --base-url https://YOUR_HOST \
  --publisher "YOUR VERIFIED PUBLISHER NAME"
```

The generated `dist-plugin/` directory contains production `plugin.json`, `mcp.json`, and the skill.
