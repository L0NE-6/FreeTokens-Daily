<div align="center">

<sub><strong>L0NE-6 · FREE TOKEN SIGNAL</strong></sub>

# 🎁 FreeTokens Daily

**AIHOT 免费额度全景清单 · 独立 provider 仓库导航 · 统一调度入口**

> 当前版本：**v1.0.1**（2026-11-23） · 61 项额度情报，签到脚本全部拆分到独立 provider 仓库

[简体中文](README.md) · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

🎁 61 项免费额度盘点 · 🧭 13 个独立 provider 仓库 · 🔁 统一调度 · 📊 JSON 汇总 · 🐧 青龙友好 · ☁️ GitHub Actions

<img src="https://img.shields.io/github/v/release/L0NE-6/FreeTokens-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/FreeTokens-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20%E9%9D%92%E9%BE%99-4EAA25?style=for-the-badge&logo=linux&logoColor=white" />
<img src="https://img.shields.io/badge/Deploy-%E9%9D%92%E9%BE%99%20%7C%20GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

[✨ 速览](#-30-秒速览) · [📋 覆盖范围](#-61-项怎么覆盖) · [🚀 快速开始](#-快速开始) · [🔧 环境变量](#-环境变量) · [☁️ Actions](#-github-actions) · [🚫 使用边界](#usage-policy) · [✦ 星轨](#-星轨-star-trail)

</div>

---

<a id="usage-policy"></a>
## 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。

禁止把本仓库、脚本、部署说明或 Release 包装成付费资源、内部版、独家版、会员权益、收费课程、代部署服务或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商和付费平台进行涨粉、截流、倒卖或引流；禁止删除作者与版权信息后冒充原创。

官方仓库和 Release 始终免费。第三方以“下载费、激活费、内部版、代部署、会员门槛”等名义收费，均与作者无关。完整规则见 **[NOTICE.md](NOTICE.md)**。

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **做什么** | 同步 AIHOT 免费额度清单，导航到独立 provider 仓库，并提供统一调度入口。 |
| **输入** | 各 provider 独立仓库的 Token、Cookie 或本地客户端凭据；本仓库不内置任何账号数据或签到脚本。 |
| **输出** | 每账号结果、领取回执、服务端回读、失败分类和聚合 JSON。 |
| **部署** | Windows / Linux / 青龙面板 / GitHub Actions。 |
| **依赖** | Python 3.9+；清单同步依赖 `requests`。 |
| **成功判据** | 优先认签到状态、余额变化、领取流水或服务端活动状态，不以单独 HTTP 200 冒充成功。 |

## ✨ 这是什么

AIHOT 的免费额度清单混合了四类东西：

1. **每日/每月可领取**：存在明确签到、claim 或活动领取动作，适合自动化。
2. **一次性新人礼**：可能只需要登录后领取，也可能要求实名认证、报名或客户端交互。
3. **自动刷新额度**：平台按月/按日重置免费 quota，没有独立“签到”按钮。
4. **必须人工**：学生认证、微信报名、客户端弹窗、账号关联等关键步骤无法由纯 HTTP 脚本可靠完成。

因此本项目不会为了凑数给每一行硬写一个假签到。它做的是：

- 把所有 61 项整理成可审计清单；
- 每个签到脚本单独维护一个仓库；
- 本仓库只保留索引、统一调度和覆盖状态；
- 对 quota-only 和 manual 项明确标注，不伪造成功。

---

## 📋 61 项怎么覆盖

完整逐项结果见 **[INVENTORY.md](INVENTORY.md)**，机器可读快照见 **[inventory.json](inventory.json)**。

| 覆盖类型 | 数量 | 含义 |
| :--- | ---: | :--- |
| `bundled` | 0 | 本仓库不再内置任何签到脚本 |
| `existing_repo` | 20 | 全部指向 L0NE-6 独立 provider 仓库 |
| `implementable_todo` | 0 | 没有尚未验证但被误报为可自动化的项目 |
| `manual` | 10 | 实名、学生认证、报名、微信小程序、客户端弹窗等必须人工 |
| `quota_or_free_api` | 31 | 没有独立签到动作，免费额度自动刷新或直接调用 |
| **合计** | **61** | AIHOT 当前公开清单 |

> 数量会随 AIHOT 清单变化。运行 `python sync_inventory.py` 可重新生成，并自动检查是否仍为 61 项。

### 独立 provider

| Provider | 独立仓库 | 动作 |
| :--- | :--- | :--- |
| MiniMax Code | [L0NE-6/MiniMax-Daily](https://github.com/L0NE-6/MiniMax-Daily) | OAuth 凭据续期、状态、签到、领积分 |
| Meoo | [L0NE-6/Meoo-Daily](https://github.com/L0NE-6/Meoo-Daily) | 每日登录积分 |
| MobileClaw | [L0NE-6/MobileClaw-Daily](https://github.com/L0NE-6/MobileClaw-Daily) | 每日、每月、新人实名奖励 |
| 书生·端砚 | [L0NE-6/Inkstone-Daily](https://github.com/L0NE-6/Inkstone-Daily) | 每月免费墨点 |

### 其他独立仓库

| Provider | 仓库 | AIHOT 覆盖 |
| :--- | :--- | :--- |
| 华为 OfficeAce | [L0NE-6/OfficeAce-Daily](https://github.com/L0NE-6/OfficeAce-Daily) | 每日积分、一次性奖励 |
| 华为码道 | [L0NE-6/CodeArts-Daily](https://github.com/L0NE-6/CodeArts-Daily) | 每日福利、免费版、新人注册礼 |
| ModelScope | [L0NE-6/ModelScope-Daily](https://github.com/L0NE-6/ModelScope-Daily) | 国内/国际每日登录魔粒 |
| 科大讯飞 AStudio | [L0NE-6/AStudio-Daily](https://github.com/L0NE-6/AStudio-Daily) | 每日登录、新用户积分 |
| Qoder | [L0NE-6/Qoder-Daily](https://github.com/L0NE-6/Qoder-Daily) | 每日 Credits、新人奖励 |
| TRAE | [L0NE-6/Trae-AutoCheckin](https://github.com/L0NE-6/Trae-AutoCheckin) | 每日积分、月度积分 |
| 智谱 AutoClaw | [L0NE-6/AutoClaw-Daily](https://github.com/L0NE-6/AutoClaw-Daily) | 每周登录、升级礼 |
| 智谱 ZCode | [L0NE-6/ZCode-Daily](https://github.com/L0NE-6/ZCode-Daily) | 套餐领取 |
| 腾讯 WorkBuddy | [L0NE-6/WorkBuddy-Daily](https://github.com/L0NE-6/WorkBuddy-Daily) | 签到、成长任务、限时免费模型 |

---

## 🚀 快速开始

### 1. 安装

```powershell
python -m pip install -r requirements.txt
```

### 2. 查看 provider

```powershell
python run_all.py --list
```

### 3. 指定 provider

```powershell
python run_all.py --only minimax,meoo,mobileclaw,inkstone
```

### 4. 状态/查询模式

```powershell
python run_all.py --status
```

> `--status` 表示“使用 provider 自己声明的查询/状态入口”，**不等于绝对只读**。例如 Meoo 和 ModelScope 的查询 GET 本身就会触发每日登录发放，脚本与 README 已明确说明。Qoder、TRAE、AutoClaw 当前没有可信只读入口，统一调度器会标记 `STATUS_UNSUPPORTED`，不会误触领取。

### 5. 发现独立 provider 仓库

默认会从本仓库的**同级目录**发现这些脚本：

```text
provider-root\
├── FreeTokens-Daily\
├── MiniMax-Daily\
├── Meoo-Daily\
├── MobileClaw-Daily\
├── Inkstone-Daily\
├── OfficeAce-Daily\
├── CodeArts-Daily\
├── ModelScope-Daily\
├── AStudio-Daily\
├── Qoder-Daily\
├── Trae-AutoCheckin\
├── AutoClaw-Daily\
├── ZCode-Daily\
└── WorkBuddy-Daily\
```

如果放在其他目录：

```powershell
$env:FREETOKENS_PROVIDER_ROOT = "D:\path\to\provider-repositories"
python run_all.py
```

未安装的仓库记为 `NOT_INSTALLED`；未配置账号的 provider 记为 `NOT_CONFIGURED`；两者都不会被算成执行失败。

---

## 🔧 环境变量

### 独立签到脚本

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `MINIMAX_OAUTH_AUTH_FILE` | ⬜ | 新版 MiniMax OAuth `auth.json` 路径；不填时自动查找 `~/.minimax/auth/*/*/*/auth.json` |
| `MINIMAX_LS_LEVELDB` | ⬜ | 旧版 MiniMax leveldb 目录覆盖 |
| `MEOO_COOKIES` | ⬜ | 多账号，每行 `备注\|Cookie` |
| `MEOO_COOKIE` | ⬜ | 单账号 Cookie |
| `MOBILECLAW_TOKENS` | ⬜ | 多账号 Token/Cookie，格式见脚本头 |
| `MOBILECLAW_TOKEN` | ⬜ | 单账号 Token/Cookie |
| `INKSTONE_TOKENS` | ⬜ | 多账号 `uaa-token`，格式见脚本头 |
| `INKSTONE_TOKEN` | ⬜ | 单账号 `uaa-token` |
| `PUSHPLUS_TOKEN` | ⬜ | 可选推送；统一调度默认关闭子脚本推送 |
| `QYWX_WEBHOOK` | ⬜ | 可选企业微信机器人完整 URL 或 key |

### 其他 provider

| Provider | 核心变量 |
| :--- | :--- |
| OfficeAce | `OFFICEACE_TOKENS` / `OFFICEACE_AK` + `OFFICEACE_SK` |
| CodeArts | `CODEARTS_CREDENTIALS` |
| ModelScope | `MODELSCOPE_CN_TOKENS` / `MODELSCOPE_INTL_TOKENS` |
| AStudio | `ASTUDIO_COOKIES` |
| Qoder | `QODER_TOKENS` / `QODER_GLOBAL_TOKENS` |
| TRAE | `TRAE_ACCOUNTS` / `TRAE_REFRESH_TOKEN` |
| AutoClaw | `AUTOCLAW_CN_TOKENS` |
| ZCode | `ZCODE_CN_TOKENS` |
| WorkBuddy | `WORKBUDDY_REFRESH_TOKEN` |

每个变量支持的账号格式、续期行为和可选风控参数，以对应仓库 README 为准。

---

## ☁️ GitHub Actions

本仓库的 Actions 只验证清单、调度器和测试，不执行任何账号领取。真正的签到/领取工作流分别位于各 provider 独立仓库。

统一调度在本地或青龙中运行时，会从同级目录发现 provider 仓库；未安装和未配置会分别标记 `NOT_INSTALLED` / `NOT_CONFIGURED`。

---

## 🧪 测试

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

当前测试覆盖清单解析、provider 发现、路径解析和子进程汇总，不读取真实账号，不访问真实签到接口。

真实账号的领取结果必须由实际运行产生；单测通过不代表某个账号当天已领取成功。

---

## 🔄 更新 AIHOT 清单

```powershell
python sync_inventory.py
```

脚本会：

- 抓取 `https://aihot.news/free-tokens.md`；
- 解析 61 项活动；
- 更新 `inventory.json` 和 `INVENTORY.md`；
- 按 `bundled`、`existing_repo`、`implementable_todo`、`manual`、`quota_or_free_api` 分类。

如果 AIHOT 数量不再是 61，脚本会直接报错，防止清单悄悄错位。

---

## 🧠 设计原则

- **独立仓库维护**：每个签到/领取脚本单独版本化、测试、发布和追踪问题。
- **服务端回读**：签到、claim、任务状态或余额至少有一个可信后态。
- **不伪造签到**：没有独立领取动作的 quota-only 项不写假脚本。
- **不掩盖失败**：未安装、未配置、无只读入口、鉴权失效和接口失败分开报告。
- **多账号隔离**：每个账号独立 Session、独立错误，单个失败不阻断后续。
- **敏感信息脱敏**：日志、JSON 和异常信息不输出 Token/Cookie。
- **幂等优先**：已领取识别为中性成功，重复运行不重复领。

第三方许可证声明见 **[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)**。

---

## 🔒 隐私说明

本仓库不包含任何账号、手机号、Token、Cookie、JWT、设备号或本机认证文件。所有凭据均由环境变量、GitHub Secrets 或本地客户端凭据注入。

请不要提交：

- `*_tokens.json`
- `*_cookies.json`
- `auth.json`
- `login_result.json`
- 运行日志
- 包含真实手机号或设备信息的截图

`.gitignore` 已覆盖常见运行文件，但提交前仍应人工检查。

---

## 📁 目录结构

```text
FreeTokens-Daily/
├── .github/workflows/freetokens.yml
├── assets/
│   ├── donate-alipay.jpg
│   └── donate-wechat.png
├── docs/                         # 多语言 README
├── tests/
│   ├── test_run_all.py
│   └── test_sync_inventory.py
├── run_all.py                    # 统一调度器
├── sync_inventory.py             # AIHOT 清单同步
├── inventory.json
├── INVENTORY.md
├── CHANGELOG.md
├── NOTICE.md
├── THIRD_PARTY_NOTICES.md
├── pyproject.toml
├── requirements.txt
└── LICENSE
```

---

## 📦 版本与发布

- 每个实质更新单独发一个 Release；
- 历史版本保留，不覆盖旧 tag；
- Release 附带索引源码包与 `SHA256SUMS.txt`；签到脚本在各自仓库独立发布；
- 公开包不会包含账号凭据和运行日志。

下载页：<https://github.com/L0NE-6/FreeTokens-Daily/releases>

---

## ⚠️ 免责声明

本项目用于个人学习和合法的个人自动化。免费额度规则、接口和活动资格由各平台决定；使用前请确认对应服务条款，并自行承担账号、网络和活动变化带来的风险。

---

## ☕ 支持与投喂

脚本完全免费，无广告、无功能限制。如果它确实帮你省了时间，欢迎自愿赞赏；不影响任何功能，也不影响 Issue 响应。

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>
<p align="center"><sub>💚 微信支付（左） &nbsp;|&nbsp; 💙 支付宝（右）</sub></p>

> 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源或会员群为由收费，均与作者无关。

---

## 💬 反馈与贡献

- [提交 Issue](https://github.com/L0NE-6/FreeTokens-Daily/issues)
- [发起 Pull Request](https://github.com/L0NE-6/FreeTokens-Daily/pulls)

反馈新活动时，请附上公开活动页、客户端版本、脱敏后的请求/响应字段和回读证据。不要上传真实 Token、Cookie、手机号、设备号或完整账号日志。

---

## ✦ 星轨 Star Trail

<a href="https://star-history.com/#L0NE-6/FreeTokens-Daily&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date" />
    <img alt="FreeTokens Daily Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date" />
  </picture>
</a>

---

<div align="center">
  <sub>L0NE-6 · FREE TOKEN SIGNAL &nbsp;|&nbsp; 点个 <b>Star</b>，让下一轮免费额度有迹可循 ✨</sub>
</div>
