from __future__ import annotations

import asyncio
from typing import Any, Literal

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response

from .config import settings
from .policy import landing_html, privacy_html, support_html, terms_html
from .runner import build_detail_args, build_reference_args, build_search_args, run_cnki

mcp = MCPServer(
    "cnki-scholar",
    title="CNKI Scholar",
    description="Read-only CNKI literature discovery: search bibliographic records, inspect paper metadata, and retrieve reference lists.",
    instructions=(
        "Use search_cnki for literature discovery. Use exact title search when checking whether a specific topic/title has already been studied, "
        "and use topic/keyword variants for broader novelty checks. Use get_cnki_paper_detail only with kns.cnki.net URLs returned by CNKI. "
        "Never invent metadata or interpret one empty search as proof that no prior work exists. If CNKI triggers anti-bot verification, report that clearly."
    ),
    website_url=settings.public_base_url,
    version="0.2.0",
)
_gate = asyncio.Semaphore(settings.max_concurrency)

READ_ONLY = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=True,
)


@mcp.tool(
    title="Search CNKI literature",
    description=(
        "Search CNKI bibliographic metadata. Supports topic, keyword, exact title, author, abstract, full-text-index, and DOI fields; "
        "optional year and document-type filters; and relevance/date/citation/download sorting. Use title search for suspected exact matches, "
        "then broaden to topic/keyword variants before making novelty claims."
    ),
    annotations=READ_ONLY,
    meta={
        "openai/toolInvocation/invoking": "Searching CNKI…",
        "openai/toolInvocation/invoked": "CNKI search complete",
    },
    structured_output=True,
)
async def search_cnki(
    query: str,
    field: Literal["topic", "keyword", "title", "author", "abstract", "fulltext", "doi"] = "topic",
    from_year: int | None = None,
    to_year: int | None = None,
    types: list[Literal["journal", "master", "phd", "conference", "newspaper", "yearbook"]] | None = None,
    sort: Literal["relevance", "date", "cited", "downloads"] = "relevance",
    size: int = 20,
) -> dict[str, Any]:
    args = build_search_args(
        query,
        field=field,
        from_year=from_year,
        to_year=to_year,
        types=types,
        sort=sort,
        size=size,
    )
    async with _gate:
        data = await run_cnki(args)
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected CNKI search payload")
    return data


@mcp.tool(
    title="Read CNKI paper metadata",
    description=(
        "Read bibliographic metadata for one HTTPS kns.cnki.net paper URL, including title, authors, institutions, abstract, keywords, DOI, "
        "source, year, fund information, citation/download counts when available. Optionally include references."
    ),
    annotations=READ_ONLY,
    meta={
        "openai/toolInvocation/invoking": "Reading CNKI metadata…",
        "openai/toolInvocation/invoked": "CNKI metadata loaded",
    },
    structured_output=True,
)
async def get_cnki_paper_detail(url: str, with_references: bool = False) -> dict[str, Any]:
    args = build_detail_args(url, with_references=with_references)
    async with _gate:
        data = await run_cnki(args)
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected CNKI detail payload")
    return data


@mcp.tool(
    title="Read a CNKI reference list",
    description="Retrieve the reference list associated with one HTTPS kns.cnki.net paper URL. This is read-only metadata retrieval, not full-text access.",
    annotations=READ_ONLY,
    meta={
        "openai/toolInvocation/invoking": "Loading CNKI references…",
        "openai/toolInvocation/invoked": "CNKI references loaded",
    },
    structured_output=True,
)
async def get_cnki_references(url: str) -> dict[str, Any]:
    args = build_reference_args(url)
    async with _gate:
        data = await run_cnki(args)
    return {"references": data}


@mcp.custom_route("/", methods=["GET"])
async def home(_: Request) -> HTMLResponse:
    return HTMLResponse(landing_html())


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True, "service": "cnki-scholar", "version": "0.2.0"})


@mcp.custom_route("/privacy", methods=["GET"])
async def privacy(_: Request) -> HTMLResponse:
    return HTMLResponse(privacy_html())


@mcp.custom_route("/terms", methods=["GET"])
async def terms(_: Request) -> HTMLResponse:
    return HTMLResponse(terms_html())


@mcp.custom_route("/support", methods=["GET"])
async def support(_: Request) -> HTMLResponse:
    return HTMLResponse(support_html())


@mcp.custom_route("/.well-known/openai-apps-challenge", methods=["GET"])
async def openai_apps_challenge(_: Request) -> Response:
    if not settings.openai_apps_challenge:
        return PlainTextResponse("Domain verification token is not configured", status_code=404)
    return PlainTextResponse(settings.openai_apps_challenge)


def main() -> None:
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=list(settings.allowed_hosts),
        allowed_origins=list(settings.allowed_origins),
    )
    mcp.run(
        transport="streamable-http",
        stateless_http=True,
        json_response=True,
        host=settings.host,
        port=settings.port,
        transport_security=security,
    )


if __name__ == "__main__":
    main()
