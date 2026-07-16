# app/scripts/normalize_jurisdiction_dongs_to_admin_dong.py
import openpyxl
from app.core.database import SessionLocal
from app.models.jurisdiction_dong import JurisdictionDong
from app.models.admin_dong_boundary import AdminDongBoundary

KIKMIX_PATH = "app/data/KIKmix_20260701.xlsx"


def load_legal_to_admin_map(xlsx_path: str) -> dict:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.worksheets[0]

    mapping = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        _admin_code, _sido_nm, sigungu_nm, admin_dong_nm, _legal_code, legal_dong_nm, _created_at, closed_at = row
        if not admin_dong_nm or not legal_dong_nm or closed_at:
            continue
        key = (sigungu_nm, legal_dong_nm)
        mapping.setdefault(key, set()).add(admin_dong_nm)
    return mapping


if __name__ == "__main__":
    db = SessionLocal()
    legal_to_admin = load_legal_to_admin_map(KIKMIX_PATH)
    boundary_keys = {(b.sigungu_nm, b.dong_nm) for b in db.query(AdminDongBoundary).all()}

    resolved, expanded, unresolved = 0, 0, []

    for jd in db.query(JurisdictionDong).all():
        key = (jd.sigungu_nm, jd.dong_nm)
        if key in boundary_keys:
            continue  # 이미 행정동 이름으로 매칭됨 — 건드릴 필요 없음

        candidates = sorted(legal_to_admin.get(key, []))
        resolved_sigungu = jd.sigungu_nm

        if not candidates and jd.sigungu_nm and " " in jd.sigungu_nm:
            # '가평군 청평면 대성리'처럼 읍/면까지 시군구 자리에 같이 묶여 들어온 3단계 주소 보정 —
            # 시군구 앞부분만 떼어 재시도 (KIKmix의 시군구명은 읍/면을 포함하지 않음)
            short_sigungu = jd.sigungu_nm.split(" ")[0]
            candidates = sorted(legal_to_admin.get((short_sigungu, jd.dong_nm), []))
            resolved_sigungu = short_sigungu

        if not candidates:
            unresolved.append(key)
            continue

        jd.sigungu_nm = resolved_sigungu
        jd.dong_nm = candidates[0]
        resolved += 1
        for extra in candidates[1:]:
            db.add(JurisdictionDong(
                jurisdiction_id=jd.jurisdiction_id,
                sigungu_nm=resolved_sigungu,
                dong_nm=extra,
                display_name=jd.display_name,
                split_ratio=jd.split_ratio,
            ))
            expanded += 1

    db.commit()
    print(f"법정동→행정동 치환: {resolved}건, 1:N 매핑으로 행 추가: {expanded}건, 매핑 실패(여전히 미해결): {len(unresolved)}건")
    for u in unresolved[:30]:
        print(" -", u)