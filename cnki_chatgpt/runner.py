from __future__ import annotations

import asyncio
import json
from typing import Any, Iterable
from urllib.parse import urlparse

from .config import settings

ALLOWED_FIELDS = {"topic", "keyword", "title", "author", "abstract", "fulltext", "doi"}
ALLOWED_TYPES = {"journal", "master", "phd", "conference", "newspaper", "yearbook"}
ALLOWED_SORTS = {"relevance", "date", "cited", "downloads"}
ALLOWED_CNKI_HOSTS = {"kns.cnki.net"}


class CNKIError(RuntimeError):
    """Base error returned by the upstream CNKI CLI."""


class CNKICaptchaError(CNKIError):
    """CNKI requested captcha / anti-bot verification."""


class CNKINoResultsError(CNKIError):
    """CNKI returned no results."""


class CNKIInvalidArgumentError(CNKIError):
    """The query arguments were rejected by the upstream CLI."""


def _validate_cnki_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_CNKI_HOSTS:
        raise ValueError("Only https://kns.cnki.net/... paper URLs are accepted")
    return url.strip()


def build_search_args(
    query: str,
    *,
    field: str = "topic",
    from_year: int | None = None,
    to_year: int | None = None,
    types: Iterable[str] | None = None,
    sort: str = "relevance",
    size: int = 20,
    max_results: int | None = None,
) -> list[str]:
    query = query.strip()
    if not query:
        raise ValueError("query cannot be empty")
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"field must be one of: {', '.join(sorted(ALLOWED_FIELDS))}")
    if sort not in ALLOWED_SORTS:
        raise ValueError(f"sort must be one of: {', '.join(sorted(ALLOWED_SORTS))}")

    limit = settings.max_results if max_results is None else max_results
    if not 1 <= size <= limit:
        raise ValueError(f"size must be between 1 and {limit}")
    if from_year is not None and not 1900 <= from_year <= 2100:
        raise ValueError("from_year must be between 1900 and 2100")
    if to_year is not None and not 1900 <= to_year <= 2100:
        raise ValueError("to_year must be between 1900 and 2100")
    if from_year is not None and to_year is not None and from_year > to_year:
        raise ValueError("from_year cannot be later than to_year")

    normalized_types: list[str] = []
    for doc_type in types or []:
        if doc_type not in ALLOWED_TYPES:
            raise ValueError(f"unsupported document type: {doc_type}")
        if doc_type not in normalized_types:
            normalized_types.append(doc_type)

    args = [
        "search",
        query,
        f"--field={field}",
        f"--sort={sort}",
        f"--size={size}",
        "--format=json",
    ]
    if from_year is not None:
        args.append(f"--from={from_year}")
    if to_year is not None:
        args.append(f"--to={to_year}")
    for doc_type in normalized_types:
        args.append(f"--type={doc_type}")
    return args


def build_detail_args(url: str, *, with_references: bool = False) -> list[str]:
    validated = _validate_cnki_url(url)
    args = ["detail", validated, "--format=json"]
    if with_references:
        args.append("--with-refs")
    return args


def build_reference_args(url: str) -> list[str]:
    return ["refs", _validate_cnki_url(url), "--format=json"]


async def run_cnki(args: list[str], *, binary: str | None = None, timeout: int | None = None) -> Any:
    executable = binary or settings.cnki_bin
    timeout_seconds = timeout or settings.timeout_seconds

    try:
        process = await asyncio.create_subprocess_exec(
            executable,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise CNKIError(f"CNKI CLI was not found at {executable!r}") from exc

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError as exc:
        process.kill()
        await process.communicate()
        raise CNKIError(f"CNKI request timed out after {timeout_seconds} seconds") from exc

    out = stdout.decode("utf-8", errors="replace").strip()
    err = stderr.decode("utf-8", errors="replace").strip()

    if process.returncode != 0:
        detail = err or out or f"cnki exited with code {process.returncode}"
        if process.returncode == 2:
            raise CNKICaptchaError(f"CNKI anti-bot verification was triggered: {detail}")
        if process.returncode == 3:
            raise CNKINoResultsError("CNKI returned no matching records")
        if process.returncode == 4:
            raise CNKIInvalidArgumentError(detail)
        raise CNKIError(detail)

    if not out:
        raise CNKIError("CNKI CLI returned an empty response")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise CNKIError("CNKI CLI returned non-JSON output") from exc
