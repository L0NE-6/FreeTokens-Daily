<div align="center">

# 🎁 FreeTokens Daily

**Inventário de tokens gratuitos do AIHOT · scripts reutilizáveis · confirmação no servidor**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

</div>

> [!IMPORTANT]
> Este projeto é gratuito. É proibido revender, colocar atrás de pagamento, redistribuir para captação, fingir ser o autor, remover avisos de copyright ou usar o nome e os QR codes de doação para sugerir autorização oficial. Consulte [NOTICE.md](../NOTICE.md).

## Cobertura

O inventário contém 61 itens públicos do AIHOT:

| Categoria | Quantidade | Significado |
| :--- | ---: | :--- |
| `bundled` | 6 | MiniMax, Meoo, MobileClaw e Inkstone neste repositório |
| `existing_repo` | 14 | Reutiliza repositórios provider existentes da L0NE-6 |
| `implementable_todo` | 0 | Nenhuma API não verificada é apresentada como automação |
| `manual` | 10 | Identidade, estudante, inscrição, WeChat ou etapa no cliente |
| `quota_or_free_api` | 31 | Sem check-in independente; cota automática ou uso direto da API |

Veja [INVENTORY.md](../INVENTORY.md) para todos os itens.

## Providers incluídos

| Provider | Script | Confirmação |
| :--- | :--- | :--- |
| MiniMax Code | `minimax_daily.py` | Status, resultado do claim, pontos e sequência |
| Meoo | `meoo_daily.py` | Concessão, motivo de já recebido e saldo |
| MobileClaw | `mobileclaw_daily.py` | `claimStatus`, tokens, sequência e carteira |
| Inkstone | `inkstone_daily.py` | Resposta free-grant, saldo e pacotes |

O executor também encontra OfficeAce, CodeArts, ModelScope, AStudio, Qoder, TRAE, AutoClaw, ZCode e WorkBuddy quando estão no diretório pai.

## Início rápido

```powershell
python -m pip install -r requirements.txt
python run_all.py --list
python run_all.py --bundled-only
python run_all.py --only meoo,mobileclaw,inkstone
```

Defina `FREETOKENS_PROVIDER_ROOT` se os outros repositórios estiverem em outro local. Itens ausentes ou sem conta aparecem como `NOT_INSTALLED` e `NOT_CONFIGURED`.

## Variáveis principais

| Variável | Uso |
| :--- | :--- |
| `MINIMAX_OAUTH_AUTH_FILE` | Caminho do `auth.json` OAuth do MiniMax |
| `MEOO_COOKIES` / `MEOO_COOKIE` | Cookie de múltiplas/uma conta Meoo |
| `MOBILECLAW_TOKENS` / `MOBILECLAW_TOKEN` | Credencial múltipla/única MobileClaw |
| `INKSTONE_TOKENS` / `INKSTONE_TOKEN` | `uaa-token` múltiplo/único Inkstone |

## Verificação

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

Testes unitários não provam que uma conta real recebeu o prêmio no dia. O sucesso real exige execução ao vivo e confirmação no servidor.

## Privacidade

Não faça commit de tokens, cookies, JWT, telefones, IDs de dispositivo, arquivos de autenticação, logs ou imagens com dados de conta.

## Apoio

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="QR de doação WeChat" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="QR de doação Alipay" />
</p>

<a href="https://star-history.com/#L0NE-6/FreeTokens-Daily&Date">
  <img alt="Star history" src="https://api.star-history.com/svg?repos=L0NE-6/FreeTokens-Daily&type=Date" />
</a>
