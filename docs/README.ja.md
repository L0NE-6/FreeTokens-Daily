<div align="center">

# 🎁 FreeTokens Daily

**AIHOT 無料枠インベントリ · 再利用可能な provider スクリプト · サーバー側再確認**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

</div>

> [!IMPORTANT]
> 本プロジェクトは無料です。有料販売、転載による集客、作者の偽装、著作権表示の削除、作者名や寄付 QR を使った公式認可の誤認は禁止です。詳細は [NOTICE.md](../NOTICE.md) を参照してください。

## 対象範囲

AIHOT の公開リスト 61 項目を整理しています。

| 種別 | 件数 | 内容 |
| :--- | ---: | :--- |
| `bundled` | 6 | MiniMax、Meoo、MobileClaw、Inkstone |
| `existing_repo` | 14 | 既存の L0NE-6 provider リポジトリを再利用 |
| `implementable_todo` | 0 | 未検証 API を自動化済みとして扱わない |
| `manual` | 10 | 本人確認、学生認証、申込、WeChat、クライアント操作 |
| `quota_or_free_api` | 31 | 独立したチェックインなし。枠は自動更新または API 利用 |

全項目は [INVENTORY.md](../INVENTORY.md) を参照してください。

## 内蔵 provider

| Provider | スクリプト | 再確認 |
| :--- | :--- | :--- |
| MiniMax Code | `minimax_daily.py` | 状態、claim 結果、ポイント、連続日数 |
| Meoo | `meoo_daily.py` | 付与フラグ、既受取理由、残高 |
| MobileClaw | `mobileclaw_daily.py` | `claimStatus`、Token、連続日数、残高 |
| Inkstone | `inkstone_daily.py` | free-grant 応答、残高、クレジットパッケージ |

OfficeAce、CodeArts、ModelScope、AStudio、Qoder、TRAE、AutoClaw、ZCode、WorkBuddy の既存リポジトリも自動検出します。

## クイックスタート

```powershell
python -m pip install -r requirements.txt
python run_all.py --list
python run_all.py --bundled-only
python run_all.py --only meoo,mobileclaw,inkstone
```

外部 provider は同じ親ディレクトリに配置するか、`FREETOKENS_PROVIDER_ROOT` を設定してください。

未導入は `NOT_INSTALLED`、アカウント未設定は `NOT_CONFIGURED` として報告されます。

## 主な環境変数

| 変数 | 用途 |
| :--- | :--- |
| `MINIMAX_OAUTH_AUTH_FILE` | MiniMax OAuth `auth.json` |
| `MEOO_COOKIES` / `MEOO_COOKIE` | Meoo の複数/単一 Cookie |
| `MOBILECLAW_TOKENS` / `MOBILECLAW_TOKEN` | MobileClaw の複数/単一認証情報 |
| `INKSTONE_TOKENS` / `INKSTONE_TOKEN` | Inkstone の複数/単一 `uaa-token` |

## 検証

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

単体テストは実際のアカウントで当日付与されたことを証明しません。実成功は実実行とサーバー側再確認で判断してください。

## プライバシー

Token、Cookie、JWT、電話番号、端末 ID、認証ファイル、ログ、アカウント情報を含む画像をコミットしないでください。

## サポート

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="WeChat donation QR" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="Alipay donation QR" />
</p>

<a href="https://star-history.com/#L0NE-6/FreeTokens-Daily&Date">
  <img alt="Star history" src="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date" />
</a>
