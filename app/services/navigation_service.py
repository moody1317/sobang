import requests
from app.core.config import settings

KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"

def fetch_route(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> dict:
    headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}
    params = {
        "origin": f"{origin_lng},{origin_lat}",
        "destination": f"{dest_lng},{dest_lat}",
        "priority": "RECOMMEND",
    }
    response = requests.get(KAKAO_DIRECTIONS_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    route = data["routes"][0]
    summary = route["summary"]

    path = []
    guides = []
    for section in route["sections"]:
        for road in section["roads"]:
            vertexes = road["vertexes"]
            for i in range(0, len(vertexes), 2):
                path.append({"lat": vertexes[i + 1], "lng": vertexes[i]})
        for guide in section["guides"]:
            guides.append({
                "name": guide["name"],
                "distance": guide["distance"],
                "guidance": guide["guidance"],
                "lat": guide["y"],
                "lng": guide["x"],
            })

    return {
        "distance_m": summary["distance"],
        "duration_s": summary["duration"],
        "path": path,
        "guides": guides,
    }