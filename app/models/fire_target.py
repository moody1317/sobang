from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class FireTarget(Base):
    __tablename__ = "fire_targets"

    id = Column(Integer, primary_key=True)
    bdst_sn = Column(String(50), unique=True, index=True)  # 건축물일련번호 — upsert 기준키

    trgtobj_nm = Column(String(100))    # 대상물명
    bldg_nm = Column(String(100))       # 건물명
    addr = Column(String(2000))         # 주소

    ctpv_nm = Column(String(40))
    sggu_nm = Column(String(40))
    emd_nm = Column(String(40))

    frstn_nm = Column(String(200))      # 소방서명
    cntr_nm = Column(String(100))       # 안전센터명

    use_yn = Column(String(1))                   # 사용여부
    lgz_fire_wktrgt_yn = Column(String(1))        # 대형화재취약대상여부
    isf_chck_trgt_yn = Column(String(1))          # 자체점검대상여부
    isf_chck_trgt_type_nm = Column(String(20))    # 자체점검대상유형명
    cltpty_yn = Column(String(1))                 # 문화재여부
    pbnst_yn = Column(String(1))                  # 공공기관여부
    arson_mng_trgt_yn = Column(String(1))         # 방화관리대상여부

    fire_insrnc_co_nm = Column(String(40))        # 화재보험회사명
    fire_insrnc_join_ymd = Column(String(8))      # 화재보험가입일자

    use_aprv_ymd = Column(String(8))    # 사용승인일자

    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)