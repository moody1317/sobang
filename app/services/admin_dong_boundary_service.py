# app/services/admin_dong_boundary_service.py
import json
import openpyxl
from sqlalchemy.orm import Session

from app.models.admin_dong_boundary import AdminDongBoundary


def load_admin_dong_boundary_master(db: Session, xlsx_path: str) -> dict:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.worksheets[0]

    created, updated, skipped = 0, 0, 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        admin_code, sido_nm, sigungu_nm, dong_nm, _created_at, closed_at = row
        if not dong_nm or closed_at:   # 읍면동 아닌 상위 행정구역 행, 폐지된 동 제외
            skipped += 1
            continue

        existing = db.query(AdminDongBoundary).filter(AdminDongBoundary.admin_code == admin_code).first()
        if existing:
            existing.dong_nm = dong_nm
            existing.sigungu_nm = sigungu_nm
            existing.sido_nm = sido_nm
            updated += 1
        else:
            db.add(AdminDongBoundary(
                admin_code=admin_code,
                dong_nm=dong_nm,
                sigungu_nm=sigungu_nm,
                sido_nm=sido_nm,
            ))
            created += 1

    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped}


def attach_dong_geometry(db: Session, geojson_path: str) -> dict:
    with open(geojson_path, encoding="utf-8") as f:
        geo = json.load(f)

    matched, unmatched = 0, []
    for feature in geo["features"]:
        admin_code = feature["properties"]["adm_cd2"]
        dong = db.query(AdminDongBoundary).filter(AdminDongBoundary.admin_code == admin_code).first()
        if not dong:
            unmatched.append(admin_code)
            continue
        dong.geometry = feature["geometry"]
        matched += 1

    db.commit()
    return {"matched": matched, "unmatched_count": len(unmatched), "unmatched_codes": unmatched[:30]}
