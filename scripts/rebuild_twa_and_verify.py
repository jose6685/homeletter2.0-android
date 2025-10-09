#!/usr/bin/env python3
"""
重建 TWA 版 AAB 並使用 bundletool 驗證。

使用方式：
  python scripts/rebuild_twa_and_verify.py

需求：Windows（已安裝 JDK 11+）、Gradle Wrapper、bundletool（專案已附帶）。
"""
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None):
    print(f"\n>>> RUN: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, shell=False)
    if proc.returncode != 0:
        raise SystemExit(f"命令失敗（exit={proc.returncode}）：{' '.join(cmd)}")


def main():
    project_root = Path(__file__).resolve().parent.parent
    gradlew = project_root / 'gradlew.bat'
    app_dir = project_root / 'app'
    aab_path = app_dir / 'build' / 'outputs' / 'bundle' / 'prodRelease' / 'app-prod-release.aab'

    if not gradlew.exists():
        raise SystemExit(f"找不到 Gradle Wrapper：{gradlew}")

    print("1) 清理專案…")
    run([str(gradlew), 'clean'], cwd=str(project_root))

    print("2) 建置並產生 prodRelease AAB…")
    run([str(gradlew), ':app:bundleProdRelease', '--no-daemon'], cwd=str(project_root))

    if not aab_path.exists():
        raise SystemExit(f"AAB 未找到：{aab_path}")
    print(f"AAB 生成完成：{aab_path}")

    print("3) 使用 bundletool 驗證 AAB…")
    verify_script = project_root / 'scripts' / 'verify_aab_with_bundletool.py'
    if not verify_script.exists():
        raise SystemExit(f"找不到驗證腳本：{verify_script}")
    run(['python', str(verify_script), str(aab_path)], cwd=str(project_root))

    print("全部步驟完成！")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"發生錯誤：{e}")
        sys.exit(1)