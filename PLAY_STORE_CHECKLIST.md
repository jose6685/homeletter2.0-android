# Google Play 上架檢查清單（Prod 版）

- App Bundle：上傳 `homeletter-twa/app/build/outputs/bundle/prodRelease/app-prod-release.aab`
- 版本號：`versionCode=7`、`versionName="7"`
- 套件名：`org.homeletter.app`
- Min/Target SDK：`minSdk=21`、`targetSdk=35`
- 簽章：使用 Upload Key（詳見 `homeletter-twa/PLAY_SIGNING_INFO.md`）
- 隱私政策：提供公開網址（範例：`frontend/privacy.html` 或部署站點）
- Data Safety：
  - 網路通訊（`INTERNET`）
  - 推播通知（`POST_NOTIFICATIONS`，Android 13+ 權限）
  - 使用者生成內容（信件）可能透過 API 傳輸與儲存
  - 不收集精準位置、不讀取通訊錄、不採集敏感個資（依實際功能如有變更請更新）
- 內容分級：依文字內容與互動性填寫
- 素材：圖示、螢幕截圖、橫幅、描述（中英文）、聯絡 email、支援網址
- 測試：安裝 `prodRelease` APK 進行實機測試（`./gradlew.bat assembleProdRelease`）
- 後端：確認 `https://homeletter2-0-frontend.vercel.app` 連線正常（或正式後端位址）
- 版本策略：每次上架提升 `versionCode`，維持 `versionName` 規劃（語義化建議）

## 交付前自查
- 非預覽模式：`frontend/config.live.js` 連線至正式 API
- 錯誤監控：後端日誌檢查、前端錯誤處理（重試、提示）
- 法遵合規：隱私政策、資料安全表、第三方服務條款（OpenAI 等）
- 升級與回滾：保留上版 `.aab` 與變更紀錄

## 常用指令
- 產生 `.aab`：`./gradlew.bat clean bundleProdRelease --no-daemon`
- 產生 `APK`：`./gradlew.bat assembleProdRelease --no-daemon`
- 輸出位置：
  - AAB：`homeletter-twa/app/build/outputs/bundle/prodRelease/app-prod-release.aab`
  - APK：`homeletter-twa/app/build/outputs/apk/prod/release/`