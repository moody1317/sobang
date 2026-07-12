# app/scripts/debug_ems_page.py
import subprocess
from app.core.config import settings

if __name__ == "__main__":
    url = f"{settings.EMS_API_BASE_URL}?page=38&size=100&sort=dclrYmd,desc"
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", url, "-H", f"X-API-KEY: {settings.EMS_API_KEY}"],
        capture_output=True, text=True, timeout=60, encoding="utf-8",
    )
    print("returncode:", result.returncode)
    print("stdout 길이:", len(result.stdout))
    print("stderr:", repr(result.stderr))
    print("stdout 앞부분:", result.stdout[:500])