import requests

from app.core.config import settings


def fetch_station_data(page_no: int = 1, num_of_rows: int = 10):
    url = settings.STATION_API_BASE_URL

    params = {
        "serviceKey": settings.STATION_API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "returnType": "XML",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return {
        "request_url": response.url,
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type"),
        "body_preview": response.text[:5000],
    }
