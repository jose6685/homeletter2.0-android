#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建原生 Compose 版本並進行基本驗證：
1) Gradle clean
2) :app:bundleProdRelease 產出 AAB
3) 以 bundletool（若存在）驗證 AAB 結構
4) 簡單檢查 AdMob SDK 初始化 log（裝置連線時）

用法：
  python scripts/rebuild_original_compose.py
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_DIR / 'app'
BUILD_DIR = APP_DIR / 'build' / 'outputs' / 'bundle' / 'prodRelease'
GRADLEW = PROJECT_DIR / ('gradlew.bat' if os.name == 'nt' else 'gradlew')


def run(cmd, cwd=None, shell=False):
    print(f"\n$ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, cwd=cwd, shell=shell, text=True, capture_output=True)


def main():
    print("=== Step 1: Gradle clean ===")
    r = run([str(GRADLEW), 'clean'], cwd=str(PROJECT_DIR))
    print(r.stdout); print(r.stderr)

    if r.returncode != 0:
        print("[ERROR] gradle clean 失敗")
        sys.exit(1)

    print("=== Step 2: Build :app:bundleProdRelease ===")
    r = run([str(GRADLEW), ':app:bundleProdRelease', '--stacktrace'], cwd=str(PROJECT_DIR))
    print(r.stdout); print(r.stderr)

    if r.returncode != 0:
        print("[ERROR] 建置 AAB 失敗")
        sys.exit(1)

    aab_files = list(BUILD_DIR.glob('*.aab'))
    if not aab_files:
        print("[ERROR] 未找到 AAB 產物於", BUILD_DIR)
        sys.exit(1)
    aab = aab_files[0]
    print(f"AAB: {aab}")

    print("=== Step 3: Bundletool 驗證（若存在） ===")
    bt = os.environ.get('BUNDLETOOL_JAR', '')
    if bt and Path(bt).exists():
        # 僅進行 validate，避免生成 apks 檔案
        r = run(['java', '-jar', bt, 'validate', '--bundle', str(aab)])
        print(r.stdout); print(r.stderr)
        print(f"Bundletool validate exit={r.returncode}")
    else:
        print("略過：未設定 BUNDLETOOL_JAR 環境變數或檔案不存在。")

    print("=== Step 4: AdMob 初始化檢查（ADB 可選） ===")
    # 嘗試抓取 Logcat 中 Google Mobile Ads SDK 初始化關鍵字
    try:
        r = run(['adb', 'logcat', '-d', '|', 'findstr', 'MobileAds'])
        print(r.stdout)
    except Exception as e:
        print(f"略過：ADB 不可用或無裝置。{e}")

    print("\n完成。請於 Android Studio/裝置上進一步驗證版面與廣告顯示。")


if __name__ == '__main__':
    main()