import re
from app.core.database import SessionLocal
from app.models.station import Station
from app.models.safety_center import SafetyCenter
from app.models.ambulance_unit import AmbulanceUnit
from app.models.aviation_unit import AviationUnit
from app.models.special_response_unit import SpecialResponseUnit
from app.models.local_unit import LocalUnit

TYPE_TABLE_MAP = {
    "안전센터": SafetyCenter,
    "구급대": AmbulanceUnit,
    "항공대": AviationUnit,
    "특수대응단": SpecialResponseUnit,
    "지역대": LocalUnit,
}


def extract_district(address: str) -> str:
    match = re.search(r"(\S+[시군구])", address or "")
    return match.group(1) if match else ""


def split_stations():
    db = SessionLocal()
    headquarters = db.query(Station).filter(Station.unit_type == "본서").all()

    counts = {k: 0 for k in TYPE_TABLE_MAP}

    for unit_type, model in TYPE_TABLE_MAP.items():
        items = db.query(Station).filter(Station.unit_type == unit_type).all()

        for item in items:
            district = extract_district(item.address)
            parent = next((hq for hq in headquarters if district and district in (hq.address or "")), None)

            db.add(model(
                station_code=item.station_code,
                station_name=item.station_name,
                address=item.address,
                phone_number=item.phone_number,
                parent_station_id=parent.id if parent else None,
            ))
            counts[unit_type] += 1

    db.commit()
    return counts


if __name__ == "__main__":
    result = split_stations()
    print(result)