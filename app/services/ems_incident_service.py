# app/services/ems_incident_service.py
import json
import subprocess
from app.core.config import settings


def fetch_ems_incidents_raw(page: int = 1, size: int = 20, dspt_ymd_prefix: str = None, q: str = None, sort: str = None) -> dict:
    url = f"{settings.EMS_API_BASE_URL}?page={page}&size={size}"
    if dspt_ymd_prefix:
        url += f"&dsptYmd={dspt_ymd_prefix}"
    if q:
        url += f"&q={q}"
    if sort:
        url += f"&sort={sort}"

    print("DEBUG URL:", url)

    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST", url,
            "-H", f"X-API-KEY: {settings.EMS_API_KEY}",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"curl 실행 실패: {result.stderr}")

    return json.loads(result.stdout)


def fetch_ems_incidents_preview(page: int = 1, size: int = 3) -> dict:
    return fetch_ems_incidents_raw(page=page, size=size)