# Changelog

## v1.1.0 - 2026-11-24

- Added DuMate, TeleAgent, DeepAI Code, Codar, MonkeyCode, Kakou, Xingchi,
  Trustoken, WPS Lingxi, Croli, Baipiao, AgentRouter, Sub2API, and NewAPI to
  the unified provider scheduler.
- Added explicit status-mode support where the provider exposes a read-only
  status or query action.
- Synchronized the Chinese README and five translated guides with the new
  independent repository table and credential variable names.

## v1.0.2 - 2026-11-23

- Fixed a scheduler test that depended on a locally installed Meoo checkout.
- Verified the Release zip in an isolated extraction directory.

## v1.0.1 - 2026-11-23

- Split MiniMax, Meoo, MobileClaw, and Inkstone into standalone repositories.
- Removed all provider implementation scripts from this repository.
- Changed the runner to discover every provider from adjacent repositories.
- Reclassified the split providers under `existing_repo`.
- Replaced the claim workflow with catalog validation and inventory drift checks.

## v1.0.0 - 2026-11-23

- Added the AIHOT Free Tokens inventory sync with 61 classified entries.
- Added bundled MiniMax, Meoo, MobileClaw, and Inkstone scripts.
- Added a unified provider runner for bundled scripts and adjacent L0NE-6
  provider repositories.
- Added fake-session and subprocess regression tests.
- Added GitHub Actions, privacy rules, usage policy, and third-party notices.
