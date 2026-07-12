# app/scripts/test_pwn_cd.py
import json
from app.services.weather_warning_service import fetch_pwn_cd

if __name__ == "__main__":
    result = fetch_pwn_cd(stn_id="108")
    items = result.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    print("건수:", len(items))
    print("특보종류 분포:", set(i.get("warnVar") for i in items))