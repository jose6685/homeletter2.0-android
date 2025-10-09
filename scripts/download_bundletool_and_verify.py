import os
import shutil
import subprocess
from pathlib import Path

project_path = r"F:\homeletter2.0android251006\homeletterAPP"
bundletool_url = "https://github.com/google/bundletool/releases/download/1.18.2/bundletool-all-1.18.2.jar"


def run_cmd(cmd_str: str):
    try:
        print(f"[RUN] {cmd_str}")
        result = subprocess.run(["cmd", "/c", cmd_str], cwd=project_path, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode
    except Exception as e:
        print(f"[NativeCommandError] {e}")
        return 1


def download_bundletool(dest_path: Path):
    try:
        import requests  # type: ignore
        print("[INFO] Using requests to download bundletool...")
        r = requests.get(bundletool_url, stream=True, timeout=120, allow_redirects=True)
        r.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        print(f"[requests_unavailable_or_failed] {e}")
        try:
            print("[INFO] Fallback to urllib to download bundletool...")
            import urllib.request
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(bundletool_url, timeout=120) as resp, open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e2:
            print(f"[urllib_failed] {e2}")
            return False
    # Basic validation
    try:
        size = dest_path.stat().st_size
        with open(dest_path, "rb") as f:
            header = f.read(2)
        if size < 100_000 or header != b"PK":
            print(f"[download_validation_failed] size={size}, header={header}")
            return False
        print(f"[OK] Downloaded: {dest_path} ({size} bytes)")
        return True
    except Exception as e:
        print(f"[validation_error] {e}")
        return False


def main():
    scripts_jar = Path(project_path) / "scripts" / "bundletool-all.jar"
    root_jar = Path(project_path) / "bundletool-all.jar"

    # Download JAR if not present
    if not scripts_jar.exists():
        ok = download_bundletool(scripts_jar)
        if not ok:
            print("<DOWNLOAD_BUNDLETOOL_FAILED>")
            return
    else:
        print(f"[INFO] Already exists: {scripts_jar}")

    # Copy to root for convenience
    try:
        shutil.copyfile(scripts_jar, root_jar)
        print(f"[OK] Copied to: {root_jar}")
    except Exception as e:
        print(f"[copy_failed] {e}")

    # Verify adb available
    run_cmd("adb devices")

    # Run verify script
    if shutil.which("python"):
        run_cmd("python .\\scripts\\verify_aab_with_bundletool.py")
    elif shutil.which("py"):
        run_cmd("py -3 .\\scripts\\verify_aab_with_bundletool.py")
    else:
        print("<PYTHON_NOT_FOUND>")


if __name__ == "__main__":
    main()