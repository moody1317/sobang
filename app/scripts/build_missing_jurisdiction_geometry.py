# app/scripts/build_missing_jurisdiction_geometry.py
"""VWorld WFS가 geometry를 안 주는 관할구역(예: 영운/사천119안전센터)을 위한 보정 스크립트.
jurisdiction_dongs에 매핑된 admin_dong_boundaries.geometry를 합쳐서 Jurisdiction.geometry를 채운다.
VWorld가 원래 주는 값이 아니라 행정동 경계로 근사한 값이므로, load_jurisdictions.py를 다시 돌려도
이 관할구역들은 갱신되지 않는다 (ward_id가 없는 수동 보정 데이터)."""
import unicodedata
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from app.core.database import SessionLocal
from app.models.jurisdiction import Jurisdiction
from app.models.jurisdiction_dong import JurisdictionDong
from app.models.admin_dong_boundary import AdminDongBoundary


def _key(sigungu_nm: str, dong_nm: str) -> tuple:
    sigungu_nm = unicodedata.normalize("NFC", sigungu_nm) if sigungu_nm else sigungu_nm
    dong_nm = unicodedata.normalize("NFC", dong_nm) if dong_nm else dong_nm
    return (sigungu_nm, dong_nm)


def to_multipolygon_geojson(geom) -> dict:
    """shapely Polygon/MultiPolygon 결과를 to_multipolygon()과 같은 GeoJSON 형태로 통일."""
    geo = mapping(geom)
    if geo["type"] == "Polygon":
        return {"type": "MultiPolygon", "coordinates": [geo["coordinates"]]}
    return {"type": "MultiPolygon", "coordinates": list(geo["coordinates"])}


def _geometry_missing(geometry) -> bool:
    """NULL은 물론, {} 같은 빈 값이나 좌표가 없는 값도 '누락'으로 취급한다."""
    if not geometry:
        return True
    return not geometry.get("coordinates")


def build_missing_jurisdiction_geometry(db) -> dict:
    boundary_lookup = {
        _key(b.sigungu_nm, b.dong_nm): b
        for b in db.query(AdminDongBoundary).filter(AdminDongBoundary.geometry.isnot(None)).all()
    }

    targets = [j for j in db.query(Jurisdiction).all() if _geometry_missing(j.geometry)]

    filled, skipped = [], []
    for j in targets:
        dongs = db.query(JurisdictionDong).filter(JurisdictionDong.jurisdiction_id == j.id).all()
        shapes = []
        missing_dongs = []
        for jd in dongs:
            boundary = boundary_lookup.get(_key(jd.sigungu_nm, jd.dong_nm))
            if boundary is None:
                missing_dongs.append(jd.dong_nm)
                continue
            shapes.append(shape(boundary.geometry))

        if not shapes:
            skipped.append({"jurisdiction_id": j.id, "ward_name": j.ward_name, "reason": "매핑된 동 경계 없음"})
            continue

        merged = unary_union(shapes)
        j.geometry = to_multipolygon_geojson(merged)
        filled.append({"jurisdiction_id": j.id, "ward_name": j.ward_name, "dong_count": len(shapes), "missing": missing_dongs})

    db.commit()
    return {"filled": filled, "skipped": skipped}


if __name__ == "__main__":
    db = SessionLocal()
    result = build_missing_jurisdiction_geometry(db)

    print(f"채움: {len(result['filled'])}건")
    for f in result["filled"]:
        note = f" (경계 없는 동 {f['missing']} 제외)" if f["missing"] else ""
        print(f" - [{f['jurisdiction_id']}] {f['ward_name']}: 동 {f['dong_count']}개 합성{note}")

    print(f"스킵: {len(result['skipped'])}건")
    for s in result["skipped"]:
        print(f" - [{s['jurisdiction_id']}] {s['ward_name']}: {s['reason']}")