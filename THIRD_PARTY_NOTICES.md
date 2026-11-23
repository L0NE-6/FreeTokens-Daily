# Third-Party Sources

This project reuses mature public protocol implementations where possible.
The scripts in this repository do not contain account credentials.

The MIT permission text is reproduced in [LICENSE](LICENSE). Upstream
copyright notices retained here:

- `Copyright (c) 2026 Minatoxiaohu`
- `Copyright (c) 2026 magpie-community contributors`
- The Meoo upstream LICENSE file currently contains
  `Copyright (c) 2026 YOUR NAME`; this notice preserves the file exactly as
  published rather than inventing an author name.

## Bundled implementations

### MiniMax Code

- Source: `Minatoxiaohu/agent-auto-signin`
- License: MIT
- Reused for: MiniMax OAuth credential handling, refresh-token rotation,
  sign-in status, claim, and local credential write-back.
- Local file: `minimax_daily.py`

### Meoo

- Source: `shadyrispy/magpie-meoo`
- Commit reviewed: `078c04440696f91ecac47496af135c9687f6a451`
- License: MIT
- Reused for: the `GET /api/mc/entitlement/init` daily-login protocol and
  response-field semantics.
- Local file: `meoo_daily.py`

### 书生·端砚

- Source: `magpie-community/plugins`
- Protocol commit reviewed: `087c36123dc01f6035acbf371647da192a292eda`
- Hook commit reviewed: `73d1f898221c4300f3b677076f8936eafc892272`
- License: MIT
- Reused for: monthly free-credit claim and balance/package readback.
- Local file: `inkstone_daily.py`

## Protocol evidence only

### MobileClaw

- Source: `lyimoexiao/opencode-mobileclaw-auth`
- Commit reviewed: `06550f02a3105a292d8dd4e5bdf9d6d6f49064d9`
- License status: no SPDX license was present when reviewed.
- Use: protocol evidence only. The local implementation is independently
  written and does not copy source code from that repository.

## Existing L0NE-6 providers

The unified runner can invoke scripts from these adjacent public repositories:

- `L0NE-6/OfficeAce-Daily`
- `L0NE-6/CodeArts-Daily`
- `L0NE-6/ModelScope-Daily`
- `L0NE-6/AStudio-Daily`
- `L0NE-6/Qoder-Daily`
- `L0NE-6/Trae-AutoCheckin`
- `L0NE-6/AutoClaw-Daily`
- `L0NE-6/ZCode-Daily`
- `L0NE-6/WorkBuddy-Daily`

Those repositories retain their own licenses, notices, credentials, and
release histories.

## Inventory

- Source: <https://aihot.news/free-tokens>
- Snapshot generator: `sync_inventory.py`
- Generated files: `inventory.json`, `INVENTORY.md`
