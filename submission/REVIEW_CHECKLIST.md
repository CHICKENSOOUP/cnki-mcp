# OpenAI public-submission checklist

## Publisher and listing

- [ ] Use an OpenAI Platform organization with **Apps Management: Write** permission.
- [ ] Complete individual or business identity verification.
- [ ] Replace `CNKI Scholar contributors` with the exact verified publisher identity where required.
- [ ] Add production-owned logo/icon assets; do not use CNKI branding in a way that implies affiliation.
- [ ] Fill website, support, privacy, and terms URLs with the real production HTTPS domain.
- [ ] Select countries/regions where the service is intended to operate.

## MCP deployment

- [ ] Deploy to a stable public HTTPS origin.
- [ ] Confirm `https://YOUR_HOST/mcp` is reachable by the OpenAI scanner.
- [ ] Set `PUBLIC_BASE_URL=https://YOUR_HOST`.
- [ ] Set `MCP_ALLOWED_HOSTS=YOUR_HOST,YOUR_HOST:*`.
- [ ] If the portal requests domain verification, set `OPENAI_APPS_CHALLENGE` to the exact token and verify `https://YOUR_HOST/.well-known/openai-apps-challenge` returns it.
- [ ] Run **Scan Tools** and confirm the three discovered tools match this repository.
- [ ] Confirm every tool reports read-only/open-world/destructive annotations accurately.
- [ ] Confirm no debug payloads, credentials, cookies, secrets, or unnecessary personal data appear in MCP responses.

## Plugin package

- [ ] Run `python scripts/configure_plugin.py --base-url https://YOUR_HOST --publisher "VERIFIED NAME"`.
- [ ] Validate generated `dist-plugin/plugin.json` and `dist-plugin/mcp.json` against the current Agent Plugin schemas.
- [ ] Upload/import the `skills/cnki-literature-search` skill if the portal does not import it automatically from the package.
- [ ] Copy realistic starter prompts from `submission/STARTER_PROMPTS.md`.
- [ ] Enter exactly the 5 positive + 3 negative cases from `submission/TEST_CASES.md` and verify actual behavior.
- [ ] Paste release notes from `submission/RELEASE_NOTES.md`.

## Live functional checks

- [ ] Exact-title CNKI search works.
- [ ] Topic search with `journal/master/phd` works.
- [ ] Sorting by `cited` and `date` works.
- [ ] Paper detail works for a returned `kns.cnki.net` URL.
- [ ] Reference retrieval works.
- [ ] Non-CNKI URL is rejected.
- [ ] Empty query / over-limit size is rejected.
- [ ] CAPTCHA/anti-bot response becomes an explicit error rather than a bypass attempt.
- [ ] `/privacy`, `/terms`, `/support`, and `/health` are public over HTTPS.
