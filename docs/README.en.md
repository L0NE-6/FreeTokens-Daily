<div align="center">

# 🎁 FreeTokens Daily

**AIHOT free-token inventory · reusable provider scripts · server-side readback**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

</div>

> [!IMPORTANT]
> This project is free. Do not resell it, paywall it, repackage it as an
> "internal" or "managed" service, remove author notices, or use the author's
> identity and donation QR codes to imply official authorization. See
> [NOTICE.md](../NOTICE.md).

## Coverage

The inventory currently contains 61 AIHOT entries:

| Category | Count | Meaning |
| :--- | ---: | :--- |
| `bundled` | 6 | MiniMax, Meoo, MobileClaw, and Inkstone scripts in this repository |
| `existing_repo` | 14 | Reuse adjacent L0NE-6 provider repositories |
| `implementable_todo` | 0 | No unverified claim is presented as automation |
| `manual` | 10 | Real-name, student, registration, or client-only steps |
| `quota_or_free_api` | 31 | No independent check-in; quota is automatic or API-based |

See [INVENTORY.md](../INVENTORY.md) for every entry.

## Built-in providers

| Provider | Script | Readback |
| :--- | :--- | :--- |
| MiniMax Code | `minimax_daily.py` | Sign-in status, claim result, points, streak |
| Meoo | `meoo_daily.py` | Grant flag, already-granted reason, balance |
| MobileClaw | `mobileclaw_daily.py` | `claimStatus`, token amount, streak, wallet |
| Inkstone | `inkstone_daily.py` | Free-grant response, balance, credit packages |

The runner also discovers adjacent repositories such as OfficeAce-Daily,
CodeArts-Daily, ModelScope-Daily, AStudio-Daily, Qoder-Daily,
Trae-AutoCheckin, AutoClaw-Daily, ZCode-Daily, and WorkBuddy-Daily.

## Quick start

```powershell
python -m pip install -r requirements.txt
python run_all.py --list
python run_all.py --bundled-only
python run_all.py --only meoo,mobileclaw,inkstone
```

Place provider repositories next to this repository, or set:

```powershell
$env:FREETOKENS_PROVIDER_ROOT = "D:\path\to\provider-repositories"
```

Missing checkouts are reported as `NOT_INSTALLED`; providers without account
configuration are reported as `NOT_CONFIGURED`.

## Core variables

| Variable | Purpose |
| :--- | :--- |
| `MINIMAX_OAUTH_AUTH_FILE` | Path to MiniMax OAuth `auth.json` |
| `MEOO_COOKIES` / `MEOO_COOKIE` | Meoo multi/single account Cookie |
| `MOBILECLAW_TOKENS` / `MOBILECLAW_TOKEN` | MobileClaw multi/single credential |
| `INKSTONE_TOKENS` / `INKSTONE_TOKEN` | Inkstone multi/single `uaa-token` |

Provider-specific formats are documented in each script header and the
corresponding provider repository.

## GitHub Actions

The bundled workflow runs only scripts from this repository. Add the relevant
repository secrets, enable Actions, and run the workflow manually once.
External provider repositories are not cloned automatically.

## Verification

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

Unit tests use fake sessions and do not prove that a real account received a
reward on a specific day. Real success must come from a live run and
server-side readback.

## Privacy

Never commit tokens, cookies, JWTs, phone numbers, device identifiers, auth
files, logs, or screenshots containing account data. The repository and its
release assets contain no credentials.

## Disclaimer

Use this project for personal learning and lawful personal automation. Each
platform controls its own eligibility rules and APIs; verify its terms before
use.

## Support

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="WeChat donation QR" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="Alipay donation QR" />
</p>

Donations are voluntary and never affect functionality.

## Star Trail

<a href="https://star-history.com/#L0NE-6/FreeTokens-Daily&Date">
  <img alt="Star history" src="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date" />
</a>
