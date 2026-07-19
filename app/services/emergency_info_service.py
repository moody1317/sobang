from functools import lru_cache
import requests
from app.core.config import settings

SIDO_ABBR_MAP = {
    "서울특별시": "서울소방재난본부",
    "경기도": "경기도소방재난본부",
    "충청북도": "충북소방본부",
    "충청남도": "충청남도재난본부",
    "대전광역시": "대전소방본부",
    "제주특별자치도": "제주소방안전본부",
    "대구광역시": "대구소방본부",
    "인천광역시": "인천소방본부",
    "광주광역시": "광주소방본부",
    "부산광역시": "부산소방본부",
    "강원특별자치도": "강원소방본부",
    "세종특별자치시": "세종소방본부",
    "전라남도": "전남소방본부",
    "전북특별자치도": "전북소방본부",
    "울산광역시": "울산소방본부",
    "경상남도": "경남소방본부",
    "경상북도": "경북소방본부",
}

LATEST_EMS_STAT_MONTH = "202512"

def fetch_emg_patient_transfer_info(
    station_name: str,
    stmt_ym: str,
    sido_name: str = None,
    page_no: int = 1,
    num_of_rows: int = 100,
) -> dict:
    params = {
        "serviceKey": settings.EMERGENCY_INFO_API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "resultType": "json",
        "rsacGutFsttOgidNm": station_name,
        "stmtYm": stmt_ym,
    }
    if sido_name:
        params["sidoHqOgidNm"] = sido_name

    response = requests.get(settings.EMERGENCY_INFO_API_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def extract_short_station_name(full_name: str) -> str:
    for direction in ["동부", "서부", "남부", "북부", "중부"]:
        if direction in full_name and full_name.endswith("소방서"):
            return direction + "소방서"
    return full_name

def get_recent_ems_months(count: int = 3) -> list[str]:
    year = int(LATEST_EMS_STAT_MONTH[:4])
    month = int(LATEST_EMS_STAT_MONTH[4:6])

    months = []
    for _ in range(count):
        months.append(f"{year}{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return months

@lru_cache(maxsize=256)  # 정부 API 페이지네이션 호출이 수십 초 걸림 — LATEST_EMS_STAT_MONTH는 코드 배포로만 바뀌므로 프로세스 재시작이 곧 무효화
def get_ems_hourly_buckets(station_name: str, sido_full_name: str) -> dict:
    short_name = extract_short_station_name(station_name)
    sido_name = SIDO_ABBR_MAP.get(sido_full_name)

    buckets = {"심야": 0, "오전": 0, "오후": 0, "저녁": 0}
    total = 0

    if not sido_name:
        return {"buckets": buckets, "total": total}

    for ym in get_recent_ems_months():
        try:
            page = 1
            while True:
                result = fetch_emg_patient_transfer_info(
                    short_name, ym, sido_name=sido_name, page_no=page, num_of_rows=100
                )
                body = result.get("body", {})
                items = body.get("items", [])
                if not items:
                    break

                for item in items:
                    hh = item.get("stmtHh")
                    if not hh:
                        continue
                    hour = int(hh)
                    total += 1
                    if 0 <= hour < 6:
                        buckets["심야"] += 1
                    elif 6 <= hour < 12:
                        buckets["오전"] += 1
                    elif 12 <= hour < 18:
                        buckets["오후"] += 1
                    else:
                        buckets["저녁"] += 1

                grand_total = int(body.get("totalCount") or result.get("totalCount", 0))
                if page * 100 >= grand_total:
                    break
                page += 1
        except Exception:
            continue

    return {"buckets": buckets, "total": total}