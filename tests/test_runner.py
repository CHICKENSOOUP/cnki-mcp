from __future__ import annotations

import asyncio
import os
import stat
import tempfile
import unittest
from pathlib import Path

from cnki_chatgpt.runner import (
    CNKICaptchaError,
    build_detail_args,
    build_search_args,
    run_cnki,
)


class RunnerTests(unittest.TestCase):
    def test_build_search_args(self) -> None:
        args = build_search_args(
            "视障人群 单位制社区",
            field="topic",
            from_year=2015,
            to_year=2026,
            types=["master", "phd", "journal"],
            sort="cited",
            size=50,
            max_results=100,
        )
        self.assertEqual(args[0:2], ["search", "视障人群 单位制社区"])
        self.assertIn("--from=2015", args)
        self.assertIn("--to=2026", args)
        self.assertIn("--type=master", args)
        self.assertIn("--sort=cited", args)
        self.assertIn("--format=json", args)

    def test_detail_rejects_non_cnki_hosts(self) -> None:
        with self.assertRaises(ValueError):
            build_detail_args("https://example.com/paper")

    def _script(self, body: str) -> str:
        temp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".py")
        temp.write("#!/usr/bin/env python3\n" + body)
        temp.close()
        mode = os.stat(temp.name).st_mode
        os.chmod(temp.name, mode | stat.S_IXUSR)
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        return temp.name

    def test_run_cnki_parses_json(self) -> None:
        script = self._script('print(\'{"total_hits": 1, "results": []}\')\n')
        data = asyncio.run(run_cnki(["search", "x"], binary=script, timeout=5))
        self.assertEqual(data["total_hits"], 1)

    def test_run_cnki_maps_captcha_exit_code(self) -> None:
        script = self._script('import sys\nprint("captcha", file=sys.stderr)\nsys.exit(2)\n')
        with self.assertRaises(CNKICaptchaError):
            asyncio.run(run_cnki(["search", "x"], binary=script, timeout=5))


if __name__ == "__main__":
    unittest.main()
