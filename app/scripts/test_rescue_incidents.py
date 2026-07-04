# app/scripts/test_rescue_incidents.py
from app.services.rescue_incident_service import fetch_rescue_incidents_raw

if __name__ == "__main__":
    r1 = fetch_rescue_incidents_raw(page=1, size=3)
    print("전체 건수:", r1["total"])
    print("샘플:", [(i.get("cntrNm"), i.get("dclrYmd")) for i in r1["items"]])

    r2 = fetch_rescue_incidents_raw(page=1, size=3, sort="dclrYmd,desc")
    print("최신순:", [i.get("dclrYmd") for i in r2["items"]])

    r3 = fetch_rescue_incidents_raw(page=1, size=5, sort="gtrRegDt,desc")
    print("gtrRegDt 최신순:", [(i.get("dclrYmd"), i.get("clmtyRscuRptpNo")) for i in r3["items"]])