# Data flow and privacy model

```text
ChatGPT / Codex
      |
      | MCP tool arguments: query/filter or CNKI paper URL
      v
CNKI Scholar Remote MCP
      |
      | validated subprocess args
      v
ExquisiteCore cnki CLI (pinned build)
      |
      | HTTPS
      v
https://kns.cnki.net
      |
      | bibliographic metadata / references
      v
CNKI Scholar -> MCP response -> host
```

## What this release does not collect

- no CNKI username/password;
- no institutional login cookies;
- no payment data;
- no user profile database;
- no write actions;
- no full-text downloading or paywall bypass.

The application code has no persistent query/result database. Hosting infrastructure may produce access/error logs; production operators should avoid logging request bodies or raw search terms where possible, redact personal information, and publish/configure finite retention.

## Network boundaries

- Search operations may contact CNKI through the pinned CLI.
- Detail/reference input is restricted to HTTPS URLs whose hostname is exactly `kns.cnki.net`.
- The server does not expose a generic fetch-URL tool.
