# app/scripts/test_ems_debug2.py
from app.services.ems_incident_service import fetch_ems_incidents_raw

if __name__ == "__main__":
    r_page1 = fetch_ems_incidents_raw(page=1, size=3)
    r_page2 = fetch_ems_incidents_raw(page=2, size=3)
    print("page1:", [i["rlfRptpNo"] for i in r_page1["items"]])
    print("page2:", [i["rlfRptpNo"] for i in r_page2["items"]])

    r_sorted = fetch_ems_incidents_raw(page=1, size=3, sort="dsptYmd,asc")
    print("정렬(asc):", [i["dsptYmd"] for i in r_sorted["items"]])

    r_exact = fetch_ems_incidents_raw(page=1, size=3, dspt_ymd_prefix="20250609")
    print("정확값 필터 total:", r_exact["total"])

    # https://www.bigdata-119.kr/fsdpApi/rest/v1/ems-incidents?page=1&size=3
    # https://www.bigdata-119.kr/fsdpApi/rest/v1/ems-incidents?page=2&size=3
    # https://www.bigdata-119.kr/fsdpApi/rest/v1/ems-incidents?page=1&size=3&sort=dsptYmd,ascx
    # https://www.bigdata-119.kr/fsdpApi/rest/v1/ems-incidents?page=1&size=3&dsptYmd=20250609