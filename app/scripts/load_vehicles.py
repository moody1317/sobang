import re
from app.core.database import SessionLocal
from app.models.station import Station
from app.models.safety_center import SafetyCenter
from app.models.rescue_unit import RescueUnit
from app.models.vehicle import Vehicle, VehicleType

STATION_NAME = "청주동부소방서"

SAFETY_CENTER_FLEET = {
    "영운119안전센터": ["중형펌프차", "소형펌프차", "물탱크차", "조연차", "소형사다리차(15M)", "고가차(53M)", "구급차2", "생활안전구조차", "오토바이"],
    "사천119안전센터": ["중형펌프차", "소형펌프차", "굴절차(69M)", "구급차", "순찰차"],
    "북문119안전센터": ["중형펌프차", "소형펌프차", "구급차2", "음압구급차", "순찰차"],
    "문의119안전센터": ["중형펌프차2", "구급차", "순찰차", "소형펌프차"],
    "미원119안전센터": ["중형펌프차", "구급차"],
    "내수119안전센터": ["대형펌프차", "소형펌프차", "구급차", "순찰차"],
    "오창119안전센터": ["중형펌프차", "물탱크차", "화학차", "구급차", "생활안전구조차", "구조공작차"],
}
RESCUE_UNIT_FLEET = ["구조공작차", "구조버스", "생활안전구조차", "트레일러"]

def parse_vehicle(raw: str) -> tuple[str, int]:
    name = re.sub(r"\([^)]*\)", "", raw)
    m = re.match(r"^(.*?)(\d+)$", name)
    if m:
        return m.group(1), int(m.group(2))
    return name, 1

def add_vehicles(db, names: list[str], **owner_kwargs):
    added, skipped = 0, []
    for raw in names:
        type_name, count = parse_vehicle(raw)
        try:
            vehicle_type = VehicleType(type_name)
        except ValueError:
            skipped.append(raw)
            continue
        db.add(Vehicle(vehicle_type=vehicle_type, count=count, **owner_kwargs))
        added += 1
    return added, skipped

def load_vehicles():
    db = SessionLocal()
    if db.query(Vehicle).first():
        print("vehicles 테이블에 이미 데이터가 있습니다. 건너뜀")
        return

    station = db.query(Station).filter(
        Station.station_name.like(f"%{STATION_NAME}%"), Station.unit_type == "본서"
    ).first()
    if not station:
        print(f"{STATION_NAME}를 찾을 수 없습니다.")
        return

    for center_name, fleet in SAFETY_CENTER_FLEET.items():
        center = db.query(SafetyCenter).filter(
            SafetyCenter.station_name.like(f"%{center_name}%"),
            SafetyCenter.parent_station_id == station.id,
        ).first()
        if not center:
            print(f" - {center_name} 안전센터를 못 찾음")
            continue
        added, skipped = add_vehicles(db, fleet, safety_center_id=center.id)
        print(f" - {center_name}: {added}건 추가" + (f" (제외: {skipped})" if skipped else ""))

    rescue_unit = db.query(RescueUnit).filter(RescueUnit.parent_station_id == station.id).first()
    if rescue_unit:
        added, skipped = add_vehicles(db, RESCUE_UNIT_FLEET, rescue_unit_id=rescue_unit.id)
        print(f" - {rescue_unit.station_name}: {added}건 추가" + (f" (제외: {skipped})" if skipped else ""))
    else:
        print(f" - {STATION_NAME} 산하 구조대를 못 찾음")

    db.commit()

if __name__ == "__main__":
    load_vehicles()
