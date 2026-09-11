from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginPackageTests(unittest.TestCase):
    def test_portable_manifest_shape(self) -> None:
        manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(manifest["name"], "cnki-scholar")
        self.assertEqual(manifest["version"], "0.2.0")
        self.assertEqual(manifest["extensions"]["com.openai"]["interface"]["capabilities"], ["Read"])

    def test_mcp_manifest_shape(self) -> None:
        config = json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
        server = config["mcpServers"]["cnki-scholar"]
        self.assertEqual(server["type"], "streamable-http")
        self.assertTrue(server["url"].endswith("/mcp"))

    def test_skill_exists_and_warns_against_false_novelty(self) -> None:
        skill = (ROOT / "skills" / "cnki-literature-search" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: cnki-literature-search", skill)
        self.assertIn("zero-result query", skill)

    def test_production_generator_requires_https_and_renders_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "configure_plugin.py"),
                    "--base-url",
                    "https://research.example.org",
                    "--publisher",
                    "Example Researcher",
                    "--out",
                    tmp,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            manifest = json.loads((Path(tmp) / "plugin.json").read_text(encoding="utf-8"))
            mcp = json.loads((Path(tmp) / "mcp.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["homepage"], "https://research.example.org/")
            self.assertEqual(manifest["author"]["name"], "Example Researcher")
            self.assertEqual(mcp["mcpServers"]["cnki-scholar"]["url"], "https://research.example.org/mcp")


if __name__ == "__main__":
    unittest.main()
