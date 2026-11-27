<div align="center">

# 🎁 FreeTokens Daily

**AIHOT 무료 토큰 목록 · 재사용 가능한 provider 스크립트 · 서버 측 재확인**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

</div>

> [!IMPORTANT]
> 이 프로젝트는 무료입니다. 유료 재판매, 유입용 재배포, 작성자 사칭, 저작권 표시 제거, 작성자 이름이나 후원 QR을 공식 승인처럼 사용하는 행위를 금지합니다. 자세한 내용은 [NOTICE.md](../NOTICE.md)를 확인하세요.

## 범위

AIHOT 공개 목록 65개 항목을 정리합니다.

| 유형 | 수량 | 의미 |
| :--- | ---: | :--- |
| `bundled` | 0 | provider 스크립트는 이 저장소에 포함하지 않음 |
| `existing_repo` | 17 | 각 provider는 독립 L0NE-6 저장소에서 관리 |
| `implementable_todo` | 0 | 검증되지 않은 API를 자동화로 표시하지 않음 |
| `manual` | 11 | 실명, 학생 인증, 신청, WeChat, 클라이언트 단계 |
| `quota_or_free_api` | 37 | 독립 체크인 없음. 자동 갱신 또는 API 직접 사용 |

전체 목록은 [INVENTORY.md](../INVENTORY.md)를 참고하세요.

## 독립 provider 저장소

v1.1.0에서 DuMate, TeleAgent, DeepAI Code, Codar, MonkeyCode CN/Intl,
Kakou, Xingchi, Trustoken, WPS Lingxi, Croli, Baipiao, AgentRouter,
Sub2API, NewAPI 등 14개 독립 버전 관리 스크립트를 추가했습니다. 전체 표는
[중국어 README](../README.md#2026-11-24-新增独立仓库)를 참조하세요.

| Provider | 저장소 | 재확인 |
| :--- | :--- | :--- |
| MiniMax Code | [MiniMax-Daily](https://github.com/L0NE-6/MiniMax-Daily) | 상태, claim 결과, 포인트, 연속일 |
| Meoo | [Meoo-Daily](https://github.com/L0NE-6/Meoo-Daily) | 지급 플래그, 오늘 이미 받음, 잔액 |
| MobileClaw | [MobileClaw-Daily](https://github.com/L0NE-6/MobileClaw-Daily) | `claimStatus`, Token, 연속일, 지갑 |
| Inkstone | [Inkstone-Daily](https://github.com/L0NE-6/Inkstone-Daily) | free-grant 응답, 잔액, 크레딧 패키지 |

OfficeAce, CodeArts, ModelScope, AStudio, Qoder, TRAE, AutoClaw, ZCode, WorkBuddy 저장소도 자동 탐색합니다.

## 빠른 시작

```powershell
python -m pip install -r requirements.txt
python run_all.py --list
python run_all.py --only meoo,mobileclaw,inkstone
```

외부 provider는 같은 상위 폴더에 두거나 `FREETOKENS_PROVIDER_ROOT`를 설정하세요. 미설치와 미설정은 각각 `NOT_INSTALLED`, `NOT_CONFIGURED`로 표시됩니다.

## 핵심 환경 변수

| 변수 | 용도 |
| :--- | :--- |
| `MINIMAX_OAUTH_AUTH_FILE` | MiniMax OAuth `auth.json` |
| `MEOO_COOKIES` / `MEOO_COOKIE` | Meoo 다중/단일 Cookie |
| `MOBILECLAW_TOKENS` / `MOBILECLAW_TOKEN` | MobileClaw 다중/단일 인증 |
| `INKSTONE_TOKENS` / `INKSTONE_TOKEN` | Inkstone 다중/단일 `uaa-token` |

## 검증

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

단위 테스트는 실제 계정이 당일 보상을 받았다는 증거가 아닙니다. 실제 성공은 실행 후 서버 측 재확인으로 판단해야 합니다.

## 개인정보

Token, Cookie, JWT, 전화번호, 기기 ID, 인증 파일, 로그, 계정 정보가 포함된 이미지를 커밋하지 마세요.

## 지원

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="WeChat donation QR" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="Alipay donation QR" />
</p>

<a href="https://star-history.com/#L0NE-6/FreeTokens-Daily&Date">
  <img alt="Star history" src="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date" />
</a>
