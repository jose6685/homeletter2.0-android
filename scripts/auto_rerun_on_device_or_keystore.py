import os
import sys
import time
import argparse
import shutil
import subprocess
from pathlib import Path

project_path = r"F:\homeletter2.0android251006\homeletterAPP"


def run_cmd(cmd_str: str):
    try:
        print(f"[RUN] {cmd_str}")
        result = subprocess.run(cmd_str, cwd=project_path, shell=True, capture_output=True, text=True)
        out = result.stdout or ""
        err = result.stderr or ""
        if out:
            print(out)
        if err:
            print(err)
        return result.returncode, out, err
    except Exception as e:
        print(f"[NativeCommandError] {e}")
        return 1, "", str(e)


def read_gradle_properties():
    props = {}
    gp = Path(project_path) / "gradle.properties"
    if gp.exists():
        for line in gp.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                props[k.strip()] = v.strip()
    return props


def resolve_keystore_path(props):
    ks = props.get("RELEASE_STORE_FILE")
    if not ks:
        return None
    p = Path(ks)
    if not p.is_absolute():
        p = Path(project_path) / p
    return str(p)


def has_connected_device():
    # Try PATH first, then fallback to explicit platform-tools path
    adb_in_path = shutil.which("adb") is not None
    cmds = []
    if adb_in_path:
        cmds.append("adb start-server")
        cmds.append("adb devices")
    cmds.append("\"C:\\platform-tools\\adb.exe\" start-server")
    cmds.append("\"C:\\platform-tools\\adb.exe\" devices")
    for c in cmds:
        code, out, _ = run_cmd(c)
        if "devices" in c and code == 0 and out:
            lines = [ln.strip() for ln in out.splitlines()]
            devs = [ln for ln in lines if ln.endswith("\tdevice")]
            if devs:
                print("[INFO] ADB device detected:")
                for d in devs:
                    print(f"- {d}")
                return True
    return False


def wait_for_conditions(timeout_sec: int, poll_sec: int):
    props = read_gradle_properties()
    ks_path = resolve_keystore_path(props)
    ks_ok = False
    dev_ok = False
    start = time.time()
    while time.time() - start < timeout_sec:
        # Check keystore
        if ks_path and Path(ks_path).exists():
            ks_ok = True
        # Check device
        dev_ok = has_connected_device()
        if ks_ok or dev_ok:
            return ks_ok, dev_ok
        print(f"[WAIT] No device/keystore yet. Polling again in {poll_sec}s...")
        time.sleep(poll_sec)
    return ks_ok, dev_ok


def rerun_verify():
    # Ensure bundletool can use adb even without PATH if needed
    prefix = "set PATH=C:\\platform-tools;%PATH% && "
    py = shutil.which("python") or shutil.which("py")
    if not py:
        print("<PYTHON_NOT_FOUND>")
        return 1
    cmd = prefix + ("python" if "python" in py else "py -3") + " .\\scripts\\verify_aab_with_bundletool.py"
    code, out, err = run_cmd(cmd)
    # Surface result
    print("=== Verify Output ===")
    print(out)
    return code


def main():
    parser = argparse.ArgumentParser(description="Auto rerun verification when emulator or keystore is ready")
    parser.add_argument("--timeout", type=int, default=600, help="Max wait seconds (default: 600)")
    parser.add_argument("--poll", type=int, default=5, help="Polling interval seconds (default: 5)")
    args = parser.parse_args()

    print("[INFO] Watching for ADB device or Release keystore...")
    ks_ok, dev_ok = wait_for_conditions(args.timeout, args.poll)
    if not (ks_ok or dev_ok):
        print("<TIMEOUT> 沒有偵測到裝置或 keystore，未重跑驗證。")
        print("提示：請連接模擬器/真機並啟用 USB 偵錯，或提供 Release keystore 後再執行。")
        sys.exit(1)

    print(f"[READY] ks_ok={ks_ok}, dev_ok={dev_ok} -> 重新執行驗證...")
    exit_code = rerun_verify()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()