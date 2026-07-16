# app/scripts/check_admin_dong_population.py
from app.core.database import SessionLocal
from app.models.admin_dong_population import AdminDongPopulation
from app.models.admin_dong_boundary import AdminDongBoundary

if __name__ == "__main__":
    db = SessionLocal()

    total = db.query(AdminDongPopulation).count()
    print("admin_dong_populations 전체 행 수:", total)

    std_yms = sorted({row[0] for row in db.query(AdminDongPopulation.std_ym).distinct().all()})
    print("적재된 std_ym 목록:", std_yms)

    cj_rows = db.query(AdminDongPopulation).filter(AdminDongPopulation.sigungu_nm.like("청주시%")).all()
    print(f"\n청주시 인구 행 수: {len(cj_rows)}")
    for r in cj_rows[:10]:
        print(f" - {r.dong_nm} (admin_code={r.admin_code}, std_ym={r.std_ym}) "
              f"총 {r.total_ppltn} / 남 {r.male_ppltn} / 여 {r.female_ppltn} / 고령 {r.elderly_ppltn}")

    bokdae = [r for r in cj_rows if r.dong_nm and "복대" in r.dong_nm]
    print("\n복대 관련 동 (분리 확인용):", [(r.dong_nm, r.total_ppltn) for r in bokdae])

    null_gender = [r for r in cj_rows if r.male_ppltn is None or r.female_ppltn is None]
    print("성별 인구 NULL인 행:", len(null_gender))

    cj_boundary_codes = {
        b.admin_code for b in db.query(AdminDongBoundary).filter(AdminDongBoundary.sigungu_nm.like("청주시%")).all()
    }
    cj_population_codes = {r.admin_code for r in cj_rows}
    print(f"\n청주시 — 경계는 있는데 인구 없는 동: {sorted(cj_boundary_codes - cj_population_codes)}")
    print(f"청주시 — 인구는 있는데 경계 없는 동: {sorted(cj_population_codes - cj_boundary_codes)}")
