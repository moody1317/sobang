from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base

class RiskScoreSnapshot(Base):
    __tablename__ = "risk_score_snapshots"
    __table_args__ = (UniqueConstraint("admin_code", "snapshot_date", name="uq_risk_score_snapshot_dong_date"),)

    id = Column(Integer, primary_key=True)
    admin_code = Column(String(20), nullable=False, index=True)
    sigungu_nm = Column(String(50))
    dong_nm = Column(String(50), nullable=False)
    risk_score = Column(Numeric(5, 2), nullable=False)
    snapshot_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
