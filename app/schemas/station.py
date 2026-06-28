from pydantic import BaseModel
from typing import Optional

class StationCreate(BaseModel):
    objt_id: str           # 시설 고유 ID
    fclty_nm: str          # 시설(소방)명
    fclty_ty: str          # 시설(소방)유형
    fclty_cd: str          # 시설(소방)코드
    rn_adres: Optional[str] = None  # 도로명주소
    telno: Optional[str] = None     # 전화번호

    class Config:
        from_attributes = True

class StationResponse(StationCreate):
    id: int

    class Config:
        from_attributes = True

class SafetyCenterResponse(BaseModel):
    id: int
    station_name: str   

    class Config:
        from_attributes = True