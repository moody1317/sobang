# app/models/ems_incident.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.core.database import Base

class EmsIncident(Base):
    __tablename__ = "ems_incidents"

    id = Column(Integer, primary_key=True)
    rlf_rptp_no = Column(String(30), unique=True, index=True)  # 구급보고서번호

    reg_cmptn_se_nm = Column(String(10))     # 등록완료구분 (진행중/등록완료 등) — 미완료건 필터링용
    dclr_ymd = Column(String(8))
    dspt_ymd = Column(String(8), nullable=True)
    grnds_arvl_ymd = Column(String(8), nullable=True)

    ctpv_nm = Column(String(40))
    sggu_nm = Column(String(40))
    frstn_nm = Column(String(200))
    cntr_nm = Column(String(100))

    ptn_ocrn_type_nm = Column(String(20))      # 환자발생유형명
    ptn_sym_se_nm = Column(String(20))         # 환자증상구분명
    trfc_acdnt_se_nm = Column(String(20))      # 교통사고구분명

    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)