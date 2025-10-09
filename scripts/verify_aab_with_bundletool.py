import os
import subprocess
import shutil
from pathlib import Path
import re

project_path = r"F:\homeletter2.0android251006\homeletterAPP"


def run_cmd(cmd_str: str):
    try:
        print(f"[RUN] {cmd_str}")
        # Use shell=True on Windows to avoid quoting issues with absolute/relative paths
        result = subprocess.run(cmd_str, cwd=project_path, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"[NativeCommandError] {e}")
        return 1, "", str(e)


def run_cmd_masked(cmd_str: str, masked_display: str):
    try:
        print(f"[RUN] {masked_display}")
        result = subprocess.run(cmd_str, cwd=project_path, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"[NativeCommandError] {e}")
        return 1, "", str(e)


def find_bundletool():
    candidates = [
        Path(project_path) / "scripts" / "bundletool-all.jar",
        Path(project_path) / "bundletool-all.jar",
        Path(project_path) / "tools" / "bundletool-all.jar",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def read_gradle_properties():
    props = {}
    gp = Path(project_path) / "gradle.properties"
    if gp.exists():
        for line in gp.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                props[k.strip()] = v.strip()
    return props


def main():
    aab_path = Path(project_path) / r"app\build\outputs\bundle\prodRelease\app-prod-release.aab"
    apks_path = Path(project_path) / "app-prod.apks"
    bundletool_jar = find_bundletool()

    print("=== Verify Inputs ===")
    print(f"AAB: {aab_path}")
    print(f"APKS: {apks_path}")
    print(f"bundletool: {bundletool_jar}")

    if not aab_path.exists():
        print("<AAB_NOT_FOUND>")
        return
    if not bundletool_jar:
        print("<BUNDLETOOL_JAR_NOT_FOUND> Please place bundletool-all.jar in project root.")
        return

    # Report AAB size
    aab_size_mb = os.path.getsize(aab_path) / (1024 * 1024)
    print(f"AAB size: {aab_size_mb:.2f} MB")

    # Read signing config
    props = read_gradle_properties()
    ks = props.get("RELEASE_STORE_FILE")
    ks_alias = props.get("RELEASE_KEY_ALIAS")
    ks_pass = props.get("RELEASE_STORE_PASSWORD")
    key_pass = props.get("RELEASE_KEY_PASSWORD", ks_pass)

    # Resolve keystore path relative to project if necessary and check existence
    ks_path = None
    ks_exists = False
    if ks:
        ks_path = Path(ks)
        if not ks_path.is_absolute():
            ks_path = Path(project_path) / ks_path
        ks_exists = ks_path.exists()
    if not ks_exists:
        print("<RELEASE_KEYSTORE_NOT_FOUND> 需使用 Release keystore 進行簽署，上傳前請提供正確 keystore、alias 與密碼。")

    # Prefer relative path to the project root for the JAR to avoid path quirks
    bundletool_rel = bundletool_jar
    try:
        bundletool_rel = os.path.relpath(bundletool_jar, project_path)
    except Exception:
        pass

    # Sanity check the jar accessibility
    sanity_cmd = f"java -jar \"{bundletool_rel}\" help"
    scode, sout, serr = run_cmd(sanity_cmd)
    if scode != 0:
        print("<BUNDLETOOL_JAR_ACCESS_FAILED>")
        return

    # Build APKS (signed) with universal mode
    signing_mode_release = bool(ks_exists and ks_alias)
    print(f"Signing mode: {'RELEASE' if signing_mode_release else 'LOCAL_TESTING (debug)'}")
    build_cmd = (
        f"java -jar \"{bundletool_rel}\" build-apks "
        f"--bundle=\"{aab_path}\" --output=\"{apks_path}\" --mode=universal --overwrite "
        + (f"--ks=\"{ks_path}\" --ks-key-alias=\"{ks_alias}\" " if signing_mode_release else "--local-testing ")
        + (f"--ks-pass=pass:{ks_pass} " if ks_exists and ks_pass else "")
        + (f"--key-pass=pass:{key_pass} " if ks_exists and key_pass else "")
    )
    masked_build_display = (
        f"java -jar \"{bundletool_rel}\" build-apks --bundle=\"{aab_path}\" --output=\"{apks_path}\" "
        f"--mode=universal --overwrite "
        + (f"--ks=\"{ks_path}\" --ks-key-alias=\"{ks_alias}\" " if signing_mode_release else "--local-testing ")
        + ("--ks-pass=pass:**** " if ks_exists and ks_pass else "")
        + ("--key-pass=pass:**** " if ks_exists and key_pass else "")
    )
    code, out, err = run_cmd_masked(build_cmd, masked_build_display)
    if code != 0 or not apks_path.exists():
        print("<BUILD_APKS_FAILED>")
        # If signing mismatch or failure, hint to use debug bundle
        print("Hint: Try ':app:bundleProdDebug' and local testing if signing fails.")
        return

    print("=== APKS Generated ===")
    print(str(apks_path))
    if not signing_mode_release:
        print("[WARN] 目前使用 debug/local-testing 簽署，僅供本機測試，不可上傳 Play Console。")

    # Check ADB devices and install APKS to connected device if available
    adb_ok = False
    use_platform_tools_path = False
    # Try starting ADB server via PATH or fallback
    run_cmd("adb start-server")
    run_cmd("\"C:\\platform-tools\\adb.exe\" start-server")

    # Prefer PATH if available, otherwise fallback to explicit platform-tools path
    adb_in_path = shutil.which("adb") is not None
    adb_checks = []
    if adb_in_path:
        adb_checks.append("adb devices")
    adb_checks.append("\"C:\\platform-tools\\adb.exe\" devices")

    for adb_cmd in adb_checks:
        code, out, err = run_cmd(adb_cmd)
        if code == 0 and out:
            device_lines = [ln for ln in out.splitlines() if ln.strip().endswith("\tdevice")]
            if device_lines:
                adb_ok = True
                use_platform_tools_path = ("platform-tools\\adb.exe" in adb_cmd)
                break

    if not adb_ok:
        print("<NO_ADB_DEVICE> Skipping install-apks.")
        install_result = "SKIPPED"
    else:
        # Ensure bundletool can find adb: inject platform-tools into PATH for this command if needed
        prefix = "set PATH=C:\\platform-tools;%PATH% && " if use_platform_tools_path and not adb_in_path else ""
        install_cmd = prefix + f"java -jar \"{bundletool_rel}\" install-apks --apks=\"{apks_path}\""
        code, out, err = run_cmd(install_cmd)
        install_result = "SUCCESS" if code == 0 else "FAILED"
    print(f"Install result: {install_result}")

    # Print signing info from AAB
    print("=== Signing (keytool -printcert -jarfile) ===")
    keytool_cmd = f"keytool -printcert -jarfile \"{aab_path}\""
    code, out, err = run_cmd(keytool_cmd)
    aab_sha256 = None
    aab_md5 = None
    if out:
        # Try to parse SHA-256 and MD5 fingerprints (keytool output varies slightly by locale)
        sha256_match = re.search(r"SHA[- ]?256(?:\s*):\s*([A-F0-9:]+)", out, re.IGNORECASE)
        md5_match = re.search(r"MD5(?:\s*):\s*([A-F0-9:]+)", out, re.IGNORECASE)
        aab_sha256 = sha256_match.group(1) if sha256_match else None
        aab_md5 = md5_match.group(1) if md5_match else None
        if aab_sha256:
            print(f"Parsed AAB SHA-256: {aab_sha256}")
        if aab_md5:
            print(f"Parsed AAB MD5: {aab_md5}")

    # If keystore details exist, obtain expected fingerprint from keystore alias
    expected_sha256 = None
    expected_md5 = None
    if ks_exists and ks_alias and ks_pass:
        list_cmd = f"keytool -list -v -keystore \"{ks_path}\" -alias \"{ks_alias}\" -storepass \"{ks_pass}\""
        masked_list_display = f"keytool -list -v -keystore \"{ks_path}\" -alias \"{ks_alias}\" -storepass \"****\""
        code, out, err = run_cmd_masked(list_cmd, masked_list_display)
        if code == 0 and out:
            sha256_match = re.search(r"SHA[- ]?256(?:\s*):\s*([A-F0-9:]+)", out, re.IGNORECASE)
            md5_match = re.search(r"MD5(?:\s*):\s*([A-F0-9:]+)", out, re.IGNORECASE)
            expected_sha256 = sha256_match.group(1) if sha256_match else None
            expected_md5 = md5_match.group(1) if md5_match else None
            if expected_sha256:
                print(f"Keystore SHA-256: {expected_sha256}")
            if expected_md5:
                print(f"Keystore MD5: {expected_md5}")

    match_sha256 = (aab_sha256 and expected_sha256 and aab_sha256.strip().upper() == expected_sha256.strip().upper())
    match_md5 = (aab_md5 and expected_md5 and aab_md5.strip().upper() == expected_md5.strip().upper())
    print(f"Fingerprint match (SHA-256): {'YES' if match_sha256 else 'NO' if aab_sha256 and expected_sha256 else 'UNKNOWN'}")
    print(f"Fingerprint match (MD5): {'YES' if match_md5 else 'NO' if aab_md5 and expected_md5 else 'UNKNOWN'}")
    upload_ready = bool(signing_mode_release and (match_sha256 or (aab_sha256 and expected_sha256)))
    print(f"Upload readiness: {'YES' if upload_ready else 'NO'}")
    # Surface RELEASE_* from gradle.properties for operator to compare
    print("=== gradle.properties RELEASE_* ===")
    for k, v in props.items():
        if k.startswith("RELEASE_"):
            if "PASSWORD" in k:
                print(f"{k}=****")
            else:
                print(f"{k}={v}")

    print("=== Summary ===")
    print(f"AAB size: {aab_size_mb:.2f} MB")
    print(f"APKS path: {apks_path}")
    print(f"Install: {install_result}")
    print(f"Signing: {'RELEASE' if signing_mode_release else 'LOCAL_TESTING'} | Upload readiness: {'YES' if upload_ready else 'NO'}")


if __name__ == "__main__":
    main()