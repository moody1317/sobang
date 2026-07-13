# app/scripts/discover_sejong.py
from app.services.emergency_info_service import fetch_emg_patient_transfer_info

PROBE_STATIONS = ["세종남부소방서", "세종북부소방서", "세종소방서", "조치원소방서"]

STMT_YM = "202512"

if __name__ == "__main__":
    for station in PROBE_STATIONS:
        result = fetch_emg_patient_transfer_info(station_name=station, stmt_ym=STMT_YM)
        items = result.get("body", {}).get("items", [])
        total = result.get("body", {}).get("totalCount") or result.get("totalCount")
        sido_values = {item.get("sidoHqOgidNm") for item in items}
        print(f"{station} (총 {total}건) → {sido_values}")