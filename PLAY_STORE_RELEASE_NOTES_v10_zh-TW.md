版本 10（2025-10-09）

重點更新
- 修正：強化信箱 API 解析，避免後端回傳非陣列時發生「Value … of type java.lang.String cannot be converted to JSONArray」錯誤，改善穩定性。
- 說明：原生 Android 詳情頁已對齊 Web 設計，不顯示 Facebook/LINE 分享（保留朗讀 TTS）。
- 其他：相容性與效能微調；整體體驗更穩定。

技術細節
- `ApiClient.getMailbox()` 改為防禦性解析：遇到字串或物件時不崩潰，並回退為空陣列或常見鍵名（`mailbox`/`data`）。
- 版本代號（versionCode）與版本名稱（versionName）更新為 10。

注意事項
- 若 Web 端仍顯示分享按鈕，請更新前端專案移除 `LINE/Facebook` 分享並重新部署，以讓 TWA 一併對齊。