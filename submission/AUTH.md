# Authentication decision

Version 0.2.0 intentionally runs in **anonymous, read-only mode**.

The server exposes only public literature-discovery operations and does not expose customer-specific data or write actions. It therefore does not require an account-linking flow in this release.

Do not add shared institutional CNKI credentials to the public service. If a future version introduces per-user/private institutional data or write actions, redesign the authorization boundary and implement OAuth 2.1 according to the then-current OpenAI/MCP authorization requirements before shipping those features.
