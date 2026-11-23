#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch AIHOT free-token inventory and classify automation coverage."""

import collections
import json
import os
import re
import sys

import requests


SOURCE_URL = "https://aihot.news/free-tokens.md"
ROOT = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(ROOT, "inventory.json")
MARKDOWN_PATH = os.path.join(ROOT, "INVENTORY.md")

BUNDLED = {
    4: "meoo_daily.py",
    10: "minimax_daily.py",
    11: "mobileclaw_daily.py",
    19: "inkstone_daily.py",
    22: "mobileclaw_daily.py",
    44: "mobileclaw_daily.py",
}

EXISTING_REPOS = {
    1: "OfficeAce-Daily",
    2: "CodeArts-Daily",
    3: "CodeArts-Daily",
    5: "ModelScope-Daily",
    7: "AStudio-Daily",
    12: "Qoder-Daily",
    13: "Trae-AutoCheckin",
    23: "Trae-AutoCheckin（每日签到；月额度无独立入口）",
    25: "AutoClaw-Daily",
    41: "AutoClaw-Daily",
    43: "AStudio-Daily",
    45: "Qoder-Daily",
    49: "ZCode-Daily",
    57: "WorkBuddy-Daily",
}

IMPLEMENTABLE_TODO = {}

MANUAL = {
    24: "Zed 学生认证",
    31: "Zed Pro 试用",
    32: "UCloud 星图卡密兑换",
    34: "硅基流动实名后活动中心手动领券",
    36: "豆包电脑版弹窗",
    37: "码道赛事报名后活动福利手动领",
    40: "微信小程序成长计划报名",
    42: "GLM Coding Plan 活动页手动领卡",
    48: "WorkBuddy Buddy One 账号关联",
    50: "阿里云学生认证",
}

QUOTA_NOTES = {
    29: "SCNet 客户端人工领新人礼；Cookie 可只读 Token Plan",
    21: "ElevenLabs 可读订阅和用量，无领取接口",
}


def parse_markdown(text):
    section = ""
    current = None
    rows = []
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.startswith("### "):
            if current:
                rows.append(current)
            current = {
                "section": section,
                "title": line[4:].strip(),
                "fields": {},
            }
        elif current and line.startswith("- "):
            match = re.match(r"- ([^：]+)：(.*)", line)
            if match:
                current["fields"][match.group(1)] = match.group(2).strip()
    if current:
        rows.append(current)
    return rows


def coverage_of(index):
    if index in BUNDLED:
        return "bundled", BUNDLED[index]
    if index in EXISTING_REPOS:
        return "existing_repo", EXISTING_REPOS[index]
    if index in IMPLEMENTABLE_TODO:
        return "implementable_todo", IMPLEMENTABLE_TODO[index]
    if index in MANUAL:
        return "manual", MANUAL[index]
    if index in QUOTA_NOTES:
        return "quota_or_free_api", QUOTA_NOTES[index]
    return "quota_or_free_api", "无独立签到动作"


def build_items(rows):
    items = []
    for index, row in enumerate(rows, 1):
        fields = row["fields"]
        coverage, target = coverage_of(index)
        items.append({
            "index": index,
            "section": row["section"],
            "title": row["title"],
            "provider": fields.get("提供方", ""),
            "amount": fields.get("能领多少", ""),
            "how": fields.get("怎么领", ""),
            "usable_for": fields.get("能用在", ""),
            "threshold": fields.get("门槛", ""),
            "expiry": fields.get("有效期", ""),
            "deadline": fields.get("截止", ""),
            "verified_at": fields.get("核实", ""),
            "url": fields.get("去领", ""),
            "coverage": coverage,
            "coverage_target": target,
        })
    return items


def write_markdown(items):
    counts = collections.Counter(item["coverage"] for item in items)
    lines = [
        "# AIHOT 免费额度自动化覆盖清单",
        "",
        "- 来源：https://aihot.news/free-tokens",
        "- 生成：`python sync_inventory.py`",
        "- 共 %d 项：`bundled` %d · `existing_repo` %d · `implementable_todo` %d · `manual` %d · `quota_or_free_api` %d"
        % (
            len(items),
            counts["bundled"],
            counts["existing_repo"],
            counts["implementable_todo"],
            counts["manual"],
            counts["quota_or_free_api"],
        ),
        "- `bundled`：本仓库内置脚本",
        "- `existing_repo`：L0NE-6 已有独立仓库",
        "- `implementable_todo`：仍需验证是否存在稳定、可回读的领取接口",
        "- `quota_or_free_api`：没有独立签到，只适合额度查询/直接调用",
        "- `manual`：关键步骤必须人工",
        "",
        "| # | 栏目 | 提供方 | 活动 | 覆盖 | 目标/说明 | 截止 |",
        "|---:|---|---|---|---|---|---|",
    ]
    for item in items:
        values = [
            str(item["index"]),
            item["section"],
            item["provider"],
            item["title"],
            item["coverage"],
            item["coverage_target"],
            item["deadline"] or "-",
        ]
        escaped = [str(value).replace("|", "\\|").replace("\n", " ") for value in values]
        lines.append("| " + " | ".join(escaped) + " |")
    lines.append("")
    with open(MARKDOWN_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))


def main():
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.get(SOURCE_URL, timeout=60, proxies=proxies)
    response.raise_for_status()
    rows = parse_markdown(response.text)
    if len(rows) != 61:
        raise RuntimeError("expected 61 inventory rows, got %d" % len(rows))
    items = build_items(rows)
    payload = {
        "source": SOURCE_URL,
        "source_bytes": len(response.content),
        "count": len(items),
        "coverage_counts": dict(
            collections.Counter(item["coverage"] for item in items)
        ),
        "items": items,
    }
    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    write_markdown(items)
    print("wrote %s and %s (%d items)" % (JSON_PATH, MARKDOWN_PATH, len(items)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
