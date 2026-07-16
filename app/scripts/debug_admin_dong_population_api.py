# app/scripts/debug_admin_dong_population_api.py
from app.services.admin_dong_population_service import fetch_admin_dong_population_raw, parse_admin_dong_population

TARGET_SIGUNGU = {
    "청주시 상당구": "4311100000",
    "청주시 서원구": "4311200000",
    "청주시 흥덕구": "4311300000",
    "청주시 청원구": "4311400000",
}

if __name__ == "__main__":
    for name, code in TARGET_SIGUNGU.items():
        raw = fetch_admin_dong_population_raw(admm_cd=code, srch_fr_ym="202604", srch_to_ym="202605")
        items = parse_admin_dong_population(raw)
        dong_names = sorted({item.get("dongNm") for item in items})
        print(f"=== {name} ({code}) — 응답 동 개수: {len(dong_names)} ===")
        for d in dong_names:
            print(" -", d)
        print()
