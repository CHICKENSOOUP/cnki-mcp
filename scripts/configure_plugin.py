from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render_json(template_path: Path, base_url: str, publisher: str) -> dict:
    text = template_path.read_text(encoding="utf-8")
    text = text.replace("__PUBLIC_BASE_URL__", base_url.rstrip("/"))
    text = text.replace("__PUBLISHER_NAME__", publisher)
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build production plugin.json and mcp.json with a real HTTPS deployment URL.")
    parser.add_argument("--base-url", required=True, help="Public HTTPS origin, e.g. https://cnki-scholar.example.com")
    parser.add_argument("--publisher", required=True, help="Verified developer/business name used in OpenAI Platform")
    parser.add_argument("--out", default=str(ROOT / "dist-plugin"), help="Output directory")
    args = parser.parse_args()

    if not args.base_url.startswith("https://"):
        raise SystemExit("--base-url must use HTTPS for a production plugin")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "plugin.json").write_text(
        json.dumps(render_json(ROOT / "plugin.template.json", args.base_url, args.publisher), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "mcp.json").write_text(
        json.dumps(render_json(ROOT / "mcp.template.json", args.base_url, args.publisher), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    skill_out = out / "skills" / "cnki-literature-search"
    skill_out.mkdir(parents=True, exist_ok=True)
    (skill_out / "SKILL.md").write_text(
        (ROOT / "skills" / "cnki-literature-search" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(f"Production plugin package written to {out}")


if __name__ == "__main__":
    main()
