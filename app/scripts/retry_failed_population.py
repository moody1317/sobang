from app.core.database import SessionLocal
from app.services.population_service import (
    fetch_total_count, fetch_population_raw, parse_population_xml, upsert_population_stats
)

FAILED_CODES = [
    {"code": "4146100000", "sigungu": "용인시 처인구"},
    {"code": "4146500000", "sigungu": "용인시 수지구"},
]

if __name__ == "__main__":
    db = SessionLocal()
    srch_fr_ym, srch_to_ym = "202604", "202605"

    for entry in FAILED_CODES:
        code = entry["code"]
        try:
            total_count = fetch_total_count(code, srch_fr_ym, srch_to_ym, lv="3")
            print(f"[{entry['sigungu']}] total_count = {total_count}")

            num_of_rows = 100
            total_pages = (total_count + num_of_rows - 1) // num_of_rows
            print(f"[{entry['sigungu']}] total_pages = {total_pages}")

            for page in range(1, total_pages + 1):
                raw_xml = fetch_population_raw(
                    code, srch_fr_ym, srch_to_ym, lv="3",
                    page_no=page, num_of_rows=num_of_rows,
                )
                parsed = parse_population_xml(raw_xml)
                print(f"[{entry['sigungu']}] page {page} parsed count = {len(parsed)}")
                result = upsert_population_stats(db, parsed)
                print(entry["sigungu"], page, result)

        except Exception as e:
            print(f"[{entry['sigungu']}] 에러 발생: {e}")