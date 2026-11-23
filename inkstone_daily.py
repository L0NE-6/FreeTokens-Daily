#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claim the monthly free Inkstone ink credits for one or more accounts.

Protocol references:
    magpie-community/plugins@087c36123dc01f6035acbf371647da192a292eda
        packages/inkstone/lib/protocol.mjs L212-L216
    magpie-community/plugins@73d1f898221c4300f3b677076f8936eafc892272
        packages/inkstone/index.mjs L690-L705

The console accepts the browser uaa-token cookie value as a Bearer token for
the tokenplan credit APIs. A pasted full cookie is reduced to that value.

Environment:
    INKSTONE_TOKENS
        One account per line: ``note|uaa-token`` or a bare token/cookie.
    INKSTONE_TOKEN
        Single account credential. INKSTONE_TOKENS takes precedence.
    INKSTONE_BASE_URL
        Optional console origin override. The default is the console origin
        used by the upstream protocol.

Modes:
    claim   Read balance/packages, claim only when the current monthly free
            package is absent, then re-read balance/packages.
    status  Read balance/packages only. This mode never POSTs or claims.

Every account emits one compact JSON line. The final line is a SUMMARY JSON
object, which is the line consumed by run_all.py.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Optional, Sequence
from urllib.parse import unquote, urlencode, urlsplit, urlunsplit

import requests


PROVIDER = "inkstone"
DEFAULT_BASE_URL = "https://discovery.intern-ai.org.cn"
BASE_URL_ENV = "INKSTONE_BASE_URL"
TOKENS_ENV = "INKSTONE_TOKENS"
TOKEN_ENV = "INKSTONE_TOKEN"

BALANCE_PATH = "/api/tokenplan/v1/credits/balance"
PACKAGES_PATH = "/api/tokenplan/v1/credits/packages"
FREE_GRANT_PATH = "/api/tokenplan/v1/users/free-grant"
PACKAGES_QUERY = (
    ("status", "all"),
    ("page", "1"),
    ("page_size", "50"),
)

REQUEST_TIMEOUT = 20
INELIGIBLE_CODE = -15900
AUTH_BUSINESS_CODES = {-10001, -10002, 401, 403}
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/152.0.0.0 Safari/537.36"
)
BASE_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "zh-CN",
    "User-Agent": USER_AGENT,
    "sec-ch-ua": '"Chromium";v="152", "Not;A=Brand";v="24", "Google Chrome";v="152"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


class ConfigError(ValueError):
    """Configuration or credential input error."""


class APIError(RuntimeError):
    """A classified request or response failure."""

    def __init__(
        self,
        result: str,
        message: str,
        *,
        http_status: Optional[int] = None,
        business_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.result = result
        self.message = message
        self.http_status = http_status
        self.business_code = business_code


@dataclass(frozen=True)
class BalanceSnapshot:
    available_credits: Optional[float]
    active_package_count: Optional[int]
    http_status: int


@dataclass(frozen=True)
class PackagesSnapshot:
    items: tuple[Mapping[str, Any], ...]
    total: Optional[int]
    free_grant_present: bool
    http_status: int


def emit(payload: Mapping[str, Any]) -> None:
    """Print one compact JSON line."""
    print(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str),
        flush=True,
    )


def _redact(value: Any, secrets: Sequence[str]) -> str:
    text = str(value)
    unique = []
    for secret in secrets:
        secret = str(secret or "")
        if secret and secret not in unique:
            unique.append(secret)
    for secret in sorted(unique, key=len, reverse=True):
        text = text.replace(secret, "[REDACTED]")
    return text


def _mask_identity(value: Any) -> str:
    text = str(value or "").strip()
    if re.fullmatch(r"\d{11}", text):
        return "%s****%s" % (text[:3], text[-4:])
    if re.fullmatch(r"[^@\s]+@[^@\s]+", text):
        local, domain = text.split("@", 1)
        return "%s***@%s" % (local[:1], domain)
    return text


def _cookie_secret_parts(raw: str) -> list[str]:
    parts = []
    for part in str(raw or "").split(";"):
        part = part.strip()
        if not part:
            continue
        parts.append(part)
        if "=" in part:
            parts.append(part.split("=", 1)[1].strip())
    return parts


def _credential_secrets(raw: str, token: str) -> list[str]:
    secrets = [
        str(raw or ""),
        str(token or ""),
        "Bearer " + str(token or ""),
        "uaa-token=" + str(token or ""),
        "uaa-token: " + str(token or ""),
    ]
    secrets.extend(_cookie_secret_parts(raw))
    return [item for item in secrets if item]


def parse_uaa_token(raw: str) -> str:
    """Extract the uaa-token value from a cookie, header, or bare token."""
    text = str(raw or "").strip()
    if not text:
        raise ConfigError("credential is empty")
    text = text.strip("\"'`").strip()
    if not text:
        raise ConfigError("credential is empty")

    lowered = text.lower()
    if lowered.startswith("cookie:"):
        text = text.split(":", 1)[1].strip()
        lowered = text.lower()
    if lowered.startswith("authorization:"):
        text = text.split(":", 1)[1].strip()
        lowered = text.lower()

    match = re.search(
        r"(?:^|;)\s*uaa-token\s*=\s*([^;]*)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        token = unquote(match.group(1).strip().strip("\"'`"))
        if not token:
            raise ConfigError("uaa-token cookie value is empty")
        return token

    if ";" in text:
        raise ConfigError("cookie input does not contain uaa-token")

    if lowered.startswith("bearer "):
        text = text[7:].strip()

    if not text:
        raise ConfigError("bearer token is empty")
    if text.lower() == "uaa-token":
        raise ConfigError("credential is the cookie name, not its value")
    if re.search(r"\s", text):
        raise ConfigError("credential contains whitespace")
    if re.search(r"=[^=]", text):
        raise ConfigError("cookie input does not contain uaa-token")
    return text


def load_accounts(
    env: Optional[Mapping[str, str]] = None,
) -> list[dict[str, Any]]:
    """Load multi-account or single-account credentials without logging them."""
    values = os.environ if env is None else env
    multi = str(values.get(TOKENS_ENV, "") or "").strip()
    if multi:
        lines = [line.strip() for line in multi.splitlines() if line.strip()]
        if not lines:
            raise ConfigError("%s contains no accounts" % TOKENS_ENV)

        accounts: list[dict[str, Any]] = []
        for index, line in enumerate(lines, 1):
            note = "account_%d" % index
            raw = line
            if "|" in line:
                note_part, raw_part = line.split("|", 1)
                note = note_part.strip() or note
                raw = raw_part.strip()
            try:
                token = parse_uaa_token(raw)
            except ConfigError as exc:
                raise ConfigError(
                    "%s line %d: %s" % (TOKENS_ENV, index, exc)
                ) from exc
            accounts.append(
                {
                    "note": note,
                    "token": token,
                    "secrets": _credential_secrets(raw, token),
                }
            )
        return accounts

    single = str(values.get(TOKEN_ENV, "") or "").strip()
    if single:
        token = parse_uaa_token(single)
        return [
            {
                "note": "默认账号",
                "token": token,
                "secrets": _credential_secrets(single, token),
            }
        ]
    raise ConfigError("set %s or %s" % (TOKENS_ENV, TOKEN_ENV))


def _normalize_base_url(base_url: str) -> str:
    text = str(base_url or "").strip().rstrip("/")
    parsed = urlsplit(text)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ConfigError("%s must be an http(s) URL" % BASE_URL_ENV)
    if parsed.username or parsed.password:
        raise ConfigError("%s must not contain credentials" % BASE_URL_ENV)
    if parsed.query or parsed.fragment:
        raise ConfigError("%s must not contain a query or fragment" % BASE_URL_ENV)
    path = parsed.path.rstrip("/")
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def resolve_base_url(env: Optional[Mapping[str, str]] = None) -> str:
    values = os.environ if env is None else env
    configured = str(values.get(BASE_URL_ENV, "") or "").strip()
    return _normalize_base_url(configured or DEFAULT_BASE_URL)


def _origin(base_url: str) -> str:
    parsed = urlsplit(base_url)
    return "%s://%s" % (parsed.scheme, parsed.netloc)


def _auth_headers(
    account: Mapping[str, Any],
    base_url: str,
) -> dict[str, str]:
    token = str(account.get("token", "") or "").strip()
    if not token:
        raise ConfigError("account token is empty")
    origin = _origin(base_url)
    headers = dict(BASE_HEADERS)
    headers.update(
        {
            "Authorization": "Bearer " + token,
            "Origin": origin,
            "Referer": origin + "/token-plan/home",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
        }
    )
    return headers


def make_session() -> requests.Session:
    """Create an isolated session for one account."""
    session = requests.Session()
    session.trust_env = False
    session.headers.update(BASE_HEADERS)
    return session


def _optional_number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    if number.is_integer():
        return int(number)
    return number


def _optional_int(value: Any) -> Optional[int]:
    number = _optional_number(value)
    if number is None:
        return None
    return int(number)


def _format_number(value: Optional[float]) -> str:
    if value is None:
        return "未返回"
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return ("%.6f" % number).rstrip("0").rstrip(".")


def _package_count(snapshot: Optional[PackagesSnapshot]) -> Optional[int]:
    if snapshot is None:
        return None
    if snapshot.total is not None:
        return snapshot.total
    return len(snapshot.items)


def _balance_delta(
    before: Optional[BalanceSnapshot],
    after: Optional[BalanceSnapshot],
) -> Optional[float]:
    if (
        before is None
        or after is None
        or before.available_credits is None
        or after.available_credits is None
    ):
        return None
    return round(
        float(after.available_credits) - float(before.available_credits),
        6,
    )


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        if number <= 0:
            return None
        seconds = number / 1000 if number > 1_000_000_000_000 else number
        try:
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        return _parse_datetime(float(text))
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _package_is_free_grant(package: Mapping[str, Any]) -> bool:
    status = str(package.get("status", "") or "").strip().lower()
    if status in {"expired", "disabled", "deleted", "invalid", "revoked"}:
        return False

    cycle = package.get("current_cycle")
    if isinstance(cycle, Mapping):
        end_at = _parse_datetime(cycle.get("end_at"))
        if end_at is not None and end_at < datetime.now(timezone.utc):
            return False

    remark = " ".join(
        str(package.get(key, "") or "")
        for key in ("remark", "remark_en", "name", "title")
    ).strip()
    lowered = remark.lower()
    free_word = "免费" in remark or "free" in lowered
    monthly_word = (
        "每月" in remark
        or "基础包" in remark
        or "monthly" in lowered
        or "base package" in lowered
    )
    if free_word and monthly_word:
        return True

    identity = " ".join(
        str(package.get(key, "") or "")
        for key in ("pkg_id", "id", "code")
    ).lower()
    return "free" in identity and ("month" in identity or "grant" in identity)


def _payload_message(payload: Any) -> str:
    if not isinstance(payload, Mapping):
        return ""
    for key in ("msg", "message", "detail", "errorMessage", "error"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            nested = _payload_message(value)
            if nested:
                return nested
        elif value not in (None, "", False):
            return str(value)
    return ""


def _business_code(payload: Any) -> Optional[int]:
    if not isinstance(payload, Mapping):
        return None
    for key in ("code", "errno", "errorCode", "error_code"):
        value = payload.get(key)
        if value in (None, "", False):
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    error = payload.get("error")
    if isinstance(error, Mapping):
        return _business_code(error)
    return None


def _looks_ineligible(message: str) -> bool:
    lowered = str(message or "").lower()
    return any(
        marker in lowered
        for marker in (
            "phonerequired",
            "phone required",
            "bind a phone",
            "绑定手机",
            "未绑定手机",
            "手机号",
        )
    )


def _looks_auth_failure(message: str) -> bool:
    lowered = str(message or "").lower()
    return any(
        marker in lowered
        for marker in (
            "not authenticated",
            "unauthorized",
            "token expired",
            "session expired",
            "request is not authenticated",
            "未认证",
            "鉴权失败",
            "登录已过期",
        )
    )


def _response_text(response: Any) -> str:
    text = getattr(response, "text", "")
    if text:
        return str(text)
    try:
        payload = response.json()
    except Exception:
        return ""
    return json.dumps(payload, ensure_ascii=False, default=str)


def _response_status(response: Any) -> int:
    try:
        return int(getattr(response, "status_code", 0) or 0)
    except (TypeError, ValueError):
        return 0


def _api_url(
    base_url: str,
    path: str,
    query: Optional[Sequence[tuple[str, str]]] = None,
) -> str:
    url = base_url + path
    if query:
        url += "?" + urlencode(list(query))
    return url


def _request_json(
    session: Any,
    method: str,
    url: str,
    *,
    headers: Mapping[str, str],
    secrets: Sequence[str],
) -> tuple[Mapping[str, Any], int]:
    try:
        if method == "GET":
            response = session.get(
                url,
                headers=dict(headers),
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
        elif method == "POST":
            response = session.post(
                url,
                headers=dict(headers),
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
        else:
            raise ValueError("unsupported method: %s" % method)
    except requests.RequestException as exc:
        raise APIError(
            "NETWORK_ERROR",
            "network request failed: %s" % _redact(exc, secrets),
        ) from exc
    except Exception as exc:
        raise APIError(
            "NETWORK_ERROR",
            "network request failed: %s" % _redact(exc, secrets),
        ) from exc

    status_code = _response_status(response)
    if status_code in (401, 403):
        raise APIError(
            "AUTH_FAILED",
            "credential is invalid or expired (HTTP %d)" % status_code,
            http_status=status_code,
        )
    if 300 <= status_code < 400:
        raise APIError(
            "HTTP_ERROR",
            "request was redirected (HTTP %d)" % status_code,
            http_status=status_code,
        )
    if status_code == 429:
        raise APIError(
            "HTTP_ERROR",
            "request was rate limited (HTTP %d)" % status_code,
            http_status=status_code,
        )
    if not 200 <= status_code < 300:
        detail = _redact(_response_text(response), secrets)
        message = "API request failed (HTTP %d)" % status_code
        if detail:
            message += ": " + detail[:240]
        raise APIError(
            "HTTP_ERROR",
            message,
            http_status=status_code,
        )

    try:
        payload = response.json()
    except Exception as exc:
        raise APIError(
            "INVALID_JSON",
            "API response is not JSON: %s" % _redact(exc, secrets),
            http_status=status_code,
        ) from exc
    if not isinstance(payload, Mapping):
        raise APIError(
            "INVALID_RESPONSE",
            "API response JSON is not an object",
            http_status=status_code,
        )

    code = _business_code(payload)
    message = _payload_message(payload)
    if code not in (None, 0):
        if code == INELIGIBLE_CODE or _looks_ineligible(message):
            raise APIError(
                "INELIGIBLE",
                "phone number is not bound to this account",
                http_status=status_code,
                business_code=code,
            )
        if code in AUTH_BUSINESS_CODES or _looks_auth_failure(message):
            raise APIError(
                "AUTH_FAILED",
                "authentication failed: %s"
                % (_redact(message, secrets) or "code %s" % code),
                http_status=status_code,
                business_code=code,
            )
        raise APIError(
            "BUSINESS_ERROR",
            _redact(message, secrets) or "business request failed (code %s)" % code,
            http_status=status_code,
            business_code=code,
        )

    if payload.get("success") is False:
        if _looks_ineligible(message):
            raise APIError(
                "INELIGIBLE",
                "phone number is not bound to this account",
                http_status=status_code,
                business_code=code,
            )
        if _looks_auth_failure(message):
            raise APIError(
                "AUTH_FAILED",
                "authentication failed: %s" % _redact(message, secrets),
                http_status=status_code,
                business_code=code,
            )
        raise APIError(
            "BUSINESS_ERROR",
            _redact(message, secrets) or "business request failed",
            http_status=status_code,
            business_code=code,
        )

    return payload, status_code


def parse_balance(
    payload: Mapping[str, Any],
    http_status: int = 0,
) -> BalanceSnapshot:
    data = payload.get("data")
    if not isinstance(data, Mapping):
        raise APIError(
            "INVALID_RESPONSE",
            "balance response is missing a data object",
            http_status=http_status,
        )
    return BalanceSnapshot(
        available_credits=_optional_number(data.get("available_credits")),
        active_package_count=_optional_int(data.get("active_package_count")),
        http_status=http_status,
    )


def parse_packages(
    payload: Mapping[str, Any],
    http_status: int = 0,
) -> PackagesSnapshot:
    data = payload.get("data")
    if isinstance(data, Mapping):
        raw_items = data.get("packages")
        if raw_items is None:
            raw_items = data.get("items")
        if raw_items is None:
            raw_items = []
        total = _optional_int(data.get("total"))
    elif isinstance(data, list):
        raw_items = data
        total = len(data)
    else:
        raise APIError(
            "INVALID_RESPONSE",
            "packages response is missing data",
            http_status=http_status,
        )
    if not isinstance(raw_items, list):
        raise APIError(
            "INVALID_RESPONSE",
            "packages response data is not a list",
            http_status=http_status,
        )

    items = tuple(item for item in raw_items if isinstance(item, Mapping))
    return PackagesSnapshot(
        items=items,
        total=total,
        free_grant_present=any(_package_is_free_grant(item) for item in items),
        http_status=http_status,
    )


def _read_balance(
    session: Any,
    base_url: str,
    headers: Mapping[str, str],
    secrets: Sequence[str],
) -> BalanceSnapshot:
    payload, status_code = _request_json(
        session,
        "GET",
        _api_url(base_url, BALANCE_PATH),
        headers=headers,
        secrets=secrets,
    )
    return parse_balance(payload, status_code)


def _read_packages(
    session: Any,
    base_url: str,
    headers: Mapping[str, str],
    secrets: Sequence[str],
) -> PackagesSnapshot:
    payload, status_code = _request_json(
        session,
        "GET",
        _api_url(base_url, PACKAGES_PATH, PACKAGES_QUERY),
        headers=headers,
        secrets=secrets,
    )
    return parse_packages(payload, status_code)


def _read_snapshots(
    session: Any,
    base_url: str,
    headers: Mapping[str, str],
    secrets: Sequence[str],
) -> tuple[BalanceSnapshot, PackagesSnapshot]:
    balance = _read_balance(session, base_url, headers, secrets)
    packages = _read_packages(session, base_url, headers, secrets)
    return balance, packages


def _claim_has_received(payload: Mapping[str, Any]) -> Optional[bool]:
    data = payload.get("data")
    if not isinstance(data, Mapping):
        return None
    value = data.get("has_received")
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    return None


def _snapshot_message(
    balance: Optional[BalanceSnapshot],
    packages: Optional[PackagesSnapshot],
) -> str:
    available = None if balance is None else balance.available_credits
    count = _package_count(packages)
    if count is None:
        count = 0
    return "余额 %s，墨点包 %d 个" % (_format_number(available), count)


def _result(
    account: Mapping[str, Any],
    mode: str,
    result: str,
    ok: bool,
    message: str,
    *,
    phase: str,
    http_status: Optional[int] = None,
    claim_request_sent: bool = False,
    claimable: Optional[bool] = None,
    granted: bool = False,
    already_claimed: bool = False,
    ineligible: bool = False,
    before_balance: Optional[BalanceSnapshot] = None,
    before_packages: Optional[PackagesSnapshot] = None,
    after_balance: Optional[BalanceSnapshot] = None,
    after_packages: Optional[PackagesSnapshot] = None,
    error_kind: str = "",
) -> dict[str, Any]:
    before_count = _package_count(before_packages)
    after_count = _package_count(after_packages)
    delta = _balance_delta(before_balance, after_balance)
    before_credits = (
        None if before_balance is None else before_balance.available_credits
    )
    after_credits = (
        None if after_balance is None else after_balance.available_credits
    )
    secrets = [str(item) for item in account.get("secrets", []) if item]
    return {
        "account": _mask_identity(account.get("note", "")),
        "provider": PROVIDER,
        "mode": mode,
        "result": result,
        "ok": ok,
        "message": _redact(message, secrets),
        "phase": phase,
        "http_status": http_status,
        "read_only": mode == "status",
        "query_side_effect": False,
        "claim_side_effect": True,
        "claim_request_sent": claim_request_sent,
        "side_effect": FREE_GRANT_PATH if claim_request_sent else "none",
        "claimable": claimable,
        "granted": granted,
        "claimed": granted,
        "already_claimed": already_claimed,
        "ineligible": ineligible,
        "balance_before": before_credits,
        "balance_after": after_credits,
        "balance_delta": delta,
        "credits": after_credits if after_credits is not None else before_credits,
        "packages_before": before_count,
        "packages_after": after_count,
        "package_delta": (
            None
            if before_count is None or after_count is None
            else after_count - before_count
        ),
        "free_grant_package_before": (
            None
            if before_packages is None
            else before_packages.free_grant_present
        ),
        "free_grant_package_after": (
            None
            if after_packages is None
            else after_packages.free_grant_present
        ),
        "error_kind": error_kind,
    }


def _normalize_mode(mode: str) -> str:
    normalized = str(mode or "claim").strip().lower()
    if normalized not in ("claim", "status"):
        raise ConfigError("mode must be claim or status")
    return normalized


def check_account(
    account: Mapping[str, Any],
    *,
    mode: str = "claim",
    base_url: Optional[str] = None,
    session_factory: Callable[[], Any] = make_session,
) -> dict[str, Any]:
    """Process one account. One account's failure never stops the next."""
    try:
        resolved_mode = _normalize_mode(mode)
    except ConfigError as exc:
        return _result(
            account,
            str(mode or ""),
            "CONFIG_ERROR",
            False,
            str(exc),
            phase="config",
            error_kind="CONFIG",
        )

    try:
        resolved_base_url = _normalize_base_url(
            base_url or resolve_base_url()
        )
        headers = _auth_headers(account, resolved_base_url)
    except ConfigError as exc:
        return _result(
            account,
            resolved_mode,
            "CONFIG_ERROR",
            False,
            str(exc),
            phase="config",
            error_kind="CONFIG",
        )

    secrets = [str(item) for item in account.get("secrets", []) if item]
    session = None
    phase = "query"
    claim_request_sent = False
    before_balance: Optional[BalanceSnapshot] = None
    before_packages: Optional[PackagesSnapshot] = None
    after_balance: Optional[BalanceSnapshot] = None
    after_packages: Optional[PackagesSnapshot] = None

    try:
        try:
            session = session_factory()
        except Exception as exc:
            return _result(
                account,
                resolved_mode,
                "SESSION_ERROR",
                False,
                "session creation failed: %s" % _redact(exc, secrets),
                phase="query",
                error_kind="SESSION",
            )

        if hasattr(session, "trust_env"):
            session.trust_env = False
        if hasattr(session, "headers"):
            session.headers.update(BASE_HEADERS)

        before_balance, before_packages = _read_snapshots(
            session,
            resolved_base_url,
            headers,
            secrets,
        )

        if resolved_mode == "status":
            available = not before_packages.free_grant_present
            if available:
                result = "AVAILABLE"
                message = "本月免费墨点可领取；" + _snapshot_message(
                    before_balance,
                    before_packages,
                )
            else:
                result = "ALREADY_CLAIMED"
                message = "本月免费墨点已领取；" + _snapshot_message(
                    before_balance,
                    before_packages,
                )
            return _result(
                account,
                resolved_mode,
                result,
                True,
                message,
                phase="complete",
                http_status=before_packages.http_status,
                claim_request_sent=False,
                claimable=available,
                already_claimed=not available,
                before_balance=before_balance,
                before_packages=before_packages,
                after_balance=before_balance,
                after_packages=before_packages,
            )

        if before_packages.free_grant_present:
            return _result(
                account,
                resolved_mode,
                "ALREADY_CLAIMED",
                True,
                "本月免费墨点已领取；" + _snapshot_message(
                    before_balance,
                    before_packages,
                ),
                phase="complete",
                http_status=before_packages.http_status,
                claim_request_sent=False,
                claimable=False,
                already_claimed=True,
                before_balance=before_balance,
                before_packages=before_packages,
                after_balance=before_balance,
                after_packages=before_packages,
            )

        claim_request_sent = True
        phase = "claim"
        claim_payload, claim_status = _request_json(
            session,
            "POST",
            _api_url(resolved_base_url, FREE_GRANT_PATH),
            headers=headers,
            secrets=secrets,
        )
        has_received = _claim_has_received(claim_payload)

        phase = "readback"
        after_balance, after_packages = _read_snapshots(
            session,
            resolved_base_url,
            headers,
            secrets,
        )
        delta = _balance_delta(before_balance, after_balance)
        new_free_package = (
            after_packages.free_grant_present
            and not before_packages.free_grant_present
        )
        readback_changed = new_free_package or (
            delta is not None and delta > 0
        )

        if readback_changed:
            message = (
                "本月免费墨点到账；余额 %s -> %s，墨点包 %d -> %d"
                % (
                    _format_number(before_balance.available_credits),
                    _format_number(after_balance.available_credits),
                    _package_count(before_packages) or 0,
                    _package_count(after_packages) or 0,
                )
            )
            return _result(
                account,
                resolved_mode,
                "GRANTED",
                True,
                message,
                phase="complete",
                http_status=after_packages.http_status or claim_status,
                claim_request_sent=True,
                claimable=True,
                granted=True,
                before_balance=before_balance,
                before_packages=before_packages,
                after_balance=after_balance,
                after_packages=after_packages,
            )

        if has_received is True:
            message = (
                "服务端 free-grant 返回 has_received=true；"
                "余额和墨点包未观察到新增，按服务端领取状态确认；"
                + _snapshot_message(after_balance, after_packages)
            )
            return _result(
                account,
                resolved_mode,
                "CLAIMED",
                True,
                message,
                phase="readback",
                http_status=after_packages.http_status or claim_status,
                claim_request_sent=True,
                claimable=True,
                granted=True,
                before_balance=before_balance,
                before_packages=before_packages,
                after_balance=after_balance,
                after_packages=after_packages,
            )

        if has_received is False:
            return _result(
                account,
                resolved_mode,
                "CLAIM_NOT_APPLIED",
                False,
                "领取接口返回 has_received=false；"
                + _snapshot_message(after_balance, after_packages),
                phase="readback",
                http_status=after_packages.http_status or claim_status,
                claim_request_sent=True,
                claimable=True,
                before_balance=before_balance,
                before_packages=before_packages,
                after_balance=after_balance,
                after_packages=after_packages,
                error_kind="CLAIM_NOT_APPLIED",
            )

        return _result(
            account,
            resolved_mode,
            "READBACK_UNCONFIRMED",
            False,
            "领取接口已返回，但余额和墨点包没有可确认的变化；"
            + _snapshot_message(after_balance, after_packages),
            phase="readback",
            http_status=after_packages.http_status or claim_status,
            claim_request_sent=True,
            claimable=True,
            before_balance=before_balance,
            before_packages=before_packages,
            after_balance=after_balance,
            after_packages=after_packages,
            error_kind="READBACK_UNCONFIRMED",
        )
    except APIError as exc:
        if phase == "readback" and claim_request_sent:
            message = "领取请求已发送，但回读失败：%s" % exc.message
            error_kind = "READBACK_" + exc.result
        elif phase == "claim" and claim_request_sent:
            message = "领取请求失败：%s" % exc.message
            error_kind = "CLAIM_" + exc.result
        else:
            message = exc.message
            error_kind = exc.result
        return _result(
            account,
            resolved_mode,
            exc.result,
            False,
            message,
            phase=phase,
            http_status=exc.http_status,
            claim_request_sent=claim_request_sent,
            ineligible=exc.result == "INELIGIBLE",
            before_balance=before_balance,
            before_packages=before_packages,
            after_balance=after_balance,
            after_packages=after_packages,
            error_kind=error_kind,
        )
    except ConfigError as exc:
        return _result(
            account,
            resolved_mode,
            "CONFIG_ERROR",
            False,
            str(exc),
            phase=phase,
            claim_request_sent=claim_request_sent,
            before_balance=before_balance,
            before_packages=before_packages,
            after_balance=after_balance,
            after_packages=after_packages,
            error_kind="CONFIG",
        )
    except Exception as exc:
        return _result(
            account,
            resolved_mode,
            "UNEXPECTED_ERROR",
            False,
            "unexpected error: %s" % _redact(exc, secrets),
            phase=phase,
            claim_request_sent=claim_request_sent,
            before_balance=before_balance,
            before_packages=before_packages,
            after_balance=after_balance,
            after_packages=after_packages,
            error_kind="UNEXPECTED",
        )
    finally:
        close = getattr(session, "close", None)
        if callable(close):
            close()


def run_accounts(
    accounts: Sequence[Mapping[str, Any]],
    *,
    mode: str = "claim",
    base_url: Optional[str] = None,
    session_factory: Callable[[], Any] = make_session,
    output: Callable[[Mapping[str, Any]], None] = emit,
) -> list[dict[str, Any]]:
    """Process every account independently and print one JSON line each."""
    resolved_mode = _normalize_mode(mode)
    resolved_base_url = _normalize_base_url(base_url or resolve_base_url())
    results = []
    for account in accounts:
        result = check_account(
            account,
            mode=resolved_mode,
            base_url=resolved_base_url,
            session_factory=session_factory,
        )
        results.append(result)
        output(result)
    return results


def build_summary(
    results: Sequence[Mapping[str, Any]],
    mode: str = "claim",
) -> dict[str, Any]:
    resolved_mode = _normalize_mode(mode)
    total = len(results)
    success = sum(1 for item in results if item.get("ok") is True)
    failed = total - success
    granted = sum(1 for item in results if item.get("granted") is True)
    already = sum(
        1 for item in results if item.get("already_claimed") is True
    )
    ineligible = sum(1 for item in results if item.get("ineligible") is True)
    available = sum(
        1 for item in results if item.get("result") == "AVAILABLE"
    )
    claim_requests = sum(
        1 for item in results if item.get("claim_request_sent") is True
    )
    return {
        "provider": PROVIDER,
        "result": "SUMMARY",
        "status": "success" if failed == 0 and total > 0 else "failed",
        "ok": failed == 0 and total > 0,
        "mode": resolved_mode,
        "read_only": resolved_mode == "status",
        "query_side_effect": False,
        "claim_side_effect": True,
        "claim_requests": claim_requests,
        "side_effect": FREE_GRANT_PATH if claim_requests else "none",
        "accounts": total,
        "total": total,
        "success": success,
        "failed": failed,
        "granted": granted,
        "already_granted": already,
        "available": available,
        "ineligible": ineligible,
        "results": [dict(item) for item in results],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Claim the monthly free Inkstone ink credits. "
            "status mode is read-only."
        )
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="read balance and packages without claiming",
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=("status",),
        help=argparse.SUPPRESS,
    )
    return parser


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    env: Optional[Mapping[str, str]] = None,
    session_factory: Callable[[], Any] = make_session,
    output: Callable[[Mapping[str, Any]], None] = emit,
) -> int:
    args = build_parser().parse_args(argv)
    mode = "status" if args.status or args.action == "status" else "claim"
    try:
        accounts = load_accounts(env)
        base_url = resolve_base_url(env)
    except ConfigError as exc:
        result = _result(
            {"note": "config", "secrets": []},
            mode,
            "CONFIG_ERROR",
            False,
            str(exc),
            phase="config",
            error_kind="CONFIG",
        )
        summary = build_summary([result], mode)
        output(result)
        output(summary)
        return 2

    results = run_accounts(
        accounts,
        mode=mode,
        base_url=base_url,
        session_factory=session_factory,
        output=output,
    )
    summary = build_summary(results, mode)
    output(summary)
    return 0 if summary["failed"] == 0 else 1


def _configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    _configure_utf8_stdio()
    sys.exit(main())
