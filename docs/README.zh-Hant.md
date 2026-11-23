<div align="center">

# 🎁 FreeTokens Daily

**AIHOT 免費額度清單 · 可重用 provider 腳本 · 伺服器端回讀驗真**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

</div>

> [!IMPORTANT]
> 本專案永久免費。禁止付費包裝、搬運引流、冒充作者、刪除版權資訊，或使用作者身分與收款碼製造官方授權假象。完整規則見 [NOTICE.md](../NOTICE.md)。

## 覆蓋範圍

目前整理 AIHOT 公開清單共 61 項：

| 類型 | 數量 | 說明 |
| :--- | ---: | :--- |
| `bundled` | 0 | 本倉庫不再存放任何 provider 腳本 |
| `existing_repo` | 20 | 每個 provider 腳本各自維護一個 L0NE-6 倉庫 |
| `implementable_todo` | 0 | 沒有把未驗證接口包裝成已自動化 |
| `manual` | 10 | 實名、學生認證、報名、微信或客戶端人工步驟 |
| `quota_or_free_api` | 31 | 沒有獨立簽到；額度自動刷新或直接呼叫 API |

逐項清單見 [INVENTORY.md](../INVENTORY.md)。

## 獨立 provider 倉庫

| Provider | 倉庫 | 回讀 |
| :--- | :--- | :--- |
| MiniMax Code | [MiniMax-Daily](https://github.com/L0NE-6/MiniMax-Daily) | 簽到狀態、領取結果、積分、連簽 |
| Meoo | [Meoo-Daily](https://github.com/L0NE-6/Meoo-Daily) | 發放標記、今日已領原因、餘額 |
| MobileClaw | [MobileClaw-Daily](https://github.com/L0NE-6/MobileClaw-Daily) | `claimStatus`、Token 數、連簽、錢包 |
| 書生·端硯 | [Inkstone-Daily](https://github.com/L0NE-6/Inkstone-Daily) | 免費禮回執、餘額、墨點包 |

調度器也會自動尋找同級的 OfficeAce-Daily、CodeArts-Daily、ModelScope-Daily、AStudio-Daily、Qoder-Daily、Trae-AutoCheckin、AutoClaw-Daily、ZCode-Daily、WorkBuddy-Daily。

## 快速開始

```powershell
python -m pip install -r requirements.txt
python run_all.py --list
python run_all.py --only meoo,mobileclaw,inkstone
```

其他 provider 倉庫放在本倉庫同級目錄，或設定：

```powershell
$env:FREETOKENS_PROVIDER_ROOT = "D:\path\to\provider-repositories"
```

未安裝會標記 `NOT_INSTALLED`，未配置帳號會標記 `NOT_CONFIGURED`。

## 核心變數

| 變數 | 用途 |
| :--- | :--- |
| `MINIMAX_OAUTH_AUTH_FILE` | MiniMax OAuth `auth.json` 路徑 |
| `MEOO_COOKIES` / `MEOO_COOKIE` | Meoo 多/單帳號 Cookie |
| `MOBILECLAW_TOKENS` / `MOBILECLAW_TOKEN` | MobileClaw 多/單帳號憑證 |
| `INKSTONE_TOKENS` / `INKSTONE_TOKEN` | 端硯多/單帳號 `uaa-token` |

## GitHub Actions

本倉庫 workflow 只驗證清單與調度器，不執行任何帳號領取。憑證與每日任務 workflow 均在各自 provider 倉庫中維護，不會自動 clone。

## 驗證

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

單元測試不代表真實帳號當天已領取成功；真實結果必須來自實際執行與服務端回讀。

## 隱私與邊界

禁止提交 Token、Cookie、JWT、手機號、設備號、認證檔、日誌或含帳號資訊的截圖。本專案僅供個人學習與合法自動化，平台規則與活動資格由各平台決定。

## 支持與星軌

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="微信讚賞碼" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="支付寶收款碼" />
</p>

<a href="https://star-history.com/#L0NE-6/FreeTokens-Daily&Date">
  <img alt="Star history" src="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date" />
</a>
