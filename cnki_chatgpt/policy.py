from __future__ import annotations

from html import escape

from .config import settings


def _link(path: str) -> str:
    base = settings.public_base_url or ""
    return f"{base}{path}" if base else path


def _support_text() -> str:
    if settings.support_email:
        safe = escape(settings.support_email)
        return f'<a href="mailto:{safe}">{safe}</a>'
    return "the publisher contact listed in the plugin directory"


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · CNKI Scholar</title>
<style>
body{{font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:820px;margin:48px auto;padding:0 20px;line-height:1.65;color:#171717}}
a{{color:#174ea6}} code{{background:#f4f4f4;padding:.1rem .3rem;border-radius:.25rem}}
small{{color:#666}} .nav a{{margin-right:16px}}
</style>
</head>
<body>
<div class="nav"><a href="{_link('/')}">Home</a><a href="{_link('/privacy')}">Privacy</a><a href="{_link('/terms')}">Terms</a><a href="{_link('/support')}">Support</a></div>
<h1>{escape(title)}</h1>
{body}
<hr><small>CNKI Scholar is an independent open-source adapter and is not an official CNKI product.</small>
</body></html>"""


def landing_html() -> str:
    return _page(
        "CNKI Scholar",
        """
<p>A read-only literature discovery service for CNKI metadata. It supports search, paper metadata lookup, and reference-list retrieval through a Remote MCP endpoint.</p>
<p>The service intentionally does not download paywalled PDF/CAJ files, bypass authentication, or defeat CAPTCHA/anti-bot checks.</p>
<p><strong>MCP endpoint:</strong> <code>/mcp</code> &nbsp; <strong>Health:</strong> <code>/health</code></p>
""",
    )


def privacy_html() -> str:
    return _page(
        "Privacy Policy",
        f"""
<p><strong>Scope.</strong> CNKI Scholar is a read-only connector that forwards the minimum query parameters needed to perform CNKI literature searches and retrieve public bibliographic metadata.</p>
<p><strong>Data sent to CNKI.</strong> Search terms, search filters, and CNKI paper URLs supplied to a tool are sent to CNKI's <code>kns.cnki.net</code> service to fulfill that request.</p>
<p><strong>Accounts and personal data.</strong> This release does not provide user accounts and does not request CNKI credentials, institutional credentials, payment information, or other customer-specific records.</p>
<p><strong>Storage.</strong> The application code does not persist search queries, tool inputs, or tool outputs to a database. The hosting provider, reverse proxy, or security layer may generate normal operational logs. Operators should configure those logs to avoid request bodies/search terms where possible, redact personal data, and keep logs only as long as needed for security and reliability.</p>
<p><strong>Third parties.</strong> Requests rely on CNKI as the upstream literature service and on the operator's hosting/network providers. Their own policies may apply to traffic they receive.</p>
<p><strong>Deletion/contact.</strong> Because the application itself has no user database in this release, it normally has no stored user record to delete. For operational-log questions, contact {_support_text()}.</p>
<p><strong>Security.</strong> Inputs are validated, paper-detail requests are restricted to HTTPS URLs on <code>kns.cnki.net</code>, and the server does not expose arbitrary URL fetching.</p>
""",
    )


def terms_html() -> str:
    return _page(
        "Terms of Service",
        f"""
<p>CNKI Scholar is provided as an independent research utility for bibliographic discovery. It is not affiliated with, endorsed by, or operated by CNKI.</p>
<p>Use the service only for lawful research purposes and in accordance with the terms that apply to CNKI and any institution through which you access CNKI.</p>
<p>The service provides metadata and reference-list retrieval. It does not promise full-text access, does not bypass paywalls, and does not attempt to circumvent CAPTCHA, rate limits, access controls, or anti-bot measures.</p>
<p>Results may be incomplete, stale, or affected by upstream availability. Verify important citations and bibliographic details in the original source before relying on them.</p>
<p>The operator may rate-limit, suspend, or disable access to protect service stability or comply with legal/platform requirements.</p>
<p>Questions: {_support_text()}.</p>
""",
    )


def support_html() -> str:
    return _page(
        "Support",
        f"""
<p>For bugs, privacy questions, or incorrect tool behavior, contact {_support_text()}.</p>
<p>When reporting an error, include the approximate time, tool name, and non-sensitive error message. Do not send passwords, institutional login cookies, payment information, or other secrets.</p>
""",
    )
