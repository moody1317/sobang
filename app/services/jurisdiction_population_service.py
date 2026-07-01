import json
import re
from pathlib import Path
from shapely.geometry import shape
from sqlalchemy.orm import Session

from app.models.jurisdiction import Jurisdiction
from app.models.station import Station
from app.models.safety_center import SafetyCenter
from app.models.population_stat import PopulationStat

SIGUNGU_CODES_PATH = Path(__file__).resolve().parent.parent / "data" / "sigungu_codes.json"

with open(SIGUNGU_CODES_PATH, encoding="utf-8") as f:
    _SIGUNGU_NAMES = sorted(
        {entry["sigungu"] for entry in json.load(f)},
        key=len,
        reverse=True,  
    )


def extract_sigungu(address: str) -> str:
    if not address:
        return ""
    for name in _SIGUNGU_NAMES:
        if name in address:
            return name
    return ""

def get_jurisdiction_sigungu(db: Session, jurisdiction: Jurisdiction) -> str:
    if jurisdiction.safety_center_id:
        center = db.query(SafetyCenter).filter(SafetyCenter.id == jurisdiction.safety_center_id).first()
        return extract_sigungu(center.address if center else "")
    if jurisdiction.station_id:
        station = db.query(Station).filter(Station.id == jurisdiction.station_id).first()
        return extract_sigungu(station.address if station else "")
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

        pop_rows = (
            db.query(PopulationStat)
            .filter(PopulationStat.sigungu_nm == sigungu, PopulationStat.std_ym == std_ym)
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