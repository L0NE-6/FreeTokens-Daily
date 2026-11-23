import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sync_inventory


class SyncInventoryTests(unittest.TestCase):
    def test_markdown_parser_preserves_sections_and_fields(self):
        text = "\n".join(
            [
                "## 每天都能领（1 个）",
                "### 测试活动",
                "- 提供方：测试平台",
                "- 能领多少：100 Token",
                "- 怎么领：登录后点击领取",
                "- 去领：https://example.test/claim",
            ]
        )

        rows = sync_inventory.parse_markdown(text)

        self.assertEqual(1, len(rows))
        self.assertEqual("每天都能领（1 个）", rows[0]["section"])
        self.assertEqual("测试活动", rows[0]["title"])
        self.assertEqual("测试平台", rows[0]["fields"]["提供方"])

    def test_coverage_mapping_matches_verified_contracts(self):
        self.assertEqual(
            ("existing_repo", "MobileClaw-Daily"),
            sync_inventory.coverage_of(11),
        )
        self.assertEqual(
            ("existing_repo", "Inkstone-Daily"),
            sync_inventory.coverage_of(19),
        )
        self.assertEqual("manual", sync_inventory.coverage_of(34)[0])
        self.assertEqual(
            "quota_or_free_api",
            sync_inventory.coverage_of(29)[0],
        )

    def test_current_inventory_has_61_items_and_expected_categories(self):
        path = ROOT / "inventory.json"
        if not path.exists():
            self.skipTest("inventory.json has not been generated")
        payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(61, payload["count"])
        self.assertEqual(61, len(payload["items"]))
        counts = payload["coverage_counts"]
        self.assertEqual(0, counts.get("bundled", 0))
        self.assertEqual(20, counts["existing_repo"])
        self.assertEqual(0, counts.get("implementable_todo", 0))
        self.assertEqual(10, counts["manual"])
        self.assertEqual(31, counts["quota_or_free_api"])


if __name__ == "__main__":
    unittest.main()
