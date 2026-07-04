# app/models/fire_incident.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.core.database import Base


class FireIncident(Base):
    __tablename__ = "fire_incidents"

    id = Column(Integer, primary_key=True)
    wrinv_no = Column(String(25), unique=True, index=True)   # 조사서번호 (PK 대체키)

    rcpt_dt = Column(String(14))       # 접수일시
    dspt_dt = Column(String(14))       # 출동일시
    grnds_arvl_dt = Column(String(14)) # 현장도착일시
    prfect_potfr_dt = Column(String(14))  # 완전진화일시

    ctpv_nm = Column(String(40))
    sggu_nm = Column(String(40))
    frstn_nm = Column(String(200))     # 소방서명
    cntr_nm = Column(String(100))      # 안전센터명

    fire_type_nm = Column(String(20))       # 화재유형명
    fclt_plc_lclsf_nm = Column(String(20))  # 시설장소대분류명
    igtn_dmnt_lclsf_nm = Column(String(20)) # 발화요인대분류명

    dth_cnt = Column(Numeric(4, 0))     # 사망수
    injpsn_cnt = Column(Numeric(10, 0)) # 부상자수
    prpt_dam_amt = Column(Numeric(22, 2))  # 재산피해금액

    fire_supesn_hr = Column(Numeric(7, 0))  # 화재진압시간(대응시간 지표)
    
    seasn_nm = Column(String(5))           # 계절명
    dow_nm = Column(String(5))             # 요일명 (이미 dclrDow로 EMS에도 있었음)
    hr_unit_artmp = Column(Numeric(8, 3))  # 시간단위기온
    hr_unit_hum = Column(Numeric(8, 3))    # 시간단위습도
    hr_unit_wspd_info = Column(String(1000))  # 시간단위풍속정보

    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)