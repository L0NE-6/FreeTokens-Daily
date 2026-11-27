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

MIN_INVENTORY_ROWS = 50

# AIHOT inserts and reorders rows. Match stable provider/title text instead of
# numeric indexes so a new row cannot silently attach the wrong repository.
COVERAGE_RULES = [
    ("华为云 OfficeAce", "每日登录", "existing_repo", "OfficeAce-Daily"),
    ("华为云码道", "每日签到", "existing_repo", "CodeArts-Daily"),
    ("秒悟 Meoo", "每天登录", "existing_repo", "Meoo-Daily"),
    ("魔搭社区", "每天送", "existing_repo", "ModelScope-Daily"),
    ("科大讯飞 AStudio", "每天登录", "existing_repo", "AStudio-Daily"),
    ("科大讯飞 AStudio", "新用户下载登录", "existing_repo", "AStudio-Daily"),
    ("移动云 MobileClaw", "每日登录", "existing_repo", "MobileClaw-Daily"),
    ("移动云 MobileClaw", "每月登录", "existing_repo", "MobileClaw-Daily"),
    ("阿里云 Qoder", "免费试用期每天领", "existing_repo", "Qoder-Daily"),
    ("阿里云 Qoder", "新人", "existing_repo", "Qoder-Daily"),
    ("字节 TRAE", "每天签到", "existing_repo", "Trae-AutoCheckin"),
    (
        "字节 TRAE",
        "每月",
        "existing_repo",
        "Trae-AutoCheckin（每日签到；月额度无独立入口）",
    ),
    ("书生·端砚", "每月送", "existing_repo", "Inkstone-Daily"),
    ("智谱 AutoClaw", "本周登录", "existing_repo", "AutoClaw-Daily"),
    ("智谱 AutoClaw", "升级礼", "existing_repo", "AutoClaw-Daily"),
    ("智谱 ZCode", "新用户", "existing_repo", "ZCode-Daily"),
    ("长亭 MonkeyCode", "每日签到", "existing_repo", "MonkeyCode-Daily"),
    ("云知声", "U Plan", "manual", "云知声实名后领取 U Plan Free"),
    ("百度千帆", "新用户", "manual", "百度千帆实名后领取代金券"),
    ("Zed", "试用", "manual", "Zed Pro 试用"),
    ("UCloud 星图", "新客", "manual", "UCloud 星图卡密兑换"),
    ("硅基流动", "实名认证", "manual", "硅基流动实名后活动中心手动领券"),
    ("豆包", "电脑版新用户", "manual", "豆包电脑版弹窗"),
    ("华为云码道", "报名", "manual", "码道赛事报名后活动福利手动领"),
    ("阿里 千问办公", "首次激活桌面端", "manual", "千问办公桌面端完成新手任务"),
    ("腾讯云开发", "微信小程序", "manual", "微信小程序成长计划报名"),
    ("智谱", "GLM Coding Plan", "manual", "GLM Coding Plan 活动页手动领卡"),
    ("阿里云百炼", "学生", "manual", "阿里云学生认证"),
    ("ElevenLabs", "免费档", "quota_or_free_api", "可读订阅和用量，无领取接口"),
]


def _normalize(value):
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


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


def coverage_of(provider, title):
    provider_text = _normalize(provider)
    title_text = _normalize(title)
    for provider_match, title_match, coverage, target in COVERAGE_RULES:
        if _normalize(provider_match) in provider_text and _normalize(title_match) in title_text:
            return coverage, target
    return "quota_or_free_api", "无独立签到动作"


def build_items(rows):
    items = []
    for index, row in enumerate(rows, 1):
        fields = row["fields"]
        provider = fields.get("提供方", "")
        coverage, target = coverage_of(provider, row["title"])
        items.append({
            "index": index,
            "section": row["section"],
            "title": row["title"],
            "provider": provider,
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
        "- `bundled`：本仓库内置脚本（当前为 0）",
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
    if len(rows) < MIN_INVENTORY_ROWS:
        raise RuntimeError(
            "expected at least %d inventory rows, got %d"
            % (MIN_INVENTORY_ROWS, len(rows))
        )
    missing_provider = [row["title"] for row in rows if not row["fields"].get("提供方")]
    if missing_provider:
        raise RuntimeError("inventory rows missing provider: %s" % ", ".join(missing_provider))
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
