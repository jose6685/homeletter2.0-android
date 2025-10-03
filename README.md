# homeletter2.0

根倉庫包含以下子模組與服務：

- `frontend`：前端網站（Vercel 部署），含 `.well-known/assetlinks.json`
- `homeletter-twa`：Android Trusted Web Activity (TWA) 專案
- `backend`：後端服務（Render 部署）

## 子模組使用說明

- 初次克隆：
  - `git clone <root_repo_url>`
  - `cd homeletter2.0`
  - `git submodule update --init --recursive`

- 取得子模組最新更新：
  - `git submodule update --recursive --remote`

- 提交子模組指標更新（在根倉庫）：
  - `git add frontend homeletter-twa backend`
  - `git commit -m "chore(submodules): update pointers"`
  - `git push`

## TWA 與網站關聯（Digital Asset Links）

- TWA 專案設定檔：`homeletter-twa/twa-manifest.json`
  - `packageId`: `org.homeletter.app`
  - `host`: `homeletter2-0-frontend.vercel.app`

- 網站端的 Asset Links：`frontend/.well-known/assetlinks.json`
  - `package_name` 應為 `org.homeletter.app`
  - `sha256_cert_fingerprints` 應與簽章憑證一致

- 更新憑證指紋（若需要）：
  - 以本機簽章檔（例如 `homeletter-release.keystore`）產生 SHA256：
    - `keytool -list -v -keystore homeletter-release.keystore -alias homeletter`
  - 將指紋更新到 `frontend/.well-known/assetlinks.json` 並部署到網站域名

## Play Store 發佈檢查清單（摘要）

- 版本號：更新 `homeletter-twa/twa-manifest.json` 的 `appVersionCode` / `appVersionName`
- 圖示與名稱：`launcherName`、各密度 `mipmap` 圖檔
- 隱私政策：`frontend/docs/privacy.html`（或 `frontend/privacy.html`）對外可訪問
- 站點清單：`webManifestUrl` 指向網站 `manifest.json`，`startUrl` 為根路徑
- 數位資產連結：網站 `/.well-known/assetlinks.json` 必須可公開存取且與簽章指紋一致

## 開發與 CI

- 在 `homeletter-twa` 專案中可使用 Gradle 構建：
  - `cd homeletter-twa`
  - `./gradlew assembleDebug`（Debug 版不需簽章）
  - `./gradlew assembleRelease`（Release 版需簽章設定）

- GitHub Actions（Android CI）會在推送時自動構建 Debug 版 APK（見 `homeletter-twa/.github/workflows/android-ci.yml`）。

## 注意事項

- 若根倉庫為公開倉庫，避免提交大型二進位檔與私密憑證（建議使用 `.gitignore` 或 Git LFS / CI Secrets）。