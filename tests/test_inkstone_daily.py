import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

import requests


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import inkstone_daily


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=None, text=None):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error
        if text is not None:
            self.text = text
        elif payload is not None:
            self.text = json.dumps(payload, ensure_ascii=False)
        else:
            self.text = ""

    def json(self):
        if self.json_error is not None:
            raise self.json_error
        return self.payload


class FakeSession:
    def __init__(self, routes):
        self.routes = {
            key: list(value) for key, value in routes.items()
        }
        self.calls = []
        self.headers = {}
        self.trust_env = True
        self.closed = False

    def _request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        path = urlsplit(url).path
        responses = self.routes.get((method, path))
        if not responses:
            raise AssertionError("unexpected %s %s" % (method, path))
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._request("POST", url, **kwargs)

    def close(self):
        self.closed = True


class SessionFactory:
    def __init__(self, route_sets):
        self.route_sets = [dict(item) for item in route_sets]
        self.sessions = []

    def __call__(self):
        session = FakeSession(self.route_sets.pop(0))
        self.sessions.append(session)
        return session


def ok(data):
    return FakeResponse(payload={"code": 0, "msg": "success", "data": data})


def business_error(code, msg):
    return FakeResponse(payload={"code": code, "msg": msg, "data": None})


def free_package(remaining=10, total=10):
    return {
        "pkg_id": "pkg-free",
        "status": "available",
        "remaining_credits": remaining,
        "total_credits": total,
        "remark": "每月免费基础包",
    }


def success_routes(before_balance=0, after_balance=10):
    return {
        ("GET", inkstone_daily.BALANCE_PATH): [
            ok({"available_credits": before_balance}),
            ok({"available_credits": after_balance}),
        ],
        ("GET", inkstone_daily.PACKAGES_PATH): [
            ok({"total": 0, "packages": []}),
            ok({"total": 1, "packages": [free_package()]}),
        ],
        ("POST", inkstone_daily.FREE_GRANT_PATH): [
            ok({"has_received": True}),
        ],
    }


class InkstoneDailyTests(unittest.TestCase):
    def test_success_claims_then_reads_balance_and_packages(self):
        factory = SessionFactory([success_routes()])
        result = inkstone_daily.check_account(
            {
                "note": "主号",
                "token": "token-secret-one",
                "secrets": ["token-secret-one"],
            },
            base_url="https://example.test",
            session_factory=factory,
        )

        self.assertEqual("GRANTED", result["result"])
        self.assertTrue(result["ok"])
        self.assertTrue(result["granted"])
        self.assertTrue(result["claim_request_sent"])
        self.assertEqual("complete", result["phase"])
        self.assertEqual(0, result["balance_before"])
        self.assertEqual(10, result["balance_after"])
        self.assertEqual(1, result["package_delta"])
        self.assertFalse(result["free_grant_package_before"])
        self.assertTrue(result["free_grant_package_after"])
        self.assertNotIn(
            "token-secret-one",
            json.dumps(result, ensure_ascii=False),
        )

        session = factory.sessions[0]
        self.assertTrue(session.closed)
        self.assertEqual(
            ["GET", "GET", "POST", "GET", "GET"],
            [call[0] for call in session.calls],
        )
        self.assertEqual(
            "Bearer token-secret-one",
            session.calls[0][2]["headers"]["Authorization"],
        )
        self.assertIn(
            "status=all",
            urlsplit(session.calls[1][1]).query,
        )
        self.assertEqual(
            inkstone_daily.FREE_GRANT_PATH,
            urlsplit(session.calls[2][1]).path,
        )
        self.assertNotIn("json", session.calls[2][2])

    def test_already_claimed_skips_post(self):
        routes = {
            ("GET", inkstone_daily.BALANCE_PATH): [
                ok({"available_credits": 10}),
            ],
            ("GET", inkstone_daily.PACKAGES_PATH): [
                ok({"total": 1, "packages": [free_package()]}),
            ],
        }
        factory = SessionFactory([routes])
        result = inkstone_daily.check_account(
            {
                "note": "已领账号",
                "token": "token-already",
                "secrets": ["token-already"],
            },
            base_url="https://example.test",
            session_factory=factory,
        )

        self.assertEqual("ALREADY_CLAIMED", result["result"])
        self.assertTrue(result["ok"])
        self.assertTrue(result["already_claimed"])
        self.assertFalse(result["granted"])
        self.assertFalse(result["claim_request_sent"])
        self.assertEqual(
            ["GET", "GET"],
            [call[0] for call in factory.sessions[0].calls],
        )

    def test_has_received_true_confirms_claim_when_readback_shape_is_unchanged(self):
        routes = {
            ("GET", inkstone_daily.BALANCE_PATH): [
                ok({"available_credits": 0}),
                ok({"available_credits": 0}),
            ],
            ("GET", inkstone_daily.PACKAGES_PATH): [
                ok({"total": 0, "packages": []}),
                ok({"total": 0, "packages": []}),
            ],
            ("POST", inkstone_daily.FREE_GRANT_PATH): [
                ok({"has_received": True}),
            ],
        }
        factory = SessionFactory([routes])

        result = inkstone_daily.check_account(
            {
                "note": "服务端已确认",
                "token": "token-server-confirmed",
                "secrets": ["token-server-confirmed"],
            },
            base_url="https://example.test",
            session_factory=factory,
        )

        self.assertEqual("CLAIMED", result["result"])
        self.assertTrue(result["ok"])
        self.assertTrue(result["granted"])
        self.assertTrue(result["claim_request_sent"])
        self.assertEqual("readback", result["phase"])

    def test_ineligible_phone_is_classified(self):
        routes = {
            ("GET", inkstone_daily.BALANCE_PATH): [
                ok({"available_credits": 0}),
            ],
            ("GET", inkstone_daily.PACKAGES_PATH): [
                ok({"total": 0, "packages": []}),
            ],
            ("POST", inkstone_daily.FREE_GRANT_PATH): [
                business_error(-15900, "PhoneRequired"),
            ],
        }
        factory = SessionFactory([routes])
        result = inkstone_daily.check_account(
            {
                "note": "未绑手机",
                "token": "token-ineligible",
                "secrets": ["token-ineligible"],
            },
            base_url="https://example.test",
            session_factory=factory,
        )

        self.assertEqual("INELIGIBLE", result["result"])
        self.assertFalse(result["ok"])
        self.assertTrue(result["ineligible"])
        self.assertTrue(result["claim_request_sent"])
        self.assertEqual("claim", result["phase"])
        self.assertEqual(200, result["http_status"])
        self.assertNotIn(
            "token-ineligible",
            json.dumps(result, ensure_ascii=False),
        )

    def test_auth_failure_stops_before_claim(self):
        routes = {
            ("GET", inkstone_daily.BALANCE_PATH): [
                FakeResponse(
                    status_code=401,
                    payload={"msg": "expired token-secret-auth"},
                ),
            ],
        }
        factory = SessionFactory([routes])
        result = inkstone_daily.check_account(
            {
                "note": "失效账号",
                "token": "token-secret-auth",
                "secrets": ["token-secret-auth"],
            },
            base_url="https://example.test",
            session_factory=factory,
        )

        self.assertEqual("AUTH_FAILED", result["result"])
        self.assertFalse(result["ok"])
        self.assertFalse(result["claim_request_sent"])
        self.assertEqual("query", result["phase"])
        self.assertEqual(401, result["http_status"])
        self.assertNotIn(
            "token-secret-auth",
            json.dumps(result, ensure_ascii=False),
        )
        self.assertEqual(
            ["GET"],
            [call[0] for call in factory.sessions[0].calls],
        )

    def test_status_positional_and_flag_are_read_only(self):
        for argv in (["status"], ["--status"]):
            with self.subTest(argv=argv):
                routes = {
                    ("GET", inkstone_daily.BALANCE_PATH): [
                        ok({"available_credits": 10}),
                    ],
                    ("GET", inkstone_daily.PACKAGES_PATH): [
                        ok({"total": 0, "packages": []}),
                    ],
                }
                factory = SessionFactory([routes])
                output = []
                code = inkstone_daily.main(
                    argv,
                    env={
                        "INKSTONE_TOKEN": "token-status",
                        "INKSTONE_BASE_URL": "https://example.test/",
                    },
                    session_factory=factory,
                    output=output.append,
                )

                self.assertEqual(0, code)
                self.assertEqual("AVAILABLE", output[0]["result"])
                self.assertTrue(output[0]["read_only"])
                self.assertFalse(output[0]["claim_request_sent"])
                self.assertEqual("SUMMARY", output[-1]["result"])
                self.assertTrue(output[-1]["read_only"])
                self.assertEqual(0, output[-1]["claim_requests"])
                self.assertEqual(
                    ["GET", "GET"],
                    [call[0] for call in factory.sessions[0].calls],
                )

    def test_multi_account_isolation_and_output_redaction(self):
        env = {
            "INKSTONE_TOKENS": (
                "主号|uaa-token=token-one; sid=cookie-secret-one\n"
                "小号|Bearer token-two"
            ),
            "INKSTONE_BASE_URL": "https://example.test",
        }
        second_routes = {
            ("GET", inkstone_daily.BALANCE_PATH): [
                FakeResponse(status_code=403, payload={"msg": "disabled"}),
            ],
        }
        factory = SessionFactory([success_routes(), second_routes])
        output = []

        code = inkstone_daily.main(
            [],
            env=env,
            session_factory=factory,
            output=output.append,
        )

        self.assertEqual(1, code)
        self.assertEqual("GRANTED", output[0]["result"])
        self.assertEqual("AUTH_FAILED", output[1]["result"])
        self.assertEqual("SUMMARY", output[-1]["result"])
        self.assertEqual(2, output[-1]["accounts"])
        self.assertEqual(1, output[-1]["success"])
        self.assertEqual(1, output[-1]["failed"])
        self.assertEqual(1, output[-1]["granted"])
        self.assertEqual(1, output[-1]["claim_requests"])
        self.assertIsNot(factory.sessions[0], factory.sessions[1])
        self.assertTrue(all(session.closed for session in factory.sessions))

        rendered = json.dumps(output, ensure_ascii=False)
        for secret in ("token-one", "token-two", "cookie-secret-one"):
            self.assertNotIn(secret, rendered)

    def test_http_json_and_network_errors_are_classified(self):
        cases = [
            (
                FakeResponse(
                    status_code=503,
                    text="server rejected token-http",
                ),
                "HTTP_ERROR",
            ),
            (
                FakeResponse(
                    json_error=ValueError("bad json token-json"),
                ),
                "INVALID_JSON",
            ),
            (
                requests.ConnectionError("network failed token-network"),
                "NETWORK_ERROR",
            ),
        ]
        for response, expected in cases:
            with self.subTest(expected=expected):
                token = {
                    "HTTP_ERROR": "token-http",
                    "INVALID_JSON": "token-json",
                    "NETWORK_ERROR": "token-network",
                }[expected]
                factory = SessionFactory(
                    [
                        {
                            ("GET", inkstone_daily.BALANCE_PATH): [
                                response,
                            ],
                        }
                    ]
                )
                result = inkstone_daily.check_account(
                    {
                        "note": "错误账号",
                        "token": token,
                        "secrets": [token],
                    },
                    base_url="https://example.test",
                    session_factory=factory,
                )

                self.assertEqual(expected, result["result"])
                self.assertFalse(result["ok"])
                self.assertNotIn(
                    token,
                    json.dumps(result, ensure_ascii=False),
                )

    def test_cookie_parsing_and_base_url_validation(self):
        accounts = inkstone_daily.load_accounts(
            {
                "INKSTONE_TOKENS": (
                    "一号|sid=secret; uaa-token=abc.def.ghi\n"
                    "二号|Authorization: Bearer xyz=="
                )
            }
        )

        self.assertEqual("abc.def.ghi", accounts[0]["token"])
        self.assertEqual("xyz==", accounts[1]["token"])
        self.assertEqual(
            "https://discovery.intern-ai.org.cn",
            inkstone_daily.resolve_base_url({}),
        )
        self.assertEqual(
            "https://example.test",
            inkstone_daily.resolve_base_url(
                {"INKSTONE_BASE_URL": "https://example.test/"}
            ),
        )

    def test_config_error_still_ends_with_summary(self):
        output = []
        code = inkstone_daily.main(
            [],
            env={},
            session_factory=SessionFactory([]),
            output=output.append,
        )

        self.assertEqual(2, code)
        self.assertEqual("CONFIG_ERROR", output[0]["result"])
        self.assertEqual("SUMMARY", output[-1]["result"])
        self.assertEqual(1, output[-1]["failed"])


if __name__ == "__main__":
    unittest.main()
