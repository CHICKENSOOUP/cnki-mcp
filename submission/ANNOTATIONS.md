# MCP tool annotations and justifications

All three tools are read-only and access the external CNKI service, so they use the same safety annotations:

| Tool | readOnlyHint | destructiveHint | idempotentHint | openWorldHint | Justification |
|---|---:|---:|---:|---:|---|
| `search_cnki` | true | false | true | true | Reads external CNKI bibliographic search results; does not mutate CNKI or local user data. Repeating the same request has no intended side effect. |
| `get_cnki_paper_detail` | true | false | true | true | Reads metadata for an allowlisted `kns.cnki.net` paper URL; no writes or destructive action. |
| `get_cnki_references` | true | false | true | true | Reads an external reference list; no writes or destructive action. |

`openWorldHint=true` is intentional because results depend on a third-party network service and can change over time.
