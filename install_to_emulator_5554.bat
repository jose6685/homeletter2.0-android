@echo off
setlocal enabledelayedexpansion

REM 查詢並顯示 adb 裝置列表
echo [INFO] Checking adb in PATH...
where adb >nul 2>nul
if errorlevel 1 (
  echo [ERROR] adb 未找到。請安裝 Android Platform Tools 並將 adb 加入 PATH。
  echo 下載頁面: https://developer.android.com/studio/releases/platform-tools
  exit /b 2
)

echo [INFO] 列出目前 adb devices：
adb devices

set "DEVICE=emulator-5554"
set "FOUND="

for /f "skip=1 tokens=1,2" %%A in ('adb devices') do (
  if "%%A"=="%DEVICE%" (
    if /I "%%B"=="device" set FOUND=1
    if /I "%%B"=="offline" set FOUND=OFFLINE
    if /I "%%B"=="unauthorized" set FOUND=UNAUTH
  )
)

if not defined FOUND (
  echo [ERROR] 目標裝置 %DEVICE% 未連線。請先啟動 Android Emulator 或連線裝置。
  echo [HINT] 可嘗試：啟動 AVD 後再執行本批次檔。
  exit /b 3
)

if /I "%FOUND%"=="OFFLINE" (
  echo [ERROR] 裝置 %DEVICE% 狀態為 offline。嘗試：adb kill-server && adb start-server
  exit /b 4
)

if /I "%FOUND%"=="UNAUTH" (
  echo [ERROR] 裝置 %DEVICE% 狀態為 unauthorized。請在裝置上確認授權提示。
  exit /b 5
)

REM 預設 APK 路徑（可修改或改以第一個參數傳入）
set "APK=%~dp0app-prod-release-universal.apk"
if not "%~1"=="" set "APK=%~1"

if not exist "%APK%" (
  echo [ERROR] 未找到 APK：%APK%
  echo [HINT] 先建置或將 AAB 轉為 universal APK 後再試。
  exit /b 6
)

echo [INFO] 安裝 APK 至 %DEVICE% ："%APK%"
adb -s %DEVICE% install -r "%APK%"
if errorlevel 1 (
  echo [ERROR] adb install 失敗，請檢查上方錯誤訊息。
  exit /b 7
)

echo [SUCCESS] 已成功安裝至 %DEVICE% 。
exit /b 0