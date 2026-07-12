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
    return ""

def geometry_area(geometry_json: dict) -> float:
    return shape(geometry_json).area

def allocate_population_to_jurisdictions(db: Session, std_ym: str) -> dict:
    jurisdictions = db.query(Jurisdiction).filter(Jurisdiction.is_active == True).all()

    sigungu_groups: dict[str, list] = {}
    no_sigungu = []

    for j in jurisdictions:
        sigungu = get_jurisdiction_sigungu(db, j)
        if not sigungu:
            no_sigungu.append(j.ward_name)
            continue
        area = geometry_area(j.geometry)
        sigungu_groups.setdefault(sigungu, []).append((j, area))

    allocated = 0
    empty_population_sigungu = []

    for sigungu, entries in sigungu_groups.items():
        total_area = sum(area for _, area in entries)
        if total_area == 0:
            continue

        # 정확히 일치하는 것 + "OO시 OO구"처럼 하위 일반구까지 포함해서 다 합산
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

        for jurisdiction, area in entries:
            ratio = area / total_area
            jurisdiction.allocated_total_ppltn = round(total_ppltn * ratio)
            jurisdiction.allocated_female_ppltn = round(total_female * ratio)
            jurisdiction.allocated_elderly_ppltn = round(total_elderly * ratio)
            jurisdiction.population_std_ym = std_ym
            allocated += 1

    db.commit()
    return {
        "allocated": allocated,
        "no_sigungu_matched": no_sigungu,
        "empty_population_sigungu": empty_population_sigungu,
    }

def extract_city_name(sigungu_full: str) -> str:
    """'청주시 청원구' 같은 일반구 이름이면 'OO시'만 추출"""
    if " " in sigungu_full:
        return sigungu_full.split(" ")[0]
    return sigungu_full