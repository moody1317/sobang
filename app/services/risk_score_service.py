import re
import unicodedata
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.jurisdiction import Jurisdiction
from app.models.jurisdiction_dong import JurisdictionDong
from app.models.admin_dong_boundary import AdminDongBoundary
from app.models.admin_dong_population import AdminDongPopulation
from app.models.fire_incident import FireIncident
from app.models.ems_incident import EmsIncident
from app.models.mountain_accident import MountainAccident
from app.models.fire_target import FireTarget
from app.models.station import Station
from app.models.safety_center import SafetyCenter
from app.models.local_unit import LocalUnit
from app.models.user import User
from app.models.incident import Incident, IncidentType, IncidentStatus
from app.models.notification import NotificationLevel
from app.services.jurisdiction_population_service import extract_sigungu, get_my_jurisdictions
from app.services.weather_warning_service import get_active_warnings_for_jurisdiction, get_weather_warning_weight
from app.services.earthquake_service import get_earthquake_boost_for_jurisdiction
from app.services.notification_service import create_notification

RISK_LEVEL_KO = {"danger": "위험", "caution": "주의", "warning": "경계", "safe": "안전"}
RISK_LEVEL_NOTIF = {
    "danger": NotificationLevel.DANGER,
    "caution": NotificationLevel.CAUTION,
    "warning": NotificationLevel.WARNING,
    "safe": NotificationLevel.SAFE,
}

WEATHER_STRESS_SEVERITY = {0: 0.5, 1: 1.0}  # 0=주의보, 1=경보 — 초기 경험값(위험 스코어 산식 DB 명세서 6장)
COUNT_BASED_KEYS = ["target", "fire", "ems", "mountain", "death", "injury", "damage"]
DONG_ALLOCATED_KEYS = ["fire", "ems", "mountain", "death", "injury", "damage"]  # target은 동 단위 직접 재집계(5.7 ②)

ACTIVE_INCIDENT_POINTS = {
    IncidentType.화재: 10,
    IncidentType.구조: 6,
    IncidentType.구급: 6,
    IncidentType.위험물: 5,
    IncidentType.기타: 2,
}
ACTIVE_INCIDENT_BOOST_CAP = 20

def resolve_risk_level(score: float) -> str:
    if score >= 80:
        return "danger"
    if score >= 50:
        return "caution"
    if score >= 20:
        return "warning"
    return "safe"


def dong_key(sigungu_nm: str, dong_nm: str) -> tuple:
    sigungu_nm = unicodedata.normalize("NFC", sigungu_nm) if sigungu_nm else sigungu_nm
    dong_nm = unicodedata.normalize("NFC", dong_nm) if dong_nm else dong_nm
    return (sigungu_nm, dong_nm)


def _population_key(sigungu_nm: str, dong_nm: str) -> tuple:
    sigungu_nm, dong_nm = dong_key(sigungu_nm, dong_nm)
    if dong_nm:
        dong_nm = dong_nm.replace(".", "")
        dong_nm = re.sub(r"제(\d)", r"\1", dong_nm)
    return (sigungu_nm, dong_nm)


def min_max_normalize(value: float, all_values: list[float]) -> float:
    lo, hi = min(all_values), max(all_values)
    if hi == lo:
        return 0.0
    return (value - lo) / (hi - lo)


def _count_by_safety_center(rows) -> dict:
    counts = {}
    for r in rows:
        if r.safety_center_id is None:
            continue
        counts[r.safety_center_id] = counts.get(r.safety_center_id, 0) + 1
    return counts


def _sum_by_safety_center(rows, field: str) -> dict:
    sums = {}
    for r in rows:
        if r.safety_center_id is None:
            continue
        sums[r.safety_center_id] = sums.get(r.safety_center_id, 0) + float(getattr(r, field))
    return sums


def get_my_dong_boundaries(db: Session, current_user: User) -> list[AdminDongBoundary]:
    jurisdictions = get_my_jurisdictions(db, current_user)
    jurisdiction_ids = [j.id for j in jurisdictions]
    if not jurisdiction_ids:
        return []

    jurisdiction_dongs = (
        db.query(JurisdictionDong).filter(JurisdictionDong.jurisdiction_id.in_(jurisdiction_ids)).all()
    )
    if not jurisdiction_dongs:
        return []

    match_conditions = [
        and_(AdminDongBoundary.sigungu_nm == jd.sigungu_nm, AdminDongBoundary.dong_nm == jd.dong_nm)
        for jd in jurisdiction_dongs
    ]
    candidates = (
        db.query(AdminDongBoundary)
        .filter(AdminDongBoundary.geometry.isnot(None), or_(*match_conditions))
        .all()
    )

    my_dong_keys = {dong_key(jd.sigungu_nm, jd.dong_nm) for jd in jurisdiction_dongs}
    return [b for b in candidates if dong_key(b.sigungu_nm, b.dong_nm) in my_dong_keys]


def get_station_mountain_accident_count(db: Session, station: Station) -> int:
    sigungu = extract_sigungu(station.address, fallback_name=station.station_name)
    if not sigungu:
        return 0
    return db.query(MountainAccident).filter(MountainAccident.gu_nm == sigungu).count()


def get_active_incidents_for_safety_center(db: Session, safety_center_id: int) -> list[Incident]:
    if safety_center_id is None:
        return []
    return (
        db.query(Incident)
        .filter(
            Incident.safety_center_id == safety_center_id,
            Incident.status != IncidentStatus.종료,
            Incident.is_false_alarm == False,  # noqa: E712
        )
        .all()
    )


def active_incident_boost(incidents: list[Incident]) -> float:
    total = sum(ACTIVE_INCIDENT_POINTS.get(i.incident_type, 0) for i in incidents)
    return min(ACTIVE_INCIDENT_BOOST_CAP, total)


def _incident_dong_key(dong_name: str) -> str:
    return unicodedata.normalize("NFC", dong_name) if dong_name else dong_name


def _resolve_jurisdiction_station_id(
    jurisdiction: Jurisdiction, safety_center_parent: dict, local_unit_parent: dict
) -> int | None:
    if jurisdiction.station_id:
        return jurisdiction.station_id
    if jurisdiction.safety_center_id:
        return safety_center_parent.get(jurisdiction.safety_center_id)
    if jurisdiction.local_unit_id:
        return local_unit_parent.get(jurisdiction.local_unit_id)
    return None


def _notify_if_dong_risk_level_changed(
    db: Session, boundary: AdminDongBoundary, station_id: int | None, old_score
) -> None:
    if old_score is None or boundary.risk_score is None:
        return
    old_level = resolve_risk_level(float(old_score))
    new_level = resolve_risk_level(float(boundary.risk_score))
    if old_level == new_level:
        return
    create_notification(
        db,
        level=RISK_LEVEL_NOTIF[new_level],
        source="risk_score",
        title=boundary.dong_nm,
        message=f"{boundary.sigungu_nm} {boundary.dong_nm} 위험도가 {RISK_LEVEL_KO[old_level]}에서 {RISK_LEVEL_KO[new_level]}(으)로 변경되었습니다.",
        station_id=station_id,
    )


def recalculate_active_incident_boost_for_jurisdiction(db: Session, jurisdiction: Jurisdiction) -> None:
    if not jurisdiction.risk_score_breakdown:
        return
    
    incidents = get_active_incidents_for_safety_center(db, jurisdiction.safety_center_id)
    breakdown = dict(jurisdiction.risk_score_breakdown)
    breakdown["active_incident"] = round(active_incident_boost(incidents), 2)

    jurisdiction.risk_score_breakdown = breakdown
    jurisdiction.risk_score = min(100, round(sum(breakdown.values()), 2))
    jurisdiction.risk_score_updated_at = datetime.now()
    db.commit()


def recalculate_active_incident_boost_for_dong(db: Session, incident: Incident) -> None:
    if incident.safety_center_id is None or not incident.dong_name:
        return

    jurisdiction = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.safety_center_id == incident.safety_center_id, Jurisdiction.is_active == True)
        .first()
    )
    if not jurisdiction:
        return

    target_key = _incident_dong_key(incident.dong_name)
    matched_jd = next(
        (
            jd
            for jd in db.query(JurisdictionDong).filter(JurisdictionDong.jurisdiction_id == jurisdiction.id).all()
            if _incident_dong_key(jd.dong_nm) == target_key
        ),
        None,
    )
    if not matched_jd:
        return

    boundary = (
        db.query(AdminDongBoundary)
        .filter(
            AdminDongBoundary.sigungu_nm == matched_jd.sigungu_nm,
            AdminDongBoundary.dong_nm == matched_jd.dong_nm,
        )
        .first()
    )
    if not boundary or not boundary.risk_score_breakdown:
        return

    incidents_in_dong = [
        i
        for i in get_active_incidents_for_safety_center(db, incident.safety_center_id)
        if _incident_dong_key(i.dong_name) == target_key
    ]
    old_score = boundary.risk_score
    breakdown = dict(boundary.risk_score_breakdown)
    breakdown["active_incident"] = round(active_incident_boost(incidents_in_dong), 2)

    boundary.risk_score_breakdown = breakdown
    boundary.risk_score = min(100, round(sum(breakdown.values()), 2))
    boundary.risk_score_updated_at = datetime.now()
    _notify_if_dong_risk_level_changed(db, boundary, incident.station_id, old_score)
    db.commit()


def recalculate_active_incident_boost(db: Session, incident: Incident) -> None:
    if incident.safety_center_id is None:
        return
    jurisdiction = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.safety_center_id == incident.safety_center_id, Jurisdiction.is_active == True)
        .first()
    )
    if jurisdiction:
        recalculate_active_incident_boost_for_jurisdiction(db, jurisdiction)
    recalculate_active_incident_boost_for_dong(db, incident)


def calculate_jurisdiction_risk_scores(db: Session) -> dict:
    jurisdictions = db.query(Jurisdiction).filter(Jurisdiction.is_active == True).all()

    fire_target_counts = _count_by_safety_center(
        db.query(FireTarget).filter(FireTarget.lgz_fire_wktrgt_yn == "Y").all()
    )
    fire_incidents = db.query(FireIncident).all()
    fire_counts = _count_by_safety_center(fire_incidents)
    ems_counts = _count_by_safety_center(db.query(EmsIncident).all())
    death_sums = _sum_by_safety_center(fire_incidents, "dth_cnt")
    injury_sums = _sum_by_safety_center(fire_incidents, "injpsn_cnt")
    damage_sums = _sum_by_safety_center(fire_incidents, "prpt_dam_amt")

    station_mountain_counts = {
        st.id: get_station_mountain_accident_count(db, st) for st in db.query(Station).all()
    }
    parent_station_by_center = {
        c.id: c.parent_station_id for c in db.query(SafetyCenter).all()
    }

    def mountain_count_for(jurisdiction: Jurisdiction) -> int:
        station_id = parent_station_by_center.get(jurisdiction.safety_center_id)
        return station_mountain_counts.get(station_id, 0)

    raw = {
        j.id: {
            "target": fire_target_counts.get(j.safety_center_id, 0),
            "fire": fire_counts.get(j.safety_center_id, 0),
            "ems": ems_counts.get(j.safety_center_id, 0),
            "mountain": mountain_count_for(j),
            "death": death_sums.get(j.safety_center_id, 0),
            "injury": injury_sums.get(j.safety_center_id, 0),
            "damage": damage_sums.get(j.safety_center_id, 0),
        }
        for j in jurisdictions
    }
    all_values = {key: [raw[j.id][key] for j in jurisdictions] for key in COUNT_BASED_KEYS}

    now = datetime.now()
    for j in jurisdictions:
        r = raw[j.id]
        weather_score = min(12.5, sum(
            get_weather_warning_weight(w, now) * WEATHER_STRESS_SEVERITY[w.warn_stress]
            for w in get_active_warnings_for_jurisdiction(db, j)
        ))
        earthquake_score = min(12.5, get_earthquake_boost_for_jurisdiction(db, j, now) / 30 * 12.5)

        breakdown = {
            "forest": float(j.forest_fire_risk_index) / 100 * 15 if j.forest_fire_risk_index is not None else 0,
            "target": min_max_normalize(r["target"], all_values["target"]) * 15,
            "weather": weather_score,
            "earthquake": earthquake_score,
            "fire": min_max_normalize(r["fire"], all_values["fire"]) * 15,
            "ems": min_max_normalize(r["ems"], all_values["ems"]) * 10,
            "mountain": min_max_normalize(r["mountain"], all_values["mountain"]) * 5,
            "death": min_max_normalize(r["death"], all_values["death"]) * 7,
            "injury": min_max_normalize(r["injury"], all_values["injury"]) * 4,
            "damage": min_max_normalize(r["damage"], all_values["damage"]) * 4,
            "active_incident": active_incident_boost(get_active_incidents_for_safety_center(db, j.safety_center_id)),
        }
        j.risk_score = min(100, round(sum(breakdown.values()), 2))
        j.risk_score_breakdown = {k: round(v, 2) for k, v in breakdown.items()}
        j.risk_score_updated_at = now

    db.commit()
    return {"updated": len(jurisdictions)}


def allocate_risk_score_to_dongs(db: Session) -> dict:
    latest = db.query(AdminDongPopulation.std_ym).order_by(AdminDongPopulation.std_ym.desc()).first()
    std_ym = latest[0] if latest else None

    population_lookup = {
        _population_key(p.sigungu_nm, p.dong_nm): p
        for p in db.query(AdminDongPopulation).filter(AdminDongPopulation.std_ym == std_ym).all()
    }
    boundary_lookup = {dong_key(b.sigungu_nm, b.dong_nm): b for b in db.query(AdminDongBoundary).all()}
    jurisdictions = {j.id: j for j in db.query(Jurisdiction).filter(Jurisdiction.is_active == True).all()}
    jurisdiction_dongs = db.query(JurisdictionDong).all()
    safety_center_parent = {c.id: c.parent_station_id for c in db.query(SafetyCenter).all()}
    local_unit_parent = {u.id: u.parent_station_id for u in db.query(LocalUnit).all()}

    jurisdiction_population = {}
    for jd in jurisdiction_dongs:
        pop_row = population_lookup.get(_population_key(jd.sigungu_nm, jd.dong_nm))
        if not pop_row:
            continue
        jurisdiction_population[jd.jurisdiction_id] = (
            jurisdiction_population.get(jd.jurisdiction_id, 0) + pop_row.total_ppltn
        )

    target_counts_by_dong = {}
    for t in db.query(FireTarget).filter(FireTarget.lgz_fire_wktrgt_yn == "Y").all():
        key = dong_key(t.sggu_nm, t.emd_nm)
        target_counts_by_dong[key] = target_counts_by_dong.get(key, 0) + 1
    all_dong_target_counts = [
        target_counts_by_dong.get(dong_key(b.sigungu_nm, b.dong_nm), 0) for b in boundary_lookup.values()
    ]

    active_incidents_by_dong = {}
    for i in db.query(Incident).filter(Incident.status != IncidentStatus.종료, Incident.is_false_alarm == False).all():  # noqa: E712
        key = _incident_dong_key(i.dong_name)
        if not key:
            continue
        active_incidents_by_dong.setdefault(key, []).append(i)

    now = datetime.now()
    updated, skipped = 0, 0

    for jd in jurisdiction_dongs:
        jurisdiction = jurisdictions.get(jd.jurisdiction_id)
        boundary = boundary_lookup.get(dong_key(jd.sigungu_nm, jd.dong_nm))
        pop_row = population_lookup.get(_population_key(jd.sigungu_nm, jd.dong_nm))
        if not jurisdiction or not boundary or not pop_row or not jurisdiction.risk_score_breakdown:
            skipped += 1
            continue

        jur_pop = jurisdiction_population.get(jd.jurisdiction_id, 0)
        pop_ratio = pop_row.total_ppltn / jur_pop if jur_pop else 0

        j_breakdown = jurisdiction.risk_score_breakdown
        dong_breakdown = {key: round(j_breakdown[key] * pop_ratio, 2) for key in DONG_ALLOCATED_KEYS}
        for key in ("forest", "weather", "earthquake"):
            dong_breakdown[key] = j_breakdown[key]

        target_count = target_counts_by_dong.get(dong_key(jd.sigungu_nm, jd.dong_nm), 0)
        dong_breakdown["target"] = round(min_max_normalize(target_count, all_dong_target_counts) * 15, 2)

        elderly_ratio = pop_row.elderly_ppltn / pop_row.total_ppltn if pop_row.total_ppltn else 0
        dong_breakdown["elderly_bonus"] = round(min(5, elderly_ratio * 20), 2)

        dong_incidents = active_incidents_by_dong.get(_incident_dong_key(jd.dong_nm), [])
        dong_breakdown["active_incident"] = round(active_incident_boost(dong_incidents), 2)

        old_score = boundary.risk_score
        boundary.risk_score = min(100, round(sum(dong_breakdown.values()), 2))
        boundary.risk_score_breakdown = dong_breakdown
        boundary.risk_score_updated_at = now
        station_id = _resolve_jurisdiction_station_id(jurisdiction, safety_center_parent, local_unit_parent)
        _notify_if_dong_risk_level_changed(db, boundary, station_id, old_score)
        updated += 1

    db.commit()
    return {"updated": updated, "skipped": skipped, "std_ym": std_ym}