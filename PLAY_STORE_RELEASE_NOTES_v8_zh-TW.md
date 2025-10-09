版本：8（2025-10-07）

重點更新
- 原生版套件名與命名空間統一為 `org.homeletter.app`，與商店設定一致。
- 針對 Compose 依賴與匯入進行對齊，修復部分匯入解析問題，提升穩定性。
- 清除設定檔中的 BOM 字元（`settings.gradle`），避免 Gradle 解析錯誤。
- `API_BASE_URL`（prod）改為正式後端 `https://homeletter2-0-backend.onrender.com`，確保行動裝置連線可靠。
- 提升 `activity-compose` 版本與補齊 `foundation`、`runtime-livedata` 依賴。

效能與修正
- 改善應用啟動流程與依賴解析，減少潛在編譯與同步問題。
- 維持文字朗讀（TTS）與分享功能，並優化相容性。

已知事項
- 需於本機設定 Android SDK 路徑（`local.properties` 或 `ANDROID_HOME`），方可完成打包。