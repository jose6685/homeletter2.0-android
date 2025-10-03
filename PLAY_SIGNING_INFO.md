# Play 上架簽章資訊（Upload Key）

- 套件名稱：`org.homeletter.app`
- 版本：`versionCode=7`、`versionName="7"`
- Min/Target SDK：`minSdk=21`、`targetSdk=35`

簽章憑證（來源：`homeletter-twa/gradle.properties`）

- `RELEASE_STORE_FILE=F:/homeletter2.0/homeletter-twa/upload.keystore`
- `RELEASE_KEY_ALIAS=upload`
- `RELEASE_STORE_PASSWORD=homeletter2025`
- `RELEASE_KEY_PASSWORD=homeletter2025`

打包指令（Windows）：

- `./gradlew.bat clean bundleProdRelease --no-daemon`
- 產物：`homeletter-twa/app/build/outputs/bundle/prodRelease/app-prod-release.aab`

備註：
- Play App Signing 建議使用上傳金鑰（Upload Key）簽署 `.aab`。
- 首次上架請保留這份憑證資訊，以利後續更換或設定 App Signing。