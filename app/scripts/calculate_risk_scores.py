from app.core.database import SessionLocal
from app.services.risk_score_service import (
    calculate_jurisdiction_risk_scores, allocate_risk_score_to_dongs, snapshot_dong_risk_scores,
)

if __name__ == "__main__":
    db = SessionLocal()

    jur_result = calculate_jurisdiction_risk_scores(db)
    print("관할구역 위험 스코어 계산 완료:", jur_result["updated"], "건")

    dong_result = allocate_risk_score_to_dongs(db)
    print(f"관할동 배분 완료 — 갱신: {dong_result['updated']}, 스킵: {dong_result['skipped']}, 기준연월: {dong_result['std_ym']}")

    snapshot_result = snapshot_dong_risk_scores(db)
    print(f"오늘자 스냅샷 저장 — 신규: {snapshot_result['created']}, 스킵(이미 있음): {snapshot_result['skipped']}")
