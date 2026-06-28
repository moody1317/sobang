import requests
from app.core.config import settings

def fetch_safety_center_api():
    url = "여기에_API_엔드포인트_URL"
    params = {
        "serviceKey": settings.SAFETY_CENTER_API_KEY,  # .env에 추가 필요
        "type": "json",
        "numOfRows": 1000,
        "pageNo": 1,
    }
    response = requests.get(url, params=params, timeout=15)
    return response.json()


if __name__ == "__main__":
    data = fetch_safety_center_api()

    # 실제 응답 구조에 맞게 경로 조정 필요 (예: data["response"]["body"]["items"])
    items = data.get("response", {}).get("body", {}).get("items", [])
    api_center_names = [item.get("119안전센터명", "") for item in items]

    print("API에서 받은 개수:", len(api_center_names))

    unmatched_50 = [
        "미근119안전센터", "신도119안전센터", "감북119안전센터", "경안119안전센터",
        "수진119안전센터", "독산119안전센터", "기장119안전센터", "차룡119안전센터",
        "동천119안전센터", "둔산119안전센터", "율량안전센터", "사내119안전센터",
        "현남북119안전센터", "지좌119안전센터", "소룡119안전센터", "비응119소방정안전센터",
        "남중119안전센터", "송지안전센터", "관산안전센터", "항만119센터",
        "안좌안전센터", "추자지역119센터", "삼문119안전센터", "삼진119안전센터",
        "사천읍119안전센터", "연동119센터", "삼도119센터", "오라119센터",
        "이도119센터", "화북119센터",
    ]

    for name in unmatched_50:
        if any(name in api_name or api_name in name for api_name in api_center_names):
            print(f"✅ {name} - API에 있음")
        else:
            print(f"❌ {name} - API에도 없음")