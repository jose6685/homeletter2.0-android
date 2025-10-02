@echo off
setlocal
copy /Y ".\frontend\config.live.js" ".\frontend\config.js" >nul 2>&1
if %errorlevel% equ 0 (
  echo 已切換為「正式模式」：恢復廣告與 API。請重新整理瀏覽器。
  rem -- 自動推到 GitHub（若已設定 Git 與遠端） --
  if exist ".git" (
    where git >nul 2>&1
    if %errorlevel% equ 0 (
      git add frontend\config.js >nul 2>&1
      git status --porcelain | findstr /r "." >nul 2>&1
      if %errorlevel% equ 0 (
        git commit -m "chore(toggle): enable ads (SAFE_MODE=false)" || echo 無需提交或提交失敗
      ) else (
        echo 無變更需要提交。
      )
      for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set BRANCH=%%i
      git remote get-url origin >nul 2>&1
      if %errorlevel% equ 0 (
        git push origin %BRANCH%
        if %errorlevel% equ 0 (
          echo 已推送到遠端分支：%BRANCH%
        ) else (
          echo 推送失敗：請確認憑證/權限已設定。
        )
      ) else (
        echo 未設定遠端 origin，略過推送。
      )
    ) else (
      echo 未安裝 Git 或未在 PATH 中，略過推送。
    )
  ) else (
    echo 非 Git 專案，略過推送。
  )
) else (
  echo 切換失敗：請確認檔案路徑存在。
)
endlocal
pause