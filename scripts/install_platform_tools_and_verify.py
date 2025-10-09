import os
import sys
import zipfile
import urllib.request
import shutil
import re
from pathlib import Path
import subprocess

project_path = r"F:\homeletter2.0android251006\homeletterAPP"
platform_tools_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
install_dir = Path(r"C:\platform-tools")


def run_cmd(cmd: str, cwd: Path | None = None):
    try:
        print(f"[RUN] {cmd}")
        res = subprocess.run(f"cmd /c {cmd}", cwd=str(cwd or project_path), shell=True, capture_output=True, text=True)
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr)
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        print(f"[NativeCommandError] {e}")
        return 1, "", str(e)


def download_platform_tools_zip(dest_zip: Path):
    try:
        dest_zip.parent.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Downloading Platform Tools from {platform_tools_url}")
        with urllib.request.urlopen(platform_tools_url, timeout=120) as resp, open(dest_zip, "wb") as f:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
        size = dest_zip.stat().st_size
        print(f"[OK] Downloaded ZIP: {dest_zip} ({size} bytes)")
        return True
    except Exception as e:
        print(f"[download_failed] {e}")
        return False


def extract_zip_to(zip_path: Path, out_dir: Path):
    try:
        # If already installed and adb exists, keep existing installation
        existing_adb = out_dir / "adb.exe"
        if out_dir.exists() and existing_adb.exists():
            print(f"[INFO] Existing Platform Tools detected at {out_dir}; skipping clean reinstall.")
        else:
            if out_dir.exists():
                print(f"[INFO] Removing existing {out_dir} for clean install...")
                try:
                    shutil.rmtree(out_dir)
                except Exception as e:
                    print(f"[WARN] Could not remove existing dir: {e}. Will attempt direct extract.")
            out_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(out_dir)
            # The ZIP contains a folder 'platform-tools'; if so, flatten it
            inner = out_dir / "platform-tools"
            if inner.exists():
                for item in inner.iterdir():
                    target = out_dir / item.name
                    if target.exists():
                        try:
                            if target.is_dir():
                                shutil.rmtree(target)
                            else:
                                target.unlink()
                        except Exception:
                            pass
                    try:
                        shutil.move(str(item), str(target))
                    except Exception:
                        pass
                try:
                    shutil.rmtree(inner)
                except Exception:
                    pass
        out_dir.mkdir(parents=True, exist_ok=True)
        adb_path = out_dir / "adb.exe"
        print(f"[OK] Extracted to {out_dir}; adb present: {adb_path.exists()}")
        return adb_path.exists()
    except Exception as e:
        print(f"[extract_failed] {e}")
        return False


def ensure_path_has_platform_tools():
    try:
        import winreg
        reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            val, _ = winreg.QueryValueEx(key, "Path")
            paths = val.split(";") if val else []
            add = str(install_dir)
            if add.lower() not in [p.lower() for p in paths]:
                paths.append(add)
                new_val = ";".join(paths)
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_val)
                print(f"[OK] Added to system PATH (HKLM): {add}")
            else:
                print(f"[INFO] PATH already contains: {add}")
    except Exception as e:
        print(f"[HKLM_PATH_update_failed] {e}")
        # Fallback HKCU
        try:
            import winreg
            reg_path = r"Environment"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                val, _ = winreg.QueryValueEx(key, "Path")
                paths = val.split(";") if val else []
                add = str(install_dir)
                if add.lower() not in [p.lower() for p in paths]:
                    paths.append(add)
                    new_val = ";".join(paths)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_val)
                    print(f"[OK] Added to user PATH (HKCU): {add}")
                else:
                    print(f"[INFO] User PATH already contains: {add}")
        except Exception as e2:
            print(f"[HKCU_PATH_update_failed] {e2}")
    # Update current process PATH for immediate use
    os.environ["PATH"] = f"{install_dir};" + os.environ.get("PATH", "")


def verify_adb_version():
    # Prefer direct path to freshly installed adb to avoid PATH timing issues
    adb_full = install_dir / "adb.exe"
    if adb_full.exists():
        code, out, err = run_cmd(f"\"{adb_full}\" version")
    else:
        code, out, err = run_cmd("adb version")
    target = "Android Debug Bridge version 36.0.1"
    ok = (code == 0 and target in (out or ""))
    print(f"ADB version ok: {ok}")
    return ok, out, err


def list_devices():
    adb_full = install_dir / "adb.exe"
    if adb_full.exists():
        code, out, err = run_cmd(f"\"{adb_full}\" devices")
    else:
        code, out, err = run_cmd("adb devices")
    devices = []
    if code == 0 and out:
        for ln in out.splitlines():
            if ln.strip().endswith("\tdevice") and not ln.lower().startswith("list of devices"):
                devices.append(ln.strip())
    if not devices:
        print("<NO_ADB_DEVICE> 建議：啟用 USB 偵錯，連接裝置並授權。")
    else:
        print("Connected devices:")
        for d in devices:
            print(f"- {d}")
    return devices


def run_verify_script():
    # Use cmd /c python to run the existing verification script
    code, out, err = run_cmd("python scripts\\verify_aab_with_bundletool.py")
    return code, out, err


def parse_install_result(output: str) -> str:
    # Look for 'Install result: ...'
    m = re.search(r"Install result:\s*(\w+)", output)
    return m.group(1) if m else "UNKNOWN"


def fallback_debug_if_needed(verify_code: int, verify_out: str):
    install_status = parse_install_result(verify_out)
    need_fallback = (verify_code != 0) or (install_status not in ("SUCCESS",))
    if not need_fallback:
        print("[INFO] No fallback needed; install status is SUCCESS.")
        return
    print("[INFO] Fallback to debug AAB for local testing...")
    # Build debug AAB
    code, out, err = run_cmd(".\\gradlew :app:bundleProdDebug")
    if code != 0:
        print("<DEBUG_AAB_BUILD_FAILED>")
        return
    debug_aab = Path(project_path) / r"app\build\outputs\bundle\prodDebug\app-prod-debug.aab"
    if not debug_aab.exists():
        print("<DEBUG_AAB_NOT_FOUND>")
        return
    apks_path = Path(project_path) / "app-prod-debug.apks"
    # Use local-testing for debug AAB
    code, out, err = run_cmd(
        f"java -jar scripts\\bundletool-all.jar build-apks --bundle=\"{debug_aab}\" --output=\"{apks_path}\" --mode=universal --overwrite --local-testing"
    )
    if code != 0 or not apks_path.exists():
        print("<DEBUG_APKS_BUILD_FAILED>")
        return
    # Install
    code, out, err = run_cmd(f"java -jar scripts\\bundletool-all.jar install-apks --apks=\"{apks_path}\"")
    print(f"[DEBUG] Install result: {'SUCCESS' if code == 0 else 'FAILED'}")


def extract_fingerprints(apks_path: Path, keystore_path: Path | None, alias: str | None, storepass: str | None):
    out_dir = Path(project_path) / "apks_extracted"
    try:
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        # Directly extract 'universal.apk' from the .apks (ZIP)
        with zipfile.ZipFile(apks_path, "r") as zf:
            names = zf.namelist()
            uni = next((n for n in names if n.endswith("universal.apk")), None)
            if not uni:
                print("<UNIVERSAL_APK_NOT_FOUND>")
                return None
            zf.extract(uni, out_dir)
        universal_apk = out_dir / "universal.apk"
        if not universal_apk.exists():
            print("<UNIVERSAL_APK_EXTRACTION_FAILED>")
            return None
        # Find META-INF/*.RSA file inside universal.apk
        rsa_path = None
        with zipfile.ZipFile(universal_apk, "r") as apk:
            rsa_candidates = [n for n in apk.namelist() if n.upper().startswith("META-INF/") and n.upper().endswith(".RSA")]
            if rsa_candidates:
                target = rsa_candidates[0]
                apk.extract(target, out_dir)
                rsa_path = out_dir / target
        if not rsa_path or not rsa_path.exists():
            print("<RSA_FILE_NOT_FOUND>")
            return None
        # Read APK certificate fingerprint
        code, out, err = run_cmd(f"keytool -printcert -file \"{rsa_path}\"")
        apk_sha256 = None
        apk_md5 = None
        if out:
            m1 = re.search(r"SHA[- ]?256\s*:\s*([A-F0-9:]+)", out, re.IGNORECASE)
            m2 = re.search(r"MD5\s*:\s*([A-F0-9:]+)", out, re.IGNORECASE)
            apk_sha256 = m1.group(1) if m1 else None
            apk_md5 = m2.group(1) if m2 else None
            if apk_sha256:
                print(f"APK SHA-256: {apk_sha256}")
            if apk_md5:
                print(f"APK MD5: {apk_md5}")
        # Read keystore fingerprint if provided
        ks_sha256 = None
        ks_md5 = None
        if keystore_path and alias and storepass:
            code, out, err = run_cmd(f"keytool -list -v -keystore \"{keystore_path}\" -alias \"{alias}\" -storepass \"{storepass}\"")
            if code == 0 and out:
                m1 = re.search(r"SHA[- ]?256\s*:\s*([A-F0-9:]+)", out, re.IGNORECASE)
                m2 = re.search(r"MD5\s*:\s*([A-F0-9:]+)", out, re.IGNORECASE)
                ks_sha256 = m1.group(1) if m1 else None
                ks_md5 = m2.group(1) if m2 else None
                if ks_sha256:
                    print(f"Keystore SHA-256: {ks_sha256}")
                if ks_md5:
                    print(f"Keystore MD5: {ks_md5}")
        # Compare
        match_sha256 = (apk_sha256 and ks_sha256 and apk_sha256.upper() == ks_sha256.upper())
        match_md5 = (apk_md5 and ks_md5 and apk_md5.upper() == ks_md5.upper())
        print(f"Fingerprint match (SHA-256): {'YES' if match_sha256 else 'NO' if apk_sha256 and ks_sha256 else 'UNKNOWN'}")
        print(f"Fingerprint match (MD5): {'YES' if match_md5 else 'NO' if apk_md5 and ks_md5 else 'UNKNOWN'}")
        return {
            "apk_sha256": apk_sha256,
            "apk_md5": apk_md5,
            "ks_sha256": ks_sha256,
            "ks_md5": ks_md5,
        }
    except Exception as e:
        print(f"[fingerprint_failed] {e}")
        return None


def main():
    # 1) Install Platform Tools
    zip_dest = Path(project_path) / "scripts" / "platform-tools-latest-windows.zip"
    if not download_platform_tools_zip(zip_dest):
        return
    if not extract_zip_to(zip_dest, install_dir):
        return
    ensure_path_has_platform_tools()
    ok, out, err = verify_adb_version()
    print("=== ADB Version Output ===")
    print(out)

    # 2) List devices
    devices = list_devices()

    # 3) Rerun verify script
    code, out, err = run_verify_script()
    print("=== Verify Script Output ===")
    print(out)
    # 4) Fingerprint comparison using generated APKS
    apks = Path(project_path) / "app-prod.apks"
    # Resolve keystore from gradle.properties
    gp = Path(project_path) / "gradle.properties"
    ks_path = None
    alias = None
    storepass = None
    keypass = None
    try:
        if gp.exists():
            for line in gp.read_text(encoding="utf-8", errors="ignore").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip(); v = v.strip()
                    if k == "RELEASE_STORE_FILE": ks_path = v
                    elif k == "RELEASE_KEY_ALIAS": alias = v
                    elif k == "RELEASE_STORE_PASSWORD": storepass = v
                    elif k == "RELEASE_KEY_PASSWORD": keypass = v
        if ks_path:
            p = Path(ks_path)
            if not p.is_absolute():
                p = Path(project_path) / p
            ks_path = str(p)
    except Exception:
        pass

    if apks.exists():
        extract_fingerprints(apks, Path(ks_path) if ks_path else None, alias, storepass)

    # Fallback if needed
    fallback_debug_if_needed(code, out or "")

    print("=== Summary ===")
    print(f"ADB installed: {ok}")
    print(f"Devices: {devices if devices else '<NONE>'}")
    install_status = parse_install_result(out or "")
    print(f"Install: {install_status}")


if __name__ == "__main__":
    main()