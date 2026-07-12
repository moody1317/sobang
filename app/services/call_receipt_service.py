import json
import subprocess
from urllib.parse import quote
from app.core.config import settings

CALL_RECEIPTS_URL = "https://www.bigdata-119.kr/fsdpApi/rest/v1/call-receipts"


def fetch_call_receipts_raw(page: int = 1, size: int = 20, q: str = None, sort: str = None) -> dict:
    url = f"{CALL_RECEIPTS_URL}?page={page}&size={size}"
    if q:
        url += f"&q={quote(q)}"
    if sort:
        url += f"&sort={quote(sort)}"

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", url, "-H", f"X-API-KEY: {settings.EMS_API_KEY}"],
        capture_output=True, text=True, timeout=30, encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl 실행 실패: {result.stderr}")
    if not result.stdout.strip():
        raise RuntimeError(f"빈 응답. stderr: {result.stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("JSON 파싱 실패, 원문:")
        print(result.stdout[:1000])
        raise