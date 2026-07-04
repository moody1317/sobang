from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.core.database import Base


class RescueIncident(Base):
    __tablename__ = "rescue_incidents"

    id = Column(Integer, primary_key=True)
    clmty_rscu_rptp_no = Column(String(20), unique=True, index=True)  # 재난구조보고서번호

    dclr_ymd = Column(String(8))       # 신고일자
    dclr_tm = Column(String(6))        # 신고시각
    dspt_ymd = Column(String(8))       # 출동일자
    grnds_arvl_ymd = Column(String(8)) # 현장도착일자
    rscu_cmptn_ymd = Column(String(8)) # 구조완료일자

    dclr_pstn_lat = Column(Numeric(12, 10))  # 신고위치 위도
    dclr_pstn_lot = Column(Numeric(13, 10))  # 신고위치 경도

    ctpv_nm = Column(String(40))
    sggu_nm = Column(String(40))
    emd_nm = Column(String(40))        # 읍면동명 — 순찰용 동별 스코어에 바로 쓸 수 있음

    frstn_nm = Column(String(200))     # 소방서명
    cntr_nm = Column(String(100))      # 안전센터명

    acdnt_cs_nm = Column(String(20))       # 사고원인명
    acdnt_plc_dtl_nm = Column(String(40))  # 사고장소세부명
    prcs_rslt_se_nm = Column(String(20))   # 처리결과구분명

    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)