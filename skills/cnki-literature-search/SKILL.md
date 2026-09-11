---
name: cnki-literature-search
description: Search CNKI systematically for Chinese journal articles, master's theses, PhD theses, and related bibliographic evidence; assess prior-work overlap without overclaiming novelty.
---

# CNKI literature search

Use the CNKI Scholar MCP tools when the user's question depends on Chinese academic literature indexed by CNKI.

The user's explicit instructions take precedence over this skill. Keep the work read-only.

## Core workflow

1. Translate the research question into 2–5 compact Chinese concept groups. Do not put every concept into one over-constrained query.
2. When the user asks whether a title/topic has already been written about, begin with an exact `title` search using the distinctive title phrase.
3. Then run broader `topic` or `keyword` searches with synonyms, adjacent spatial scales, population terms, and method terms as appropriate.
4. For thesis-oriented novelty checks, include `master` and `phd`; normally include `journal` as well.
5. Use year filters only when the user requests them or when freshness is central. Do not hide older foundational work just to make a topic look novel.
6. Use `cited` sorting to find established work and `date` sorting to find recent work. These answer different questions, so use both when novelty matters.
7. Inspect `get_cnki_paper_detail` for the strongest matches before making claims about overlap. Use `get_cnki_references` when citation-chain tracing will help.
8. Present the search scope: field, main query variants, document types, years, and sort order. A zero-result query is evidence only for that query, not proof that no prior work exists.

## Query relaxation for sparse results

If a search returns no useful matches, relax one dimension at a time:

- exact title → distinctive title fragment;
- population + place + object → population + object;
- specific spatial type → broader parent type;
- exact method term → omit the method term;
- one modern term → common older synonyms.

## Novelty and overlap checks

Separate four levels of overlap:

- **Exact-title overlap**: same or near-identical title.
- **Object overlap**: same population + same spatial object.
- **Method overlap**: same evaluation or empirical method.
- **Contribution overlap**: same research question and claimed planning/design contribution.

A geographic change alone is usually weak differentiation. Stronger differentiation changes the research question, spatial mechanism, behavior/process being studied, or evidence method.

## Evidence discipline

- Never invent a title, author, institution, year, DOI, citation count, abstract, or source.
- Attribute metadata only when it appears in tool output.
- If CNKI triggers CAPTCHA/anti-bot verification, say the upstream service blocked the request; do not propose bypassing it.
- This plugin is for metadata/reference discovery. Do not claim it can provide paywalled full text or bypass institutional access.
- Verify consequential bibliographic facts against the paper-detail record or original source before finalizing a literature review.
