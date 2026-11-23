import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import run_all


class RunAllTests(unittest.TestCase):
    def test_parse_last_json_uses_last_object(self):
        text = "\n".join(
            [
                "provider log",
                '{"result": "first"}',
                "more log",
                '{"result": "second", "ok": true}',
                "tail",
            ]
        )

        payload = run_all.parse_last_json(text)

        self.assertEqual({"result": "second", "ok": True}, payload)

    def test_resolve_external_script_honors_provider_root(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {"FREETOKENS_PROVIDER_ROOT": directory}
            expected = os.path.abspath(
                os.path.join(
                    directory,
                    "OfficeAce-Daily",
                    "officeace_daily.py",
                )
            )

            self.assertEqual(
                expected,
                run_all.resolve_script("officeace", env),
            )

    def test_unconfigured_provider_is_skipped(self):
        result = run_all.run_provider("meoo", env={})

        self.assertEqual("skipped", result["status"])
        self.assertEqual("NOT_CONFIGURED", result["reason"])

    def test_missing_provider_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {
                "FREETOKENS_PROVIDER_ROOT": directory,
                "CODEARTS_CREDENTIALS": "secret-value",
            }

            result = run_all.run_provider("codearts", env=env)

        self.assertEqual("skipped", result["status"])
        self.assertEqual("NOT_INSTALLED", result["reason"])

    def test_fake_provider_success_and_json_are_aggregated(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "fake_provider.py"
            script.write_text(
                "import json\n"
                "print('working')\n"
                "print(json.dumps({'result': 'CLAIMED', 'points': 7}))\n",
                encoding="utf-8",
            )
            spec = {
                "script": script.name,
                "bundled": False,
                "env_any": ("FAKE_TOKEN",),
                "status_args": None,
            }
            env = {
                "FREETOKENS_PROVIDER_ROOT": directory,
                "FAKE_TOKEN": "super-secret-token",
            }
            with mock.patch.dict(run_all.PROVIDERS, {"fake": spec}):
                result = run_all.run_provider("fake", env=env)

        self.assertEqual("success", result["status"])
        self.assertEqual(0, result["exit_code"])
        self.assertEqual("CLAIMED", result["result"]["result"])

    def test_status_unsupported_is_skipped_without_running_script(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "fake_provider.py"
            marker = Path(directory) / "ran.txt"
            script.write_text(
                "from pathlib import Path\n"
                "Path(%r).write_text('ran', encoding='utf-8')\n"
                % str(marker),
                encoding="utf-8",
            )
            spec = {
                "script": script.name,
                "bundled": False,
                "env_any": ("FAKE_TOKEN",),
                "status_args": None,
            }
            env = {
                "FREETOKENS_PROVIDER_ROOT": directory,
                "FAKE_TOKEN": "secret",
            }
            with mock.patch.dict(run_all.PROVIDERS, {"fake": spec}):
                result = run_all.run_provider("fake", status=True, env=env)

            self.assertFalse(marker.exists())

        self.assertEqual("skipped", result["status"])
        self.assertEqual("STATUS_UNSUPPORTED", result["reason"])

    def test_redact_removes_secret_environment_values(self):
        env = {
            "MY_TOKEN": "token-value-123",
            "NORMAL_VALUE": "visible",
        }

        output = run_all.redact(
            "failure token-value-123 visible",
            env,
        )

        self.assertNotIn("token-value-123", output)
        self.assertIn("[REDACTED]", output)
        self.assertIn("visible", output)

    def test_summary_counts_success_failure_and_skipped(self):
        summary = run_all.build_summary(
            [
                {"status": "success"},
                {"status": "failed"},
                {"status": "skipped"},
            ],
            "claim",
        )

        self.assertEqual("failed", summary["status"])
        self.assertEqual(1, summary["success"])
        self.assertEqual(1, summary["failed"])
        self.assertEqual(1, summary["skipped"])

    def test_list_output_is_valid_json(self):
        import contextlib
        import io

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = run_all.main(["--list"])

        self.assertEqual(0, code)
        names = json.loads(output.getvalue())
        self.assertIn("minimax", names)
        self.assertIn("mobileclaw", names)
        self.assertIn("inkstone", names)

    def test_every_bundled_provider_script_exists(self):
        for name, spec in run_all.PROVIDERS.items():
            if spec["bundled"]:
                with self.subTest(provider=name):
                    self.assertTrue(run_all.resolve_script(name).endswith(
                        os.path.normpath(spec["script"])
                    ))
                    self.assertTrue(os.path.isfile(run_all.resolve_script(name)))


if __name__ == "__main__":
    unittest.main()
