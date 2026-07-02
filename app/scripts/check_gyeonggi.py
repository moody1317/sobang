# app/scripts/check_gyeonggi.py
from app.services.population_service import fetch_population_raw

TEST_CODES = [
    {"name": "부천시", "code": "4119000000"},
    {"name": "화성시", "code": "4159000000"},
    {"name": "수원시", "code": "4111000000"},
]

if __name__ == "__main__":
    for entry in TEST_CODES:
        print(f"=== {entry['name']} ({entry['code']}) ===")
        raw = fetch_population_raw(
            stdg_cd=entry["code"],
            srch_fr_ym="202604",
            srch_to_ym="202605",
            lv="3",
        )
        print(raw[:800])
        print()