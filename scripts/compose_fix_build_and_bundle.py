import os
import re
import subprocess
from pathlib import Path

project_path = r"F:\homeletter2.0android251006\homeletterAPP"

LOG_COMPILE = Path(project_path) / "compile_fixed.log"
LOG_BUNDLE = Path(project_path) / "bundle_fixed.log"

ERROR_PATTERN = re.compile(r"(ERROR|FAILED|Unresolved)", re.IGNORECASE)
TAIL_LINES = 400


def run_cmd(cmd_str: str) -> int:
    try:
        print(f"[RUN] {cmd_str}")
        # 使用 cmd /c 包裝以避免 NativeCommandError，並確保在專案根目錄執行
        result = subprocess.run(["cmd", "/c", cmd_str], cwd=project_path)
        return result.returncode
    except Exception as e:
        print(f"[NativeCommandError] {e}")
        return 1


def tail_and_filter_log(log_path: Path, tail_lines: int = TAIL_LINES):
    if not log_path.exists():
        print(f"<LOG_NOT_FOUND> {log_path}")
        return
    try:
        text = log_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = log_path.read_text(errors="ignore")
    lines = text.splitlines()
    tail = lines[-tail_lines:]
    print(f"=== Tail({tail_lines}) of {log_path.name} ===")
    for line in tail:
        print(line)
    print(f"=== Filtered Errors from {log_path.name} ===")
    for line in tail:
        if ERROR_PATTERN.search(line):
            print(line)


def main():
    # 1) clean
    if run_cmd(r".\gradlew.bat clean") != 0:
        print("[clean] failed")
        return

    # 2) compile（全部輸出到檔案）
    compile_cmd = r".\gradlew.bat :app:compileProdReleaseKotlin --stacktrace --info --console=plain --no-daemon > compile_fixed.log 2>&1"
    if run_cmd(compile_cmd) != 0:
        print("[compile] failed")
        tail_and_filter_log(LOG_COMPILE)
        return

    # 3) 抽尾段與過濾錯誤（compile）
    tail_and_filter_log(LOG_COMPILE)

    # 4) bundle（全部輸出到檔案）
    bundle_cmd = r".\gradlew.bat :app:bundleProdRelease --stacktrace --info --console=plain --no-daemon --no-configuration-cache > bundle_fixed.log 2>&1"
    if run_cmd(bundle_cmd) != 0:
        print("[bundle] failed")
        tail_and_filter_log(LOG_BUNDLE)
        return

    # Bundle tail & errors
    tail_and_filter_log(LOG_BUNDLE)

    # 5) 列出 AAB 路徑
    aab_dir = Path(project_path) / r"app\build\outputs\bundle\prodRelease"
    aabs = list(aab_dir.glob("*.aab"))
    print("=== AAB paths ===")
    if aabs:
        for p in aabs:
            print(str(p))
    else:
        print("<NO_AAB_FOUND>")


if __name__ == "__main__":
    main()