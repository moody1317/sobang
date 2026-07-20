import requests
from app.core.config import settings

KAKAO_CATEGORY_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/category.json"

def count_nearby_category(category_code: str, lat: float, lon: float, radius_m: int) -> int:
    headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}
    params = {"category_group_code": category_code, "x": lon, "y": lat, "radius": radius_m}
    response = requests.get(KAKAO_CATEGORY_SEARCH_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["meta"]["total_count"]
