from app.core.database import SessionLocal
from app.models.jurisdiction import Jurisdiction
from app.models.jurisdiction_dong import JurisdictionDong
from app.models.admin_dong_boundary import AdminDongBoundary
from app.models.admin_dong_population import AdminDongPopulation

if __name__ == "__main__":
    db = SessionLocal()

    latest = db.query(AdminDongPopulation.std_ym).order_by(AdminDongPopulation.std_ym.desc()).first()
    std_ym = latest[0] if latest else None

    population_keys = {
        (p.sigungu_nm, p.dong_nm.replace(".", "") if p.dong_nm else p.dong_nm)
        for p in db.query(AdminDongPopulation).filter(AdminDongPopulation.std_ym == std_ym).all()
    }

    boundary_keys = {(b.sigungu_nm, b.dong_nm) for b in db.query(AdminDongBoundary).all()}
    jurisdictions = {j.id: j for j in db.query(Jurisdiction).filter(Jurisdiction.is_active == True).all()}
    jurisdiction_dongs = db.query(JurisdictionDong).all()

    no_jurisdiction, no_boundary, no_population, no_score, ok = 0, 0, 0, 0, 0
    sample_no_boundary = []
    sample_no_population = []

    for jd in jurisdiction_dongs:
        jurisdiction = jurisdictions.get(jd.jurisdiction_id)
        key = (jd.sigungu_nm, jd.dong_nm)

        if not jurisdiction:
            no_jurisdiction += 1
            continue
        if key not in boundary_keys:
            no_boundary += 1
            if len(sample_no_boundary) < 15:
                sample_no_boundary.append(key)
            continue
        population_key = (jd.sigungu_nm, jd.dong_nm.replace(".", "") if jd.dong_nm else jd.dong_nm)
        if population_key not in population_keys:
            no_population += 1
            if len(sample_no_population) < 15:
                sample_no_population.append(key)
            continue
        if not jurisdiction.risk_score_breakdown:
            no_score += 1
            continue
        ok += 1

    print("전체 jurisdiction_dongs:", len(jurisdiction_dongs))
    print("정상 처리 가능:", ok)
    print("스킵 — 관할구역 없음(비활성/미존재):", no_jurisdiction)
    print("스킵 — 경계(admin_dong_boundaries) 매칭 실패:", no_boundary)
    print("스킵 — 인구(admin_dong_populations) 매칭 실패:", no_population)
    print("스킵 — 관할구역 점수 미계산:", no_score)
    print("\n경계 매칭 실패 예시 (sigungu_nm, dong_nm):")
    for s in sample_no_boundary:
        print(" -", s)
    print("\n인구 매칭 실패 예시 (sigungu_nm, dong_nm):")
    for s in sample_no_population:
        print(" -", s)

    # 청주시만 따로 집계
    cj_dongs = [jd for jd in jurisdiction_dongs if jd.sigungu_nm and "청주시" in jd.sigungu_nm]
    print(f"\n=== 청주시만: 전체 {len(cj_dongs)} ===")
    for jd in cj_dongs:
        population_key = (jd.sigungu_nm, jd.dong_nm.replace(".", "") if jd.dong_nm else jd.dong_nm)
        status = "OK" if key in boundary_keys and population_key in population_keys else "SKIP"
        if status == "SKIP":
            print(" -", key, "boundary" if key not in boundary_keys else "", "population" if population_key not in population_keys else "")