from __future__ import annotations

import unittest

from cnki_chatgpt.policy import landing_html, privacy_html, support_html, terms_html


class PolicyTests(unittest.TestCase):
    def test_policy_pages_disclose_independence(self) -> None:
        for page in (landing_html(), privacy_html(), terms_html(), support_html()):
            self.assertIn("not an official CNKI product", page)

    def test_privacy_discloses_cnki_data_flow(self) -> None:
        page = privacy_html()
        self.assertIn("kns.cnki.net", page)
        self.assertIn("does not persist search queries", page)

    def test_terms_disallow_bypass_claim(self) -> None:
        page = terms_html()
        self.assertIn("does not bypass paywalls", page)
        self.assertIn("CAPTCHA", page)


if __name__ == "__main__":
    unittest.main()
