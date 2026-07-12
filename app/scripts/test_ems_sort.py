import json
from app.services.ems_incident_service import fetch_ems_incidents_raw

if __name__ == "__main__":
    for sort_field in ["dclrYmd,desc", "gtrRegDt,desc"]:
        result = fetch_ems_incidents_raw(page=1, size=3, sort=sort_field)
        print(f"=== sort={sort_field} ===")
        print([i.get("dclrYmd") for i in result["items"]])
        print([i.get("gtrRegDt") for i in result["items"]])