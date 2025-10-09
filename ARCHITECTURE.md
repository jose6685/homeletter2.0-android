# 共構策略與模組拆分計畫

本專案目前保留 Web 與 Android 共構（同一專案目錄）以便：
- 同步調整邏輯與 UI，即時在 Web 預覽效果。
- 以最少流程成本維護兩端一致性。

## 倉庫映射
- `frontend/` → `jose6685/homeletter2.0-frontend`
- `backend/` → `jose6685/homeletter2.0-backend`
- 原生 Android（`homeletterAPP/`） → `jose6685/homeletter2.0-android`
- TWA（`homeletter-twa/`） → `jose6685/homeletter-twa`

> 註：Android 倉庫的 `.gitignore` 已排除非 Android 子專案目錄，推送時不會夾帶 Web/TWA 檔案。

## 開發流程建議
1. 在 `frontend/` 開發並以 `python -m http.server 8000` 本地預覽。
2. 同步必要邏輯到 Android（Compose 介面或 Activity）。
3. 依序推送：`frontend` → `android`（必要時 `backend`、`twa`），遠端有更新時以 `git fetch` + `git rebase -X ours origin/main` 對齊。
4. 僅在需求穩定後，考慮分離模組（見下）。

## 暫不拆分 submodule 的理由
- 目前仍在高頻率迭代階段，保持共構易於同步 UI 與邏輯。
- 待 API 與 UI 穩定，拆分可降低耦合並簡化 CI/CD。

## 未來拆分指引（草案）
- 目標：Web 與 Android 互不依賴檔案結構；以 API 契約為唯一邊界。
- 步驟：
  - 在各倉庫補齊 README/環境設定與打包流程。
  - 移除 Android 倉庫的 submodule 記錄，保留 `frontend/` 的獨立部署（Vercel）。
  - 以版本化 API（如 `/v1`）固定契約，避免跨倉庫破壞性變更。

## 版本與相容性
- 前端與 Android 對同一後端 `API_BASE`，請在 `config.js`／`config.live.js` 維護一致性。
- 朗讀/分享等功能的行為差異，應以平台特性包裝（Web Speech API vs TTS）。

---
若需更新此策略或開始拆分，請在 Issue 中建立「架構決策紀錄（ADR）」並更新本文件。