import json
import re
from pathlib import Path
from shapely.geometry import shape
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.jurisdiction import Jurisdiction
from app.models.station import Station
from app.models.safety_center import SafetyCenter
from app.models.population_stat import PopulationStat
from app.services.jurisdiction_service import normalize_name
from app.models.user import User, UnitType
from app.models.local_unit import LocalUnit
import re

DONG_TO_SIGUNGU_PATH = Path(__file__).resolve().parent.parent / "data" / "dong_to_sigungu.json"
with open(DONG_TO_SIGUNGU_PATH, encoding="utf-8") as f:
    _DONG_TO_SIGUNGU = json.load(f)

SIGUNGU_CODES_PATH = Path(__file__).resolve().parent.parent / "data" / "sigungu_codes.json"

with open(SIGUNGU_CODES_PATH, encoding="utf-8") as f:
    _SIGUNGU_NAMES = sorted(
        {entry["sigungu"] for entry in json.load(f)},
        key=len,
        reverse=True,  
    )

def extract_sigungu(address: str, fallback_name: str = "") -> str:
    if address:
        # 1순위: 주소에 시군구명이 직접 들어있는 경우
        for name in _SIGUNGU_NAMES:
            if name in address:
                return name

        # 2순위: 주소 괄호 안 동명으로 역산 (예: "... (본리동)")
        match = re.search(r"\(([가-힣]+동)\)", address)
        if match:
            dong = match.group(1)
            if dong in _DONG_TO_SIGUNGU:
                return _DONG_TO_SIGUNGU[dong]

    # 3순위: 안전센터/소방서 이름을 동명으로 추정 (예: "정왕119안전센터" → "정왕")
    if fallback_name:
        candidate = normalize_name(fallback_name)
        for dong, sigungu in _DONG_TO_SIGUNGU.items():
            if candidate and candidate in dong:
                return sigungu

    return ""

def get_jurisdiction_sigungu(db: Session, jurisdiction: Jurisdiction) -> str:
    if jurisdiction.safety_center_id:
        center = db.query(SafetyCenter).filter(SafetyCenter.id == jurisdiction.safety_center_id).first()
        if center:
            return extract_sigungu(center.address, fallback_name=center.station_name)
        return ""
    if jurisdiction.station_id:
        station = db.query(Station).filter(Station.id == jurisdiction.station_id).first()
        if station:
            return extract_sigungu(station.address, fallback_name=station.station_name)
        return ""
    if jurisdiction.local_unit_id:
        unit = db.query(LocalUnit).filter(LocalUnit.id == jurisdiction.local_unit_id).first()
        if unit:
            return extract_sigungu(unit.address, fallback_name=unit.station_name)
        return ""
    return ""

def geometry_area(geometry_json: dict) -> float:
    return shape(geometry_json).area

def allocate_population_to_jurisdictions(db: Session, std_ym: str) -> dict:
    jurisdictions = db.query(Jurisdiction).filter(Jurisdiction.is_active == True).all()

    sigungu_groups: dict[str, list] = {}
    no_geometry_jurisdictions: dict[str, list] = {}
    no_sigungu = []

    for j in jurisdictions:
        sigungu = get_jurisdiction_sigungu(db, j)
        if not sigungu:
            no_sigungu.append(j.ward_name)
            continue

        if not j.geometry:
            no_geometry_jurisdictions.setdefault(sigungu, []).append(j)
            continue

        area = geometry_area(j.geometry)
        sigungu_groups.setdefault(sigungu, []).append((j, area))

    allocated, approximated = 0, 0
    empty_population_sigungu = []

    for sigungu in set(list(sigungu_groups.keys()) + list(no_geometry_jurisdictions.keys())):
        entries = sigungu_groups.get(sigungu, [])
        total_area = sum(area for _, area in entries)

        pop_rows = (
            db.query(PopulationStat)
            .filter(
                PopulationStat.std_ym == std_ym,
                or_(
                    PopulationStat.sigungu_nm == sigungu,
                    PopulationStat.sigungu_nm.like(f"{sigungu} %"),
                ),
            )
            .all()
        )
        if not pop_rows:
            empty_population_sigungu.append(sigungu)
            continue

        total_ppltn = sum(p.total_ppltn or 0 for p in pop_rows)
        total_female = sum(p.female_ppltn or 0 for p in pop_rows)
        total_elderly = sum(p.elderly_ppltn or 0 for p in pop_rows)

        # 폴리곤 있는 관할구역: 면적 비율로 정밀 배분
        avg_ppltn, avg_female, avg_elderly = 0, 0, 0
        if total_area > 0:
            for jurisdiction, area in entries:
                ratio = area / total_area
                jurisdiction.allocated_total_ppltn = round(total_ppltn * ratio)
                jurisdiction.allocated_female_ppltn = round(total_female * ratio)
                jurisdiction.allocated_elderly_ppltn = round(total_elderly * ratio)
                jurisdiction.population_std_ym = std_ym
                allocated += 1
            avg_ppltn = sum(j.allocated_total_ppltn for j, _ in entries) / len(entries)
            avg_female = sum(j.allocated_female_ppltn for j, _ in entries) / len(entries)
            avg_elderly = sum(j.allocated_elderly_ppltn for j, _ in entries) / len(entries)
        elif entries:
            # 그 시군구 안에 폴리곤 있는 곳이 하나도 없으면, 시군구 전체를 균등 나눔
            n = len(entries) or 1
            avg_ppltn, avg_female, avg_elderly = total_ppltn / n, total_female / n, total_elderly / n

        # 폴리곤 없는 관할구역: 같은 시군구 평균값으로 근사치 부여
        for jurisdiction in no_geometry_jurisdictions.get(sigungu, []):
            jurisdiction.allocated_total_ppltn = round(avg_ppltn)
            jurisdiction.allocated_female_ppltn = round(avg_female)
            jurisdiction.allocated_elderly_ppltn = round(avg_elderly)
            jurisdiction.population_std_ym = std_ym
            approximated += 1

    db.commit()
    return {
        "allocated": allocated,
        "approximated": approximated,
        "no_sigungu_matched": no_sigungu,
        "empty_population_sigungu": empty_population_sigungu,
    }

def extract_city_name(sigungu_full: str) -> str:
    """'청주시 청원구' 같은 일반구 이름이면 'OO시'만 추출"""
    if " " in sigungu_full:
        return sigungu_full.split(" ")[0]
    return sigungu_full

def get_my_jurisdictions(db: Session, current_user: User) -> list[Jurisdiction]:
    """로그인 사용자 소속의 관할구역 목록 (안전센터/지역대 본인 소속만, 본서는 산하 전체)"""
    if current_user.unit_type == UnitType.SAFETY_CENTER and current_user.safety_center_id:
        return db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id == current_user.safety_center_id,
            Jurisdiction.is_active == True,
        ).all()

    if current_user.unit_type == UnitType.LOCAL_UNIT and current_user.local_unit_id:
        return db.query(Jurisdiction).filter(
            Jurisdiction.local_unit_id == current_user.local_unit_id,
            Jurisdiction.is_active == True,
        ).all()

    center_ids = [
        c.id for c in db.query(SafetyCenter)
        .filter(SafetyCenter.parent_station_id == current_user.station_id)
        .all()
    ]
    unit_ids = [
        u.id for u in db.query(LocalUnit)
        .filter(LocalUnit.parent_station_id == current_user.station_id)
        .all()
    ]

    conditions = []
    if center_ids:
        conditions.append(Jurisdiction.safety_center_id.in_(center_ids))
    if unit_ids:
        conditions.append(Jurisdiction.local_unit_id.in_(unit_ids))
    if not conditions:
        return []

    return db.query(Jurisdiction).filter(
        or_(*conditions),
        Jurisdiction.is_active == True,
    ).all()

def get_my_sigungu_set(db: Session, current_user: User) -> set:
    jurisdictions = get_my_jurisdictions(db, current_user)
    sigungu_set = {get_jurisdiction_sigungu(db, j) for j in jurisdictions}
    sigungu_set.discard(None)
    return sigungu_set