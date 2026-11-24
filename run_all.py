#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run locally installed FreeTokens provider repositories.

This repository is an index and scheduler. Every provider script lives in its
own L0NE-6 repository. Missing provider checkouts and unconfigured accounts
are reported as skipped instead of being counted as failures.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import time
from typing import Any, Mapping, Optional, Sequence


ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PROVIDER_ROOT = os.path.dirname(ROOT)
DEFAULT_TIMEOUT = 300

PROVIDERS: dict[str, dict[str, Any]] = {
    "minimax": {
        "script": "MiniMax-Daily/minimax_daily.py",
        "bundled": False,
        "env_any": ("MINIMAX_OAUTH_AUTH_FILE", "MINIMAX_LS_LEVELDB"),
        "credential_globs": (
            "~/.minimax/auth/*/*/*/auth.json",
            "~/Library/Application Support/MiniMax/Local Storage/leveldb/*.log",
            "~/Library/Application Support/MiniMax/Local Storage/leveldb/*.ldb",
        ),
        "status_args": ("status",),
    },
    "meoo": {
        "script": "Meoo-Daily/meoo_daily.py",
        "bundled": False,
        "env_any": ("MEOO_COOKIES", "MEOO_COOKIE"),
        "status_args": ("status",),
    },
    "mobileclaw": {
        "script": "MobileClaw-Daily/mobileclaw_daily.py",
        "bundled": False,
        "env_any": ("MOBILECLAW_TOKENS", "MOBILECLAW_TOKEN"),
        "status_args": ("status",),
    },
    "inkstone": {
        "script": "Inkstone-Daily/inkstone_daily.py",
        "bundled": False,
        "env_any": ("INKSTONE_TOKENS", "INKSTONE_TOKEN"),
        "status_args": ("status",),
    },
    "officeace": {
        "script": "OfficeAce-Daily/officeace_daily.py",
        "bundled": False,
        "env_any": ("OFFICEACE_TOKENS", "OFFICEACE_AK"),
        "status_args": ("--query",),
    },
    "codearts": {
        "script": "CodeArts-Daily/codearts_daily.py",
        "bundled": False,
        "env_any": ("CODEARTS_CREDENTIALS",),
        "status_args": ("--preview",),
    },
    "modelscope": {
        "script": "ModelScope-Daily/modelscope_daily.py",
        "bundled": False,
        "env_any": (
            "MODELSCOPE_CN_TOKENS",
            "MODELSCOPE_INTL_TOKENS",
            "MODELSCOPE_CN_TOKEN",
            "MODELSCOPE_INTL_TOKEN",
        ),
        "status_args": ("--query",),
    },
    "astudio": {
        "script": "AStudio-Daily/astudio_daily.py",
        "bundled": False,
        "env_any": ("ASTUDIO_COOKIES", "ASTUDIO_ACCOUNT_FILE"),
        "status_args": ("--query",),
    },
    "qoder": {
        "script": "Qoder-Daily/qoder_daily.py",
        "bundled": False,
        "env_any": ("QODER_TOKENS", "QODER_GLOBAL_TOKENS"),
        "status_args": None,
    },
    "trae": {
        "script": "Trae-AutoCheckin/trae_checkin.py",
        "bundled": False,
        "env_any": (
            "TRAE_ACCOUNTS",
            "TRAE_REFRESH_TOKEN",
            "TRAE_ACCESS_TOKEN",
            "TRAE_STORAGE_PATH",
        ),
        "status_args": None,
    },
    "autoclaw": {
        "script": "AutoClaw-Daily/autoclaw_cn_daily.py",
        "bundled": False,
        "env_any": ("AUTOCLAW_CN_TOKENS",),
        "status_args": None,
    },
    "zcode": {
        "script": "ZCode-Daily/zcode_cn_daily.py",
        "bundled": False,
        "env_any": ("ZCODE_CN_TOKENS",),
        "status_args": ("--preview",),
    },
    "workbuddy": {
        "script": "WorkBuddy-Daily/workbuddy_daily.py",
        "bundled": False,
        "env_any": ("WORKBUDDY_REFRESH_TOKEN",),
        "status_args": ("--query",),
    },
    "dumate": {
        "script": "DuMate-Daily/dumate_daily.py",
        "bundled": False,
        "env_any": ("DUMATE_COOKIES", "DUMATE_COOKIE", "DUMATE_COOKIE_FILE"),
        "status_args": ("--query",),
    },
    "teleagent": {
        "script": "TeleAgent-Daily/teleagent_daily.py",
        "bundled": False,
        "env_any": ("TELEAGENT_ACCOUNTS", "TELEAGENT_USER_ID"),
        "status_args": ("--query",),
    },
    "deepaicode": {
        "script": "DeepAICode-Daily/deepaicode_daily.py",
        "bundled": False,
        "env_any": ("DEEPAI_API_KEYS", "DEEPAI_API_KEY"),
        "status_args": None,
    },
    "codar": {
        "script": "Codar-Daily/codar_daily.py",
        "bundled": False,
        "env_any": (
            "CODAR_TOKENS",
            "CODAR_TOKEN",
            "CODAR_COOKIES",
            "CODAR_COOKIE",
        ),
        "status_args": ("--status",),
    },
    "monkeycode": {
        "script": "MonkeyCode-Daily/monkeycode_daily.py",
        "bundled": False,
        "env_any": (
            "MONKEYCODE_CN_TOKENS",
            "MONKEYCODE_CN_TOKEN",
            "MONKEYCODE_INTL_TOKENS",
            "MONKEYCODE_INTL_TOKEN",
        ),
        "status_args": None,
    },
    "kakou": {
        "script": "Kakou-Daily/kakou_daily.py",
        "bundled": False,
        "env_any": ("KAKOU_TOKENS", "KAKOU_TOKEN", "KAKOU_ACCOUNT_FILE"),
        "status_args": ("--query",),
    },
    "xingchi": {
        "script": "Xingchi-Daily/xingchi_daily.py",
        "bundled": False,
        "env_any": ("XINGCHI_TOKENS", "XINGCHI_TOKEN", "XINGCHI_ACCOUNT_FILE"),
        "status_args": ("--query",),
    },
    "trustoken": {
        "script": "Trustoken-Daily/trustoken_daily.py",
        "bundled": False,
        "env_any": ("TRUSTOKEN_TOKENS", "TRUSTOKEN_TOKEN"),
        "status_args": None,
    },
    "wpslingxi": {
        "script": "WPSLingxi-Daily/wpslingxi_daily.py",
        "bundled": False,
        "env_any": ("WPSLINGXI_COOKIES", "WPSLINGXI_COOKIE"),
        "status_args": None,
    },
    "croli": {
        "script": "Croli-Daily/croli_daily.py",
        "bundled": False,
        "env_any": ("CROLI_TOKENS", "CROLI_TOKEN"),
        "status_args": None,
    },
    "baipiao": {
        "script": "Baipiao-Daily/baipiao_daily.py",
        "bundled": False,
        "env_any": ("BAIPIAO_ACCOUNTS", "BAIPIAO_SESSION"),
        "status_args": ("--query",),
    },
    "agentrouter": {
        "script": "AgentRouter-Daily/agentrouter_daily.py",
        "bundled": False,
        "env_any": (
            "AGENTROUTER_ACCOUNTS",
            "AGENTROUTER_USERNAME",
        ),
        "status_args": None,
    },
    "sub2api": {
        "script": "Sub2API-Daily/sub2api_daily.py",
        "bundled": False,
        "env_any": (
            "SUB2API_ACCOUNTS",
            "SUB2API_SESSIONS",
            "SUB2API_ACCOUNT_FILE",
            "SUB2API_ACCESS_TOKEN",
        ),
        "status_args": ("--query",),
    },
    "newapi": {
        "script": "NewAPI-Daily/newapi_daily.py",
        "bundled": False,
        "env_any": (
            "NEWAPI_ACCOUNTS",
            "NEWAPI_ACCOUNT_FILE",
            "NEWAPI_ACCESS_TOKEN",
        ),
        "status_args": ("--query",),
    },
}


def parse_last_json(text: str) -> Optional[dict[str, Any]]:
    """Return the last JSON object printed on its own line."""
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except ValueError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def provider_root(env: Optional[Mapping[str, str]] = None) -> str:
    values = os.environ if env is None else env
    configured = str(values.get("FREETOKENS_PROVIDER_ROOT", "") or "").strip()
    return os.path.abspath(configured or DEFAULT_PROVIDER_ROOT)


def resolve_script(name: str, env: Optional[Mapping[str, str]] = None) -> str:
    spec = PROVIDERS[name]
    base = ROOT if spec["bundled"] else provider_root(env)
    return os.path.abspath(os.path.join(base, spec["script"]))


def _has_value(values: Mapping[str, str], name: str) -> bool:
    return bool(str(values.get(name, "") or "").strip())


def is_configured(
    name: str,
    env: Optional[Mapping[str, str]] = None,
) -> bool:
    values = os.environ if env is None else env
    spec = PROVIDERS[name]
    required = tuple(spec.get("env_any") or ())
    if any(_has_value(values, item) for item in required):
        return True
    for pattern in spec.get("credential_globs") or ():
        if glob.glob(os.path.expanduser(pattern)):
            return True
    return not required


def _secret_values(env: Mapping[str, str]) -> list[str]:
    secrets = []
    sensitive = ("TOKEN", "COOKIE", "SECRET", "PASSWORD", "CREDENTIAL", "KEY")
    for name, value in env.items():
        text = str(value or "")
        if len(text) < 8 or not any(word in name.upper() for word in sensitive):
            continue
        secrets.append(text)
    return sorted(set(secrets), key=len, reverse=True)


def redact(text: str, env: Mapping[str, str]) -> str:
    output = str(text or "")
    for secret in _secret_values(env):
        output = output.replace(secret, "[REDACTED]")
    return output


def build_command(
    name: str,
    *,
    status: bool = False,
    env: Optional[Mapping[str, str]] = None,
) -> list[str]:
    command = [sys.executable, resolve_script(name, env)]
    if status:
        status_args = PROVIDERS[name].get("status_args")
        if status_args is None:
            raise ValueError("provider does not expose a read-only status mode")
        command.extend(status_args)
    return command


def _child_env(
    env: Mapping[str, str],
    *,
    allow_provider_notify: bool,
) -> dict[str, str]:
    child = dict(env)
    child.setdefault("PYTHONIOENCODING", "utf-8")
    child.setdefault("PYTHONUTF8", "1")
    if not allow_provider_notify:
        child.setdefault("NO_NOTIFY", "1")
        child.setdefault("MODELSCOPE_NO_NOTIFY", "1")
        child.setdefault("WORKBUDDY_NOTIFY", "0")
    return child


def run_provider(
    name: str,
    *,
    status: bool = False,
    env: Optional[Mapping[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    allow_provider_notify: bool = False,
    include_unconfigured: bool = False,
) -> dict[str, Any]:
    values = dict(os.environ if env is None else env)
    script = resolve_script(name, values)
    base = {
        "provider": name,
        "script": os.path.relpath(script, provider_root(values)),
    }
    if not os.path.isfile(script):
        return {
            **base,
            "status": "skipped",
            "reason": "NOT_INSTALLED",
            "exit_code": None,
            "elapsed": 0,
            "result": None,
        }
    if not include_unconfigured and not is_configured(name, values):
        return {
            **base,
            "status": "skipped",
            "reason": "NOT_CONFIGURED",
            "exit_code": None,
            "elapsed": 0,
            "result": None,
        }
    if status and PROVIDERS[name].get("status_args") is None:
        return {
            **base,
            "status": "skipped",
            "reason": "STATUS_UNSUPPORTED",
            "exit_code": None,
            "elapsed": 0,
            "result": None,
        }

    command = build_command(name, status=status, env=values)
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            cwd=os.path.dirname(script),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=max(1, int(timeout)),
            env=_child_env(
                values,
                allow_provider_notify=allow_provider_notify,
            ),
        )
    except subprocess.TimeoutExpired:
        return {
            **base,
            "status": "failed",
            "reason": "TIMEOUT",
            "exit_code": 124,
            "elapsed": round(time.time() - started, 2),
            "result": None,
        }

    payload = parse_last_json(completed.stdout)
    ok = completed.returncode == 0
    return {
        **base,
        "status": "success" if ok else "failed",
        "reason": "" if ok else "PROVIDER_EXIT_%d" % completed.returncode,
        "exit_code": completed.returncode,
        "elapsed": round(time.time() - started, 2),
        "result": payload,
        "stderr": redact((completed.stderr or "").strip()[-800:], values),
    }


def build_summary(results: Sequence[Mapping[str, Any]], mode: str) -> dict[str, Any]:
    success = sum(1 for item in results if item.get("status") == "success")
    failed = sum(1 for item in results if item.get("status") == "failed")
    skipped = sum(1 for item in results if item.get("status") == "skipped")
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "status": "success" if failed == 0 else "failed",
        "total": len(results),
        "success": success,
        "failed": failed,
        "skipped": skipped,
        "results": list(results),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run provider scripts from adjacent L0NE-6 repositories. "
            "This repository only contains the inventory and scheduler."
        )
    )
    parser.add_argument(
        "--only",
        default="",
        help="comma-separated provider names; default is every provider",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help=(
            "use each provider's query/status mode; some upstream query "
            "endpoints still trigger the daily grant"
        ),
    )
    parser.add_argument(
        "--include-unconfigured",
        action="store_true",
        help="run installed providers even when their account env is empty",
    )
    parser.add_argument(
        "--allow-provider-notify",
        action="store_true",
        help="let each child provider send its own notification",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="per-provider timeout in seconds (default: %d)" % DEFAULT_TIMEOUT,
    )
    parser.add_argument("--json", default="", help="write aggregate JSON here")
    parser.add_argument(
        "--list",
        action="store_true",
        help="list provider names and exit",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list:
        print(json.dumps(sorted(PROVIDERS), ensure_ascii=False, indent=2))
        return 0

    selected = [item.strip() for item in args.only.split(",") if item.strip()]
    unknown = [item for item in selected if item not in PROVIDERS]
    if unknown:
        parser.error("unknown provider(s): %s" % ", ".join(unknown))
    names = selected or list(PROVIDERS)

    results = []
    for name in names:
        results.append(
            run_provider(
                name,
                status=args.status,
                timeout=args.timeout,
                allow_provider_notify=args.allow_provider_notify,
                include_unconfigured=args.include_unconfigured,
            )
        )

    summary = build_summary(results, "status" if args.status else "claim")
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        with open(args.json, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text + "\n")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    _configure = getattr(sys.stdout, "reconfigure", None)
    if callable(_configure):
        _configure(encoding="utf-8", errors="replace")
    sys.exit(main())
